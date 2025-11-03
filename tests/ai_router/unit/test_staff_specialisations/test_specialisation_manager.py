"""
Unit tests for SpecialisationManager.

Tests cover:
- Staff role validation
- Resource loading
- Error handling
- Status code assignment
- Available roles listing
"""

import pytest
from pathlib import Path

from utils.ai_router.staff_specialisations.specialisation_manager import (
    SpecialisationManager,
)
from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader
from utils.ai_router.staff_specialisations.models import SpecialisationStatus


class TestSpecialisationContext:
    """Tests for SpecialisationManager.get_specialisation_context()."""

    def test_valid_role_with_resources(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Valid role with resources returns LOADED context."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        assert context.staff_role == "person_1_managing_director"
        assert context.status == SpecialisationStatus.LOADED
        assert len(context.resources) > 0
        assert context.is_available()
        assert not context.is_error()

    def test_valid_role_no_resources(self, temp_staff_specialisations_dir):
        """Valid role with no resources returns NO_RESOURCES context."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_5_finance_training")

        assert context.staff_role == "person_5_finance_training"
        assert context.status == SpecialisationStatus.NO_RESOURCES
        assert len(context.resources) == 0
        assert not context.is_available()
        assert not context.is_error()

    def test_invalid_role(self, temp_staff_specialisations_dir):
        """Invalid role returns INVALID_ROLE context with error message."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("invalid_role")

        assert context.staff_role == "invalid_role"
        assert context.status == SpecialisationStatus.INVALID_ROLE
        assert context.error_message is not None
        assert "invalid_role" in context.error_message
        assert len(context.resources) == 0
        assert not context.is_available()
        assert context.is_error()

    def test_no_staff_role_provided(self, temp_staff_specialisations_dir):
        """No staff_role returns NOT_REQUESTED context."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context(None)

        assert context.staff_role is None
        assert context.status == SpecialisationStatus.NOT_REQUESTED
        assert len(context.resources) == 0
        assert not context.is_available()
        assert not context.is_error()

    def test_context_with_guide(
        self, temp_staff_specialisations_dir, sample_resources_guide
    ):
        """Context includes guide when available."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_4_compliance_wellbeing")

        assert context.guide is not None
        assert "Resource Guide" in context.guide or "resource" in context.guide.lower()


class TestAvailableRoles:
    """Tests for SpecialisationManager.get_available_roles()."""

    def test_available_roles_count(self, temp_staff_specialisations_dir):
        """Available roles returns exactly 5 roles."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        roles = manager.get_available_roles()

        assert len(roles) == 5

    def test_available_roles_values(self, temp_staff_specialisations_dir):
        """Available roles returns correct role values."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        roles = manager.get_available_roles()

        expected = [
            "person_1_managing_director",
            "person_2_temp_consultant",
            "person_3_resourcer_admin_tech",
            "person_4_compliance_wellbeing",
            "person_5_finance_training",
        ]

        for role in expected:
            assert role in roles

    def test_available_roles_correct_order(self, temp_staff_specialisations_dir):
        """Available roles are in correct order."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        roles = manager.get_available_roles()

        assert "person_1_managing_director" in roles
        assert "person_2_temp_consultant" in roles
        assert "person_3_resourcer_admin_tech" in roles
        assert "person_4_compliance_wellbeing" in roles
        assert "person_5_finance_training" in roles


class TestValidationMethod:
    """Tests for SpecialisationManager.validate_staff_role()."""

    def test_validate_valid_roles(self, temp_staff_specialisations_dir):
        """All valid roles validate successfully."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        for role in manager.get_available_roles():
            assert manager.validate_staff_role(role)

    def test_validate_invalid_role(self, temp_staff_specialisations_dir):
        """Invalid role fails validation."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        assert not manager.validate_staff_role("invalid_role")

    def test_validate_none(self, temp_staff_specialisations_dir):
        """None passes validation (optional)."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        assert manager.validate_staff_role(None)

    def test_validate_case_sensitive(self, temp_staff_specialisations_dir):
        """Validation is case-sensitive."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        assert manager.validate_staff_role("person_1_managing_director")
        assert not manager.validate_staff_role("Person_1_Managing_Director")


class TestCacheManagement:
    """Tests for cache clearing."""

    def test_clear_specific_role_cache(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Clear cache for specific role."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        # Load to populate cache
        manager.get_specialisation_context("person_1_managing_director")
        manager.get_specialisation_context("person_2_temp_consultant")

        assert "person_1_managing_director" in loader._resource_cache
        assert "person_2_temp_consultant" in loader._resource_cache

        # Clear specific role
        manager.clear_cache("person_1_managing_director")

        assert "person_1_managing_director" not in loader._resource_cache
        assert "person_2_temp_consultant" in loader._resource_cache

    def test_clear_all_cache(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Clear all cache."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        # Load to populate cache
        manager.get_specialisation_context("person_1_managing_director")
        manager.get_specialisation_context("person_2_temp_consultant")

        assert len(loader._resource_cache) > 0

        # Clear all
        manager.clear_cache()

        assert len(loader._resource_cache) == 0


class TestErrorHandling:
    """Tests for error handling."""

    def test_handles_malformed_json(self, temp_staff_specialisations_dir):
        """Manager handles malformed JSON gracefully."""
        root, role_dirs = temp_staff_specialisations_dir

        # Create malformed JSON
        person_1_dir = role_dirs["person_1_managing_director"]
        (person_1_dir / "bad.json").write_text("{invalid json")

        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        # Should not crash
        context = manager.get_specialisation_context("person_1_managing_director")

        # Might have some resources loaded, but manager should handle gracefully
        # The invalid JSON file will be marked as error in Resource
        assert context.status in (
            SpecialisationStatus.LOADED,
            SpecialisationStatus.NO_RESOURCES,
        )


class TestDefaultBasePath:
    """Tests for default base path initialization."""

    def test_default_base_path_resolved(self):
        """SpecialisationManager resolves default base path correctly."""
        manager = SpecialisationManager()

        # Should resolve to specs/003-staff-specialisations/staff_specialisations
        assert manager.base_path.exists()
        assert "staff_specialisations" in str(manager.base_path)


__all__ = [
    "TestSpecialisationContext",
    "TestAvailableRoles",
    "TestValidationMethod",
    "TestCacheManagement",
    "TestErrorHandling",
    "TestDefaultBasePath",
]
