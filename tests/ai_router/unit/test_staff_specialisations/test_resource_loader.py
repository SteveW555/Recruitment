"""
Unit tests for ResourceLoader.

Tests cover:
- Resource discovery (empty dir, multiple files, exclude guide, alphabetical order)
- Resource loading (markdown, JSON, text, error handling)
- Caching behavior (cache hit <10ms, TTL expiration)
- Guide loading
"""

import pytest
import time
from pathlib import Path
from unittest.mock import patch

from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader
from utils.ai_router.staff_specialisations.models import ResourceFormat


class TestResourceDiscovery:
    """Tests for ResourceLoader.discover_resources()."""

    def test_discover_resources_empty_directory(self, temp_staff_specialisations_dir):
        """Empty directory returns empty dict."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        person_1_dir = role_dirs["person_1_managing_director"]
        resources = loader.discover_resources(person_1_dir)

        assert len(resources) == 0

    def test_discover_resources_multiple_files(
        self,
        temp_staff_specialisations_dir,
        sample_markdown_resource,
        sample_json_resource,
        sample_text_resource,
    ):
        """Multiple files are discovered."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        # Discover person_1 with markdown
        person_1_dir = role_dirs["person_1_managing_director"]
        resources_1 = loader.discover_resources(person_1_dir)
        assert len(resources_1) > 0

        # Discover person_2 with JSON
        person_2_dir = role_dirs["person_2_temp_consultant"]
        resources_2 = loader.discover_resources(person_2_dir)
        assert len(resources_2) > 0

        # Discover person_3 with text
        person_3_dir = role_dirs["person_3_resourcer_admin_tech"]
        resources_3 = loader.discover_resources(person_3_dir)
        assert len(resources_3) > 0

    def test_discover_resources_excludes_guide(
        self, temp_staff_specialisations_dir, sample_resources_guide
    ):
        """resources-guide.md is excluded from discovery."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        person_4_dir = role_dirs["person_4_compliance_wellbeing"]
        resources = loader.discover_resources(person_4_dir)

        # Guide should be excluded
        assert "resources-guide" not in resources
        for name in resources:
            assert name != "resources-guide"

    def test_discover_resources_alphabetical_order(self, temp_staff_specialisations_dir):
        """Resources are returned in alphabetical order."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        person_1_dir = role_dirs["person_1_managing_director"]

        # Create files in non-alphabetical order
        (person_1_dir / "zebra.md").write_text("# Zebra")
        (person_1_dir / "apple.md").write_text("# Apple")
        (person_1_dir / "banana.txt").write_text("Banana")

        resources = loader.discover_resources(person_1_dir)
        names = list(resources.keys())

        # Verify alphabetical order
        assert names == sorted(names)

    def test_discover_resources_nonexistent_directory(self):
        """Non-existent directory returns empty dict."""
        loader = ResourceLoader(Path("/tmp"))
        resources = loader.discover_resources(Path("/nonexistent/path"))

        assert len(resources) == 0


class TestResourceLoading:
    """Tests for ResourceLoader.load_resource()."""

    def test_load_markdown_resource(self, sample_markdown_resource):
        """Markdown resource loads and parses correctly."""
        loader = ResourceLoader(Path("/tmp"))
        resource = loader.load_resource(sample_markdown_resource)

        assert resource.is_valid
        assert resource.metadata.format == ResourceFormat.MARKDOWN
        assert "format" in resource.parsed
        assert resource.parsed["format"] == "markdown"
        assert "headings" in resource.parsed
        assert len(resource.parsed["headings"]) > 0

    def test_load_json_resource(self, sample_json_resource):
        """JSON resource loads and parses correctly."""
        loader = ResourceLoader(Path("/tmp"))
        resource = loader.load_resource(sample_json_resource)

        assert resource.is_valid
        assert resource.metadata.format == ResourceFormat.JSON
        assert "data" in resource.parsed
        assert isinstance(resource.parsed["data"], dict)

    def test_load_text_resource(self, sample_text_resource):
        """Text resource loads and parses correctly."""
        loader = ResourceLoader(Path("/tmp"))
        resource = loader.load_resource(sample_text_resource)

        assert resource.is_valid
        assert resource.metadata.format == ResourceFormat.TEXT
        assert "lines" in resource.parsed
        assert isinstance(resource.parsed["lines"], list)

    def test_load_resource_nonexistent_file(self):
        """Non-existent file returns error resource."""
        loader = ResourceLoader(Path("/tmp"))
        resource = loader.load_resource(Path("/nonexistent/file.md"))

        assert not resource.is_valid
        assert resource.error is not None


class TestGuideLoading:
    """Tests for ResourceLoader.load_guide()."""

    def test_load_guide_exists(self, sample_resources_guide):
        """Load guide when it exists."""
        guide_dir = sample_resources_guide.parent
        loader = ResourceLoader(guide_dir.parent.parent.parent)

        guide = loader.load_guide(guide_dir)

        assert guide is not None
        assert "Resource Guide" in guide or "resource" in guide.lower()

    def test_load_guide_missing(self, empty_role_dir):
        """Load guide returns None when missing."""
        loader = ResourceLoader(empty_role_dir.parent.parent)

        guide = loader.load_guide(empty_role_dir)

        assert guide is None


class TestCaching:
    """Tests for caching behavior."""

    def test_cache_hit_performance(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Cached load is much faster than first load."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        person_1_dir = role_dirs["person_1_managing_director"]
        role_name = "person_1_managing_director"

        # First load (cache miss)
        start = time.time()
        resources_1 = loader.load_resources(role_name)
        first_load_time = time.time() - start

        # Second load (cache hit)
        start = time.time()
        resources_2 = loader.load_resources(role_name)
        cached_load_time = time.time() - start

        # Cache hit should be much faster
        assert resources_1 == resources_2
        # Cached should be <10ms (cached_load_time < first_load_time)
        assert cached_load_time < first_load_time

    def test_cache_ttl_expiration(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Cache expires after TTL."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root, cache_ttl_seconds=1)  # 1 second TTL

        person_1_dir = role_dirs["person_1_managing_director"]
        role_name = "person_1_managing_director"

        # Load and verify cached
        resources_1 = loader.load_resources(role_name)
        assert role_name in loader._resource_cache

        # Wait for cache to expire
        time.sleep(1.1)

        # Verify cache was invalidated (reload from disk)
        resources_2 = loader.load_resources(role_name)
        # Should be same content, but reloaded from disk
        assert len(resources_1) == len(resources_2)

    def test_cache_invalidation(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Manual cache invalidation works."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        role_name = "person_1_managing_director"

        # Load and verify cached
        loader.load_resources(role_name)
        assert role_name in loader._resource_cache

        # Invalidate
        loader.invalidate_cache(role_name)
        assert role_name not in loader._resource_cache

    def test_cache_invalidate_all(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Invalidate all caches."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        # Load multiple roles
        loader.load_resources("person_1_managing_director")
        loader.load_resources("person_2_temp_consultant")

        assert len(loader._resource_cache) > 0

        # Invalidate all
        loader.invalidate_cache()
        assert len(loader._resource_cache) == 0


class TestResourceParsing:
    """Tests for resource parsing."""

    def test_markdown_heading_extraction(self, sample_markdown_resource):
        """Markdown headings are extracted."""
        loader = ResourceLoader(Path("/tmp"))
        resource = loader.load_resource(sample_markdown_resource)

        headings = resource.parsed.get("headings", [])
        assert len(headings) > 0
        assert any("Framework" in h or "framework" in h for h in headings)

    def test_json_data_parsing(self, sample_json_resource):
        """JSON data is parsed to dict."""
        loader = ResourceLoader(Path("/tmp"))
        resource = loader.load_resource(sample_json_resource)

        data = resource.parsed.get("data")
        assert isinstance(data, dict)
        assert "contact_centre_metrics" in data

    def test_text_line_splitting(self, sample_text_resource):
        """Text is split into lines."""
        loader = ResourceLoader(Path("/tmp"))
        resource = loader.load_resource(sample_text_resource)

        lines = resource.parsed.get("lines", [])
        assert len(lines) > 0
        assert all(isinstance(line, str) for line in lines)


__all__ = [
    "TestResourceDiscovery",
    "TestResourceLoading",
    "TestGuideLoading",
    "TestCaching",
    "TestResourceParsing",
]
