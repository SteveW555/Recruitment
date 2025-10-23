"""
Unit tests for Staff Specialisations validators.

Tests cover:
- Staff role validation (case-sensitivity, valid values)
- Resource path validation (existence, readability, format, size)
- Resource content validation (UTF-8, non-empty)
"""

import pytest
import tempfile
from pathlib import Path

from utils.ai_router.staff_specialisations.validators import (
    validate_staff_role,
    validate_resource_path,
    validate_resource_content,
)
from utils.ai_router.staff_specialisations.models import StaffRole


class TestValidateStaffRole:
    """Tests for validate_staff_role function."""

    def test_none_is_valid(self):
        """None (no specialisation) is valid."""
        is_valid, error = validate_staff_role(None)
        assert is_valid
        assert error is None

    def test_all_valid_roles(self):
        """Test all 5 defined roles are valid."""
        for role in StaffRole:
            is_valid, error = validate_staff_role(role.value)
            assert is_valid, f"Role {role.value} should be valid"
            assert error is None

    def test_case_sensitive_exact_match_required(self):
        """Case-sensitive validation - exact match required."""
        # Valid
        is_valid, error = validate_staff_role("person_1_managing_director")
        assert is_valid

        # Invalid - different case
        is_valid, error = validate_staff_role("Person_1_Managing_Director")
        assert not is_valid
        assert error is not None
        assert "case-sensitive" in error.lower() or "valid values" in error

    def test_invalid_role_returns_helpful_error(self):
        """Invalid role returns helpful error with valid values."""
        is_valid, error = validate_staff_role("invalid_role")
        assert not is_valid
        assert error is not None
        assert "invalid_role" in error
        assert "person_1_managing_director" in error  # Lists valid values

    def test_empty_string_invalid(self):
        """Empty string is invalid."""
        is_valid, error = validate_staff_role("")
        assert not is_valid
        assert error is not None

    def test_whitespace_invalid(self):
        """Whitespace is invalid."""
        is_valid, error = validate_staff_role("   ")
        assert not is_valid
        assert error is not None

    def test_typo_in_role_detected(self):
        """Typos in role values are detected."""
        is_valid, error = validate_staff_role("person_1_managing_dirctor")  # typo
        assert not is_valid


class TestValidateResourcePath:
    """Tests for validate_resource_path function."""

    def test_valid_markdown_file(self):
        """Valid markdown file passes validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test\nContent")
            temp_path = Path(f.name)

        try:
            is_valid, error = validate_resource_path(temp_path)
            assert is_valid, f"Error: {error}"
            assert error is None
        finally:
            temp_path.unlink()

    def test_valid_json_file(self):
        """Valid JSON file passes validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"key": "value"}')
            temp_path = Path(f.name)

        try:
            is_valid, error = validate_resource_path(temp_path)
            assert is_valid
            assert error is None
        finally:
            temp_path.unlink()

    def test_valid_text_file(self):
        """Valid text file passes validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Plain text content")
            temp_path = Path(f.name)

        try:
            is_valid, error = validate_resource_path(temp_path)
            assert is_valid
            assert error is None
        finally:
            temp_path.unlink()

    def test_nonexistent_file(self):
        """Non-existent file fails validation."""
        nonexistent = Path("/nonexistent/path/file.md")
        is_valid, error = validate_resource_path(nonexistent)
        assert not is_valid
        assert error is not None
        assert "does not exist" in error.lower()

    def test_directory_not_file(self):
        """Directory (not file) fails validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            is_valid, error = validate_resource_path(dir_path)
            assert not is_valid
            assert error is not None
            assert "not a file" in error.lower()

    def test_file_too_large(self):
        """File > 10MB fails validation."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            # Write a string of known size
            f.write("x" * (11 * 1024 * 1024))  # 11MB
            temp_path = Path(f.name)

        try:
            is_valid, error = validate_resource_path(temp_path)
            assert not is_valid
            assert error is not None
            assert "10MB" in error or "exceeds" in error.lower()
        finally:
            temp_path.unlink()

    def test_unsupported_format(self):
        """Unsupported file format fails validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xyz", delete=False) as f:
            f.write("Content")
            temp_path = Path(f.name)

        try:
            is_valid, error = validate_resource_path(temp_path)
            assert not is_valid
            assert error is not None
            assert "format" in error.lower() or "supported" in error.lower()
        finally:
            temp_path.unlink()

    def test_readable_check(self):
        """File readability is verified."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# Test")
            temp_path = Path(f.name)

        try:
            # Make file unreadable
            temp_path.chmod(0o000)

            is_valid, error = validate_resource_path(temp_path)
            # Should fail (permission error)
            assert not is_valid
            assert error is not None
        finally:
            # Restore permissions before cleanup
            temp_path.chmod(0o644)
            temp_path.unlink()

    def test_empty_file_still_valid(self):
        """Empty file is still valid (content validation is separate)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            # Write nothing - empty file
            temp_path = Path(f.name)

        try:
            is_valid, error = validate_resource_path(temp_path)
            # File validation should pass (content validation is separate)
            assert is_valid
        finally:
            temp_path.unlink()


class TestValidateResourceContent:
    """Tests for validate_resource_content function."""

    def test_valid_content(self):
        """Valid non-empty content passes."""
        content = "# Header\nBody content"
        is_valid, error = validate_resource_content(content)
        assert is_valid
        assert error is None

    def test_empty_string_invalid(self):
        """Empty string fails validation."""
        is_valid, error = validate_resource_content("")
        assert not is_valid
        assert error is not None
        assert "empty" in error.lower()

    def test_whitespace_only_invalid(self):
        """Whitespace-only content fails validation."""
        is_valid, error = validate_resource_content("   \n  \t  ")
        assert not is_valid
        assert error is not None

    def test_valid_multiline_content(self):
        """Valid multi-line content passes."""
        content = """# Title

## Section 1
Content here

## Section 2
More content"""
        is_valid, error = validate_resource_content(content)
        assert is_valid

    def test_valid_json_content(self):
        """Valid JSON content passes (as string)."""
        content = '{"key": "value", "nested": {"data": [1, 2, 3]}}'
        is_valid, error = validate_resource_content(content)
        assert is_valid

    def test_single_character_valid(self):
        """Single character content is valid."""
        is_valid, error = validate_resource_content("a")
        assert is_valid

    def test_unicode_content_valid(self):
        """Unicode content is valid."""
        content = "# Título en Español\n🚀 Emoji support"
        is_valid, error = validate_resource_content(content)
        assert is_valid

    def test_newlines_preserved(self):
        """Content with newlines is valid."""
        content = "\n\n\nActual content\n\n"
        is_valid, error = validate_resource_content(content)
        assert is_valid


__all__ = [
    "TestValidateStaffRole",
    "TestValidateResourcePath",
    "TestValidateResourceContent",
]
