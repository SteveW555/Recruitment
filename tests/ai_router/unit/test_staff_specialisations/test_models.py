"""
Unit tests for Staff Specialisations data models.

Tests cover:
- StaffRole enum (all 5 values, case-sensitivity)
- ResourceMetadata validation
- Resource dataclass
- SpecialisationContext validation and methods
"""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime

from utils.ai_router.staff_specialisations.models import (
    StaffRole,
    ResourceFormat,
    SpecialisationStatus,
    ResourceMetadata,
    Resource,
    SpecialisationContext,
)


class TestStaffRole:
    """Tests for StaffRole enum."""

    def test_all_five_roles_present(self):
        """Verify all 5 roles are defined."""
        roles = list(StaffRole)
        assert len(roles) == 5

    def test_role_values_match_spec(self):
        """Verify role values match specification."""
        assert StaffRole.MANAGING_DIRECTOR.value == "person_1_managing_director"
        assert StaffRole.TEMP_CONSULTANT.value == "person_2_temp_consultant"
        assert StaffRole.RESOURCER_ADMIN_TECH.value == "person_3_resourcer_admin_tech"
        assert StaffRole.COMPLIANCE_WELLBEING.value == "person_4_compliance_wellbeing"
        assert StaffRole.FINANCE_TRAINING.value == "person_5_finance_training"

    def test_case_sensitive_validation(self):
        """Verify case-sensitive validation."""
        # Valid (exact case)
        assert StaffRole.is_valid("person_1_managing_director")

        # Invalid (different case)
        assert not StaffRole.is_valid("Person_1_Managing_Director")
        assert not StaffRole.is_valid("PERSON_1_MANAGING_DIRECTOR")

    def test_is_valid_with_all_roles(self):
        """Test is_valid with all role values."""
        for role in StaffRole:
            assert StaffRole.is_valid(role.value)

    def test_invalid_role_values(self):
        """Test is_valid with invalid values."""
        assert not StaffRole.is_valid("invalid_role")
        assert not StaffRole.is_valid("person_6_unknown")
        assert not StaffRole.is_valid("")


class TestResourceMetadata:
    """Tests for ResourceMetadata dataclass."""

    def test_create_valid_metadata(self):
        """Create valid metadata."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="test_resource",
                path=temp_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=100,
                is_guide=False,
            )
            assert metadata.name == "test_resource"
            assert metadata.format == ResourceFormat.MARKDOWN
            assert not metadata.is_guide
        finally:
            temp_path.unlink()

    def test_relative_path_property(self):
        """Test relative_path property."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="test",
                path=temp_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=100,
            )
            # Should return a string path
            assert isinstance(metadata.relative_path, str)
        finally:
            temp_path.unlink()

    def test_validate_nonexistent_path(self):
        """Validation fails for non-existent path."""
        metadata = ResourceMetadata(
            name="test",
            path=Path("/nonexistent/path/file.md"),
            format=ResourceFormat.MARKDOWN,
            size_bytes=100,
        )
        errors = metadata.validate()
        assert any("does not exist" in e for e in errors)

    def test_validate_excessive_size(self):
        """Validation fails for files > 10MB."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="test",
                path=temp_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=11 * 1024 * 1024,  # 11MB
            )
            errors = metadata.validate()
            assert any("10MB" in e for e in errors)
        finally:
            temp_path.unlink()

    def test_validate_timestamp_order(self):
        """Validation fails if updated_at < created_at."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="test",
                path=temp_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=100,
                created_at=1000,
                updated_at=500,  # Earlier than created_at
            )
            errors = metadata.validate()
            assert any("updated_at" in e for e in errors)
        finally:
            temp_path.unlink()

    def test_validate_name_with_separators(self):
        """Validation fails if name contains path separators."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="path/to/resource",
                path=temp_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=100,
            )
            errors = metadata.validate()
            assert any("path separator" in e for e in errors)
        finally:
            temp_path.unlink()


class TestResource:
    """Tests for Resource dataclass."""

    def test_valid_resource(self):
        """Create valid resource."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="test",
                path=temp_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=100,
            )
            resource = Resource(
                metadata=metadata,
                content="# Test\nContent",
                parsed={"format": "markdown", "content": "# Test\nContent"},
                error=None,
            )
            assert resource.is_valid
            assert resource.error is None
        finally:
            temp_path.unlink()

    def test_invalid_resource(self):
        """Create invalid resource with error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="bad_json",
                path=temp_path,
                format=ResourceFormat.JSON,
                size_bytes=100,
            )
            resource = Resource(
                metadata=metadata,
                content="{invalid json",
                parsed={},
                error="JSON decode error: Expecting value",
            )
            assert not resource.is_valid
            assert resource.error is not None
        finally:
            temp_path.unlink()


class TestSpecialisationContext:
    """Tests for SpecialisationContext dataclass."""

    def test_create_loaded_context(self):
        """Create a loaded context with resources."""
        context = SpecialisationContext(
            staff_role="person_1_managing_director",
            resources={"guide": "sample resource"},
            guide="# Resource Guide",
            status=SpecialisationStatus.LOADED,
        )
        assert context.is_available()
        assert not context.is_error()
        assert context.resource_count == 1

    def test_create_no_resources_context(self):
        """Create a context with NO_RESOURCES status."""
        context = SpecialisationContext(
            staff_role="person_2_temp_consultant",
            resources={},
            status=SpecialisationStatus.NO_RESOURCES,
        )
        assert not context.is_available()
        assert not context.is_error()
        assert context.resource_count == 0

    def test_create_invalid_role_context(self):
        """Create a context with INVALID_ROLE status."""
        context = SpecialisationContext(
            staff_role="invalid_role",
            resources={},
            status=SpecialisationStatus.INVALID_ROLE,
            error_message="Invalid staff role: invalid_role",
        )
        assert not context.is_available()
        assert context.is_error()

    def test_create_error_context(self):
        """Create a context with ERROR status."""
        context = SpecialisationContext(
            staff_role="person_1_managing_director",
            resources={},
            status=SpecialisationStatus.ERROR,
            error_message="Failed to load resources",
        )
        assert not context.is_available()
        assert context.is_error()

    def test_create_not_requested_context(self):
        """Create a context when no staff_role was provided."""
        context = SpecialisationContext(
            staff_role=None,
            resources={},
            status=SpecialisationStatus.NOT_REQUESTED,
        )
        assert not context.is_available()
        assert not context.is_error()

    def test_resource_count_auto_calculated(self):
        """resource_count is auto-calculated."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="test",
                path=temp_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=100,
            )
            resource = Resource(
                metadata=metadata,
                content="# Test",
                parsed={"format": "markdown"},
            )

            context = SpecialisationContext(
                staff_role="person_1_managing_director",
                resources={"guide": resource},
                status=SpecialisationStatus.LOADED,
            )
            assert context.resource_count == 1
        finally:
            temp_path.unlink()

    def test_validate_loaded_with_empty_resources(self):
        """Validation fails if LOADED status but empty resources."""
        context = SpecialisationContext(
            staff_role="person_1_managing_director",
            resources={},  # Empty!
            status=SpecialisationStatus.LOADED,
        )
        errors = context.validate()
        assert any("LOADED" in e for e in errors)

    def test_validate_error_without_message(self):
        """Validation fails if ERROR status but no error_message."""
        context = SpecialisationContext(
            staff_role="person_1_managing_director",
            resources={},
            status=SpecialisationStatus.ERROR,
            error_message=None,
        )
        errors = context.validate()
        assert any("ERROR" in e for e in errors)

    def test_validate_non_loaded_with_resources(self):
        """Validation fails if non-LOADED status but has resources."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            metadata = ResourceMetadata(
                name="test",
                path=temp_path,
                format=ResourceFormat.MARKDOWN,
                size_bytes=100,
            )
            resource = Resource(
                metadata=metadata,
                content="# Test",
                parsed={"format": "markdown"},
            )

            context = SpecialisationContext(
                staff_role="person_1_managing_director",
                resources={"guide": resource},
                status=SpecialisationStatus.NO_RESOURCES,  # Inconsistent!
            )
            errors = context.validate()
            assert any("resources" in e.lower() for e in errors)
        finally:
            temp_path.unlink()


__all__ = [
    "TestStaffRole",
    "TestResourceMetadata",
    "TestResource",
    "TestSpecialisationContext",
]
