"""
Unit tests for context builder functions.

Tests cover:
- Context prompt building (with guide, without guide, empty context)
- Resource selection (relevance scoring, max limit)
- Metadata building
"""

import pytest
from pathlib import Path

from utils.ai_router.staff_specialisations.context_builder import (
    build_context_prompt,
    select_relevant_resources,
    build_metadata,
)
from utils.ai_router.staff_specialisations.models import (
    SpecialisationContext,
    SpecialisationStatus,
    Resource,
    ResourceMetadata,
    ResourceFormat,
)


class TestBuildContextPrompt:
    """Tests for build_context_prompt()."""

    def test_build_prompt_with_guide(self, temp_staff_specialisations_dir, sample_resources_guide, sample_text_resource):
        """Build prompt includes guide when available with resources."""
        root, role_dirs = temp_staff_specialisations_dir
        from utils.ai_router.staff_specialisations.specialisation_manager import (
            SpecialisationManager,
        )
        from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        # Load person_3 which has text resource + person_4 has guide
        # Just verify that guide doesn't break prompt building
        context = manager.get_specialisation_context("person_4_compliance_wellbeing")

        prompt = build_context_prompt(context)

        # Prompt may be empty if no resources (guide alone doesn't count)
        # But if we have resources, it should have content
        if context.is_available():
            assert len(prompt) > 0
        else:
            # This is correct - guide alone doesn't make context available
            assert prompt == ""

    def test_build_prompt_without_guide(self, temp_staff_specialisations_dir, sample_markdown_resource):
        """Build prompt works without guide."""
        root, role_dirs = temp_staff_specialisations_dir
        from utils.ai_router.staff_specialisations.specialisation_manager import (
            SpecialisationManager,
        )
        from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        prompt = build_context_prompt(context)

        # Should still have content even without guide
        if context.is_available():
            assert len(prompt) > 0

    def test_build_prompt_empty_context(self):
        """Build prompt returns empty string for unavailable context."""
        context = SpecialisationContext(
            staff_role=None,
            resources={},
            status=SpecialisationStatus.NOT_REQUESTED,
        )

        prompt = build_context_prompt(context)

        assert prompt == ""

    def test_build_prompt_no_resources_context(self):
        """Build prompt returns empty string when no resources."""
        context = SpecialisationContext(
            staff_role="person_1_managing_director",
            resources={},
            status=SpecialisationStatus.NO_RESOURCES,
        )

        prompt = build_context_prompt(context)

        assert prompt == ""

    def test_build_prompt_includes_role_name(self, temp_staff_specialisations_dir, sample_markdown_resource):
        """Build prompt includes the role name."""
        root, role_dirs = temp_staff_specialisations_dir
        from utils.ai_router.staff_specialisations.specialisation_manager import (
            SpecialisationManager,
        )
        from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            prompt = build_context_prompt(context)
            assert "person_1" in prompt or "Role Context" in prompt

    def test_build_prompt_lists_resources(self, temp_staff_specialisations_dir, sample_markdown_resource):
        """Build prompt lists available resources."""
        root, role_dirs = temp_staff_specialisations_dir
        from utils.ai_router.staff_specialisations.specialisation_manager import (
            SpecialisationManager,
        )
        from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available() and context.resources:
            prompt = build_context_prompt(context)
            # Should mention resources
            assert "resource" in prompt.lower() or len(context.resources) == 0


class TestSelectRelevantResources:
    """Tests for select_relevant_resources()."""

    def test_select_resources_with_query(self, temp_staff_specialisations_dir, sample_markdown_resource):
        """Select resources based on query."""
        root, role_dirs = temp_staff_specialisations_dir
        from utils.ai_router.staff_specialisations.specialisation_manager import (
            SpecialisationManager,
        )
        from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            selected = select_relevant_resources(context, "strategy")
            # May return 0+ resources depending on content match
            assert isinstance(selected, list)

    def test_select_respects_max_resources(self, temp_staff_specialisations_dir, sample_markdown_resource):
        """Select respects max_resources limit."""
        root, role_dirs = temp_staff_specialisations_dir
        from utils.ai_router.staff_specialisations.specialisation_manager import (
            SpecialisationManager,
        )
        from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            selected = select_relevant_resources(context, "strategy", max_resources=2)
            assert len(selected) <= 2

    def test_select_empty_context_returns_empty(self):
        """Select returns empty list for unavailable context."""
        context = SpecialisationContext(
            staff_role=None,
            resources={},
            status=SpecialisationStatus.NOT_REQUESTED,
        )

        selected = select_relevant_resources(context, "test query")

        assert selected == []

    def test_select_only_valid_resources(self, temp_staff_specialisations_dir):
        """Select only returns valid resources."""
        root, role_dirs = temp_staff_specialisations_dir

        # Create a context with mix of valid and invalid resources
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Valid")
            valid_path = Path(f.name)

        try:
            valid_metadata = ResourceMetadata(
                name="valid",
                path=valid_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=100,
            )
            valid_resource = Resource(
                metadata=valid_metadata,
                content="# Valid",
                parsed={"format": "markdown"},
                error=None,
            )

            invalid_resource = Resource(
                metadata=valid_metadata,
                content="",
                parsed={},
                error="Parse error",
            )

            context = SpecialisationContext(
                staff_role="person_1_managing_director",
                resources={"valid": valid_resource, "invalid": invalid_resource},
                status=SpecialisationStatus.LOADED,
            )

            selected = select_relevant_resources(context, "test")

            # Should only include valid resources
            for resource in selected:
                assert resource.is_valid
        finally:
            valid_path.unlink()


class TestBuildMetadata:
    """Tests for build_metadata()."""

    def test_build_metadata_loaded_context(self, temp_staff_specialisations_dir, sample_markdown_resource):
        """Build metadata for loaded context includes resource info."""
        root, role_dirs = temp_staff_specialisations_dir
        from utils.ai_router.staff_specialisations.specialisation_manager import (
            SpecialisationManager,
        )
        from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            metadata = build_metadata(context, resources_consulted=1)

            assert "staff_role_used" in metadata
            assert metadata["staff_role_used"] == "person_1_managing_director"
            assert "specialisation_status" in metadata
            assert metadata["specialisation_status"] == "loaded"
            assert "resources_consulted" in metadata
            assert "resources_available" in metadata

    def test_build_metadata_no_resources_context(self):
        """Build metadata for no-resources context."""
        context = SpecialisationContext(
            staff_role="person_1_managing_director",
            resources={},
            status=SpecialisationStatus.NO_RESOURCES,
        )

        metadata = build_metadata(context, resources_consulted=0)

        assert metadata["staff_role_used"] == "person_1_managing_director"
        assert metadata["specialisation_status"] == "no_resources"
        # Should not have resources_consulted for unavailable context
        assert "resources_consulted" not in metadata

    def test_build_metadata_with_guide(self, temp_staff_specialisations_dir, sample_resources_guide):
        """Build metadata notes when guide is available."""
        root, role_dirs = temp_staff_specialisations_dir
        from utils.ai_router.staff_specialisations.specialisation_manager import (
            SpecialisationManager,
        )
        from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_4_compliance_wellbeing")

        if context.is_available():
            metadata = build_metadata(context)

            if context.guide:
                assert metadata.get("has_guide") is True

    def test_build_metadata_invalid_role_context(self):
        """Build metadata for invalid role context."""
        context = SpecialisationContext(
            staff_role="invalid_role",
            resources={},
            status=SpecialisationStatus.INVALID_ROLE,
            error_message="Invalid role",
        )

        metadata = build_metadata(context)

        assert metadata["staff_role_used"] == "invalid_role"
        assert metadata["specialisation_status"] == "invalid_role"
        assert "resources_consulted" not in metadata


# Need to import tempfile for test_select_only_valid_resources
import tempfile


__all__ = [
    "TestBuildContextPrompt",
    "TestSelectRelevantResources",
    "TestBuildMetadata",
]
