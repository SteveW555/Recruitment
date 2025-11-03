"""
Validators for Staff Specialisations feature.

This module provides validation functions for staff roles, resource paths,
and resource content.
"""

from pathlib import Path
from typing import Optional

from .models import StaffRole, ResourceFormat


def validate_staff_role(staff_role: Optional[str]) -> tuple[bool, Optional[str]]:
    """
    Validate a staff role value (case-sensitive).

    Args:
        staff_role: Staff role value to validate (or None)

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid or None
        - error_message: Helpful error message if invalid, None otherwise

    Example:
        ```python
        is_valid, error = validate_staff_role("person_1_managing_director")
        if not is_valid:
            print(f"Error: {error}")
        ```
    """
    # None is valid (staff specialisation is optional)
    if staff_role is None:
        return True, None

    # Check if it's a valid enum value
    if StaffRole.is_valid(staff_role):
        return True, None

    # Build helpful error message
    valid_values = [role.value for role in StaffRole]
    error = f"Invalid staff_role: '{staff_role}'. Valid values (case-sensitive): {', '.join(valid_values)}"
    return False, error


def validate_resource_path(path: Path) -> tuple[bool, Optional[str]]:
    """
    Validate a resource file path.

    Checks:
    - File exists
    - File is readable
    - File size is < 10MB
    - File format is supported

    Args:
        path: Path to resource file

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        ```python
        is_valid, error = validate_resource_path(Path("resources/guide.md"))
        if not is_valid:
            print(f"Error: {error}")
        ```
    """
    # Check existence
    if not path.exists():
        return False, f"Resource file does not exist: {path}"

    # Check it's a file
    if not path.is_file():
        return False, f"Path is not a file: {path}"

    # Check readability
    try:
        with open(path, "r", encoding="utf-8") as f:
            f.read(1)  # Try to read first byte
    except (PermissionError, IOError) as e:
        return False, f"Cannot read resource file: {e}"

    # Check size
    try:
        size = path.stat().st_size
        if size > 10 * 1024 * 1024:  # 10MB
            return False, f"Resource file exceeds 10MB limit: {size} bytes"
    except OSError as e:
        return False, f"Cannot stat resource file: {e}"

    # Check format (by extension)
    suffix = path.suffix.lower()
    supported = {".md", ".json", ".txt"}
    if suffix not in supported:
        return (
            False,
            f"Unsupported file format: {suffix}. Supported: {', '.join(supported)}",
        )

    return True, None


def validate_resource_content(content: str) -> tuple[bool, Optional[str]]:
    """
    Validate resource file content.

    Checks:
    - Content is valid UTF-8
    - Content is not empty

    Args:
        content: Raw file content

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        ```python
        is_valid, error = validate_resource_content(content)
        if not is_valid:
            print(f"Error: {error}")
        ```
    """
    # Check it's a string (already UTF-8 decoded by this point)
    if not isinstance(content, str):
        return False, "Content must be a string"

    # Check it's not empty
    if not content or not content.strip():
        return False, "Resource content cannot be empty"

    return True, None


__all__ = [
    "validate_staff_role",
    "validate_resource_path",
    "validate_resource_content",
]
