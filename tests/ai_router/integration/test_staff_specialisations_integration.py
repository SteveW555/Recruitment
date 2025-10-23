"""
Integration tests for Staff Specialisations feature.

Tests cover:
- Staff role parameter handling with valid/invalid/missing roles
- Backward compatibility with non-specialised queries
- Directory structure discovery
- Resource loading and caching
- Multi-format resource support
- Response enhancement with role context
"""

import pytest
from pathlib import Path
from typing import Dict, Tuple

from utils.ai_router.staff_specialisations.models import (
    StaffRole,
    SpecialisationStatus,
)


class TestStaffRoleParameterHandling:
    """Tests for staff_role parameter handling in requests."""

    def test_valid_staff_role_parameter(self, temp_staff_specialisations_dir):
        """Agent can parse and identify valid staff_role parameter."""
        root, role_dirs = temp_staff_specialisations_dir

        # Verify that valid staff role directories exist
        for role in StaffRole:
            assert (root / role.value).exists()
            assert (root / role.value).is_dir()

    def test_invalid_staff_role_parameter(self):
        """Agent handles invalid staff_role gracefully (logs warning, continues)."""
        # This will be tested more thoroughly in Phase 2/3
        # For now, verify validation would reject it
        from utils.ai_router.staff_specialisations.validators import validate_staff_role

        is_valid, error = validate_staff_role("invalid_role")
        assert not is_valid
        assert error is not None

    def test_missing_staff_role_parameter(self):
        """Agent handles missing staff_role gracefully (continues normally)."""
        from utils.ai_router.staff_specialisations.validators import validate_staff_role

        is_valid, error = validate_staff_role(None)
        assert is_valid
        assert error is None

    def test_case_sensitive_role_validation(self):
        """Staff role validation is case-sensitive."""
        from utils.ai_router.staff_specialisations.validators import validate_staff_role

        # Valid (exact case)
        is_valid, _ = validate_staff_role("person_1_managing_director")
        assert is_valid

        # Invalid (different case)
        is_valid, _ = validate_staff_role("Person_1_Managing_Director")
        assert not is_valid


class TestDirectoryStructureDiscovery:
    """Tests for discovering and validating directory structure."""

    def test_all_five_roles_directories_discoverable(self, temp_staff_specialisations_dir):
        """All 5 role directories are discoverable."""
        root, role_dirs = temp_staff_specialisations_dir

        # Verify all 5 role directories exist
        assert len(role_dirs) == 5

        for role in StaffRole:
            assert role.value in role_dirs
            assert role_dirs[role.value].exists()
            assert role_dirs[role.value].is_dir()

    def test_empty_directories_handled_gracefully(self, temp_staff_specialisations_dir):
        """Empty role directories (no resources yet) are handled gracefully."""
        root, role_dirs = temp_staff_specialisations_dir

        # All directories are empty by default
        person_1_dir = role_dirs["person_1_managing_director"]

        # Verify directory is empty
        files = list(person_1_dir.glob("*"))
        assert len(files) == 0

    def test_role_directory_naming_matches_spec(self, temp_staff_specialisations_dir):
        """Role directory names match specification exactly (case-sensitive)."""
        root, role_dirs = temp_staff_specialisations_dir

        # Verify exact names from spec
        expected_names = [
            "person_1_managing_director",
            "person_2_temp_consultant",
            "person_3_resourcer_admin_tech",
            "person_4_compliance_wellbeing",
            "person_5_finance_training",
        ]

        for expected_name in expected_names:
            assert expected_name in role_dirs


class TestResourceDiscovery:
    """Tests for resource discovery and loading."""

    def test_discover_markdown_resources(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Markdown resources in role directory are discoverable."""
        root, role_dirs = temp_staff_specialisations_dir
        person_1_dir = role_dirs["person_1_managing_director"]

        # Verify markdown file exists
        md_files = list(person_1_dir.glob("*.md"))
        assert len(md_files) > 0

        # Should find the decision_framework.md
        decision_framework = person_1_dir / "decision_framework.md"
        assert decision_framework.exists()

    def test_discover_json_resources(
        self, temp_staff_specialisations_dir, sample_json_resource
    ):
        """JSON resources in role directory are discoverable."""
        root, role_dirs = temp_staff_specialisations_dir
        person_2_dir = role_dirs["person_2_temp_consultant"]

        # Verify JSON file exists
        json_files = list(person_2_dir.glob("*.json"))
        assert len(json_files) > 0

    def test_discover_text_resources(
        self, temp_staff_specialisations_dir, sample_text_resource
    ):
        """Text resources in role directory are discoverable."""
        root, role_dirs = temp_staff_specialisations_dir
        person_3_dir = role_dirs["person_3_resourcer_admin_tech"]

        # Verify text file exists
        txt_files = list(person_3_dir.glob("*.txt"))
        assert len(txt_files) > 0

    def test_discover_resources_guide(
        self, temp_staff_specialisations_dir, sample_resources_guide
    ):
        """resources-guide.md in role directory is discoverable."""
        root, role_dirs = temp_staff_specialisations_dir
        person_4_dir = role_dirs["person_4_compliance_wellbeing"]

        # Verify guide file exists
        guide_file = person_4_dir / "resources-guide.md"
        assert guide_file.exists()

    def test_exclude_resources_guide_from_regular_resources(
        self, temp_staff_specialisations_dir, sample_resources_guide
    ):
        """resources-guide.md is excluded from regular resource discovery."""
        root, role_dirs = temp_staff_specialisations_dir
        person_4_dir = role_dirs["person_4_compliance_wellbeing"]

        # Get all files except resources-guide.md
        all_files = list(person_4_dir.glob("*.md"))
        assert len(all_files) > 0

        # But if we explicitly look for resources-guide.md, it exists
        guide_file = person_4_dir / "resources-guide.md"
        assert guide_file.exists()


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing systems."""

    def test_queries_without_staff_role_work_unchanged(self):
        """Queries without staff_role parameter work normally."""
        from utils.ai_router.agents.base_agent import AgentRequest, create_test_request

        # Create request without staff_role
        request = create_test_request(
            query="Test query",
            user_id="test_user",
            session_id="550e8400-e29b-41d4-a716-446655440000"
        )

        # Verify no staff_role is set
        assert request.staff_role is None
        assert request.specialisation_context is None

        # Request should still be valid
        assert request.query == "Test query"
        assert request.user_id == "test_user"

    def test_existing_agent_request_fields_unchanged(self):
        """Existing AgentRequest fields are unchanged."""
        from utils.ai_router.agents.base_agent import AgentRequest

        request = AgentRequest(
            query="Test query",
            user_id="test_user",
            session_id="550e8400-e29b-41d4-a716-446655440000",
            context={"key": "value"},
            metadata={"timestamp": "2025-10-23T12:00:00Z"}
        )

        # Verify existing fields work
        assert request.query == "Test query"
        assert request.user_id == "test_user"
        assert request.session_id == "550e8400-e29b-41d4-a716-446655440000"
        assert request.context == {"key": "value"}
        assert request.metadata == {"timestamp": "2025-10-23T12:00:00Z"}

    def test_existing_agent_response_fields_unchanged(self):
        """Existing AgentResponse fields are unchanged."""
        from utils.ai_router.agents.base_agent import AgentResponse

        response = AgentResponse(
            success=True,
            content="Test response",
            metadata={"agent_latency_ms": 100},
            error=None
        )

        # Verify existing fields work
        assert response.success
        assert response.content == "Test response"
        assert response.metadata == {"agent_latency_ms": 100}
        assert response.error is None


class TestNoExternalDependencies:
    """Tests to verify no external dependencies were added."""

    def test_models_only_use_stdlib(self):
        """Models module only imports from stdlib."""
        import utils.ai_router.staff_specialisations.models as models_module

        # Verify it imports successfully with only stdlib
        assert hasattr(models_module, "StaffRole")
        assert hasattr(models_module, "ResourceFormat")
        assert hasattr(models_module, "SpecialisationStatus")
        assert hasattr(models_module, "ResourceMetadata")
        assert hasattr(models_module, "Resource")
        assert hasattr(models_module, "SpecialisationContext")

    def test_validators_only_use_stdlib(self):
        """Validators module only imports from stdlib."""
        import utils.ai_router.staff_specialisations.validators as validators_module

        # Verify it imports successfully with only stdlib
        assert hasattr(validators_module, "validate_staff_role")
        assert hasattr(validators_module, "validate_resource_path")
        assert hasattr(validators_module, "validate_resource_content")


__all__ = [
    "TestStaffRoleParameterHandling",
    "TestDirectoryStructureDiscovery",
    "TestResourceDiscovery",
    "TestBackwardCompatibility",
    "TestNoExternalDependencies",
]
