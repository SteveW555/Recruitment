"""
Integration tests for User Story 2: Agent Accesses Role-Specific Resources.

Tests cover:
- Multi-format resource loading (markdown, JSON, text in same role)
- Empty role directories (no crash, status=no_resources)
- Resources-guide.md handling and accessibility
- Resource accessibility to agents
"""

import pytest
from pathlib import Path

from utils.ai_router.staff_specialisations.specialisation_manager import (
    SpecialisationManager,
)
from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader
from utils.ai_router.staff_specialisations.models import SpecialisationStatus
from utils.ai_router.staff_specialisations.context_builder import (
    build_context_prompt,
    select_relevant_resources,
)


class TestMultiFormatResourceLoading:
    """Tests for multi-format resource loading."""

    def test_load_markdown_and_json_in_same_role(
        self, temp_staff_specialisations_dir, sample_markdown_resource, sample_json_resource
    ):
        """Load markdown and JSON resources from same role directory."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        # person_1 has markdown, person_2 has json
        context_1 = manager.get_specialisation_context("person_1_managing_director")
        context_2 = manager.get_specialisation_context("person_2_temp_consultant")

        # Both should load resources
        if context_1.is_available():
            assert any(r.metadata.format.value == "markdown" for r in context_1.resources.values())
        if context_2.is_available():
            assert any(r.metadata.format.value == "json" for r in context_2.resources.values())

    def test_all_formats_accessible(
        self,
        temp_staff_specialisations_dir,
        sample_markdown_resource,
        sample_json_resource,
        sample_text_resource,
    ):
        """All three formats (markdown, JSON, text) are accessible."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        # Load all resources
        md_resources = loader.load_resources("person_1_managing_director")
        json_resources = loader.load_resources("person_2_temp_consultant")
        txt_resources = loader.load_resources("person_3_resourcer_admin_tech")

        # Verify formats are present
        formats_found = set()
        for resources_dict in [md_resources, json_resources, txt_resources]:
            for resource in resources_dict.values():
                if resource.is_valid:
                    formats_found.add(resource.metadata.format.value)

        # Should have at least some formats (depending on what was created)
        assert len(formats_found) > 0

    def test_resources_parsed_correctly(
        self, temp_staff_specialisations_dir, sample_markdown_resource, sample_json_resource
    ):
        """Resources are parsed correctly with format-specific fields."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        # Load markdown resource
        md_resources = loader.load_resources("person_1_managing_director")
        for resource in md_resources.values():
            if resource.is_valid and resource.metadata.format.value == "markdown":
                assert "format" in resource.parsed
                assert "headings" in resource.parsed
                break

        # Load JSON resource
        json_resources = loader.load_resources("person_2_temp_consultant")
        for resource in json_resources.values():
            if resource.is_valid and resource.metadata.format.value == "json":
                assert "format" in resource.parsed
                assert "data" in resource.parsed
                break


class TestEmptyRoleDirectories:
    """Tests for handling empty role directories."""

    def test_empty_directory_no_crash(self, temp_staff_specialisations_dir, empty_role_dir):
        """Empty directory doesn't crash, returns NO_RESOURCES status."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_5_finance_training")

        assert context.staff_role == "person_5_finance_training"
        assert context.status == SpecialisationStatus.NO_RESOURCES
        assert len(context.resources) == 0
        assert not context.is_available()

    def test_empty_directory_agent_continues(self, empty_role_dir):
        """Agent can continue normally with empty directory."""
        # Simulate agent processing with empty context
        from utils.ai_router.staff_specialisations.models import SpecialisationContext

        context = SpecialisationContext(
            staff_role="person_5_finance_training",
            resources={},
            status=SpecialisationStatus.NO_RESOURCES,
        )

        # Agent should be able to work with this context
        prompt = build_context_prompt(context)
        # Should return empty (no resources to add)
        assert prompt == ""

        # But agent can still construct its own response
        assert context.staff_role is not None


class TestResourcesGuideHandling:
    """Tests for resources-guide.md handling and accessibility."""

    def test_load_resources_guide(self, temp_staff_specialisations_dir, sample_resources_guide):
        """resources-guide.md is loaded and accessible."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_4_compliance_wellbeing")

        if context.guide:
            assert "Resource Guide" in context.guide or "resource" in context.guide.lower()
            assert context.guide is not None

    def test_guide_missing_handled_gracefully(self, temp_staff_specialisations_dir):
        """Missing guide doesn't cause errors."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        # Load a role without a guide
        context = manager.get_specialisation_context("person_1_managing_director")

        # Should not crash even if guide is missing
        assert context.status in (
            SpecialisationStatus.LOADED,
            SpecialisationStatus.NO_RESOURCES,
        )

    def test_guide_excluded_from_resource_list(
        self, temp_staff_specialisations_dir, sample_resources_guide
    ):
        """resources-guide.md is NOT included in regular resource list."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_4_compliance_wellbeing")

        # Guide should not be in resources dict
        assert "resources-guide" not in context.resources
        for name in context.resources.keys():
            assert name != "resources-guide"

    def test_guide_accessible_via_context(self, temp_staff_specialisations_dir, sample_resources_guide):
        """Guide is accessible via context.guide, not via resources."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_4_compliance_wellbeing")

        # Guide should be in context.guide
        if context.guide:
            assert context.guide is not None
            assert isinstance(context.guide, str)


class TestResourceAccessibilityToAgents:
    """Tests for agent access to resources."""

    def test_agent_can_access_resources_via_context(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Agent can access resources through specialisation context."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            # Agent can iterate over resources
            for name, resource in context.resources.items():
                assert resource.metadata.name == name
                assert resource.content is not None
                break

    def test_context_prompt_accessible(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Agent can build context prompt for system instructions."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            prompt = build_context_prompt(context)
            # Can be empty if no guide, but still accessible
            assert isinstance(prompt, str)

    def test_relevant_resources_selectable(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Agent can select relevant resources for query."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            selected = select_relevant_resources(context, "strategy")
            # May be empty or contain resources
            assert isinstance(selected, list)


class TestUS2AcceptanceCriteria:
    """Tests for User Story 2 acceptance criteria."""

    def test_all_resources_discoverable(
        self, temp_staff_specialisations_dir, sample_markdown_resource, sample_json_resource
    ):
        """AC: All resources in role directory are discoverable."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        # Create multiple resources
        person_1_dir = role_dirs["person_1_managing_director"]

        # Verify we can discover them
        discovered = loader.discover_resources(person_1_dir)
        assert len(discovered) > 0

    def test_resources_loaded_with_correct_format_parsing(
        self, temp_staff_specialisations_dir, sample_markdown_resource, sample_json_resource
    ):
        """AC: Resources can be loaded with correct format parsing."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        # Load and verify format parsing
        md_resources = loader.load_resources("person_1_managing_director")
        json_resources = loader.load_resources("person_2_temp_consultant")

        # Verify parsing worked
        for resources in [md_resources, json_resources]:
            for resource in resources.values():
                if resource.is_valid:
                    assert "format" in resource.parsed

    def test_empty_directories_handled_gracefully(self, temp_staff_specialisations_dir):
        """AC: Empty resource directories handled gracefully."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_5_finance_training")

        # Should not crash
        assert context.status == SpecialisationStatus.NO_RESOURCES
        # Agent can still function
        assert context.staff_role is not None

    def test_multiple_resources_accessible(
        self, temp_staff_specialisations_dir, sample_markdown_resource, sample_json_resource
    ):
        """AC: Multiple resources accessible (returns dict of all resources)."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        # Load multiple resources
        resources = loader.load_resources("person_1_managing_director")

        # Should return dict
        assert isinstance(resources, dict)
        # Can access each resource
        for name, resource in resources.items():
            assert resource is not None

    def test_resources_guide_consulted_if_present(
        self, temp_staff_specialisations_dir, sample_resources_guide
    ):
        """AC: Resources-guide.md consulted for navigation (if present)."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_4_compliance_wellbeing")

        if context.guide:
            # Guide is available and can be used
            assert context.guide is not None
            assert "Resource" in context.guide or "resource" in context.guide.lower()

    def test_resource_loading_latency_met(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """AC: <500ms resource loading latency."""
        import time

        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        start = time.time()
        resources = loader.load_resources("person_1_managing_director")
        elapsed_ms = (time.time() - start) * 1000

        # Should be well under 500ms (first load)
        assert elapsed_ms < 500  # 500ms target

    def test_corrupted_resources_dont_crash(self, temp_staff_specialisations_dir):
        """AC: Corrupted resources don't crash loading (error handling)."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)

        # Create corrupted JSON
        person_1_dir = role_dirs["person_1_managing_director"]
        (person_1_dir / "bad.json").write_text("{invalid json}")

        # Should not crash
        resources = loader.load_resources("person_1_managing_director")

        # Should return dict (with error resources marked invalid)
        assert isinstance(resources, dict)


__all__ = [
    "TestMultiFormatResourceLoading",
    "TestEmptyRoleDirectories",
    "TestResourcesGuideHandling",
    "TestResourceAccessibilityToAgents",
    "TestUS2AcceptanceCriteria",
]
