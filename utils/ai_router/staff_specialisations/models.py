"""
Data models for Staff Specialisations feature.

This module defines the core data structures used throughout the staff
specialisations system, including enums, dataclasses, and their validation
rules.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional
import time


class StaffRole(str, Enum):
    """5 ProActive People organizational roles with resource specialisations."""

    MANAGING_DIRECTOR = "person_1_managing_director"
    TEMP_CONSULTANT = "person_2_temp_consultant"
    RESOURCER_ADMIN_TECH = "person_3_resourcer_admin_tech"
    COMPLIANCE_WELLBEING = "person_4_compliance_wellbeing"
    FINANCE_TRAINING = "person_5_finance_training"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid staff role (case-sensitive)."""
        return value in cls._value2member_map_


class ResourceFormat(str, Enum):
    """Supported resource file formats."""

    MARKDOWN = "markdown"  # .md files
    JSON = "json"  # .json files
    TEXT = "text"  # .txt files
    GUIDE = "guide"  # resources-guide.md (special)


class SpecialisationStatus(str, Enum):
    """Status of specialisation context loading."""

    LOADED = "loaded"  # Successfully loaded
    INVALID_ROLE = "invalid_role"  # Staff role not found
    NO_RESOURCES = "no_resources"  # Role exists but no resources yet
    ERROR = "error"  # Loading error
    NOT_REQUESTED = "not_requested"  # No staff_role parameter


@dataclass
class ResourceMetadata:
    """Metadata about a role resource file."""

    name: str  # Resource identifier (filename without ext)
    path: Path  # Full file path
    format: ResourceFormat  # File format
    size_bytes: int  # File size
    is_guide: bool = False  # True if resources-guide.md
    created_at: float = field(default_factory=time.time)  # Unix timestamp
    updated_at: float = field(default_factory=time.time)  # Unix timestamp
    checksum: str = ""  # SHA-256 for change detection (optional)

    @property
    def relative_path(self) -> str:
        """Path relative to repo root for logging."""
        try:
            return str(self.path.relative_to(Path.cwd()))
        except ValueError:
            return str(self.path)

    def validate(self) -> list[str]:
        """Validate metadata fields. Returns list of errors (empty if valid)."""
        errors = []

        # Validate path
        if not self.path.exists():
            errors.append(f"Path does not exist: {self.path}")
        elif not self.path.is_file():
            errors.append(f"Path is not a file: {self.path}")
        elif not self.path.stat().st_mode & 0o400:  # Check read permission
            errors.append(f"Path is not readable: {self.path}")

        # Validate size
        if self.size_bytes < 0:
            errors.append("size_bytes cannot be negative")
        elif self.size_bytes > 10 * 1024 * 1024:  # 10MB limit
            errors.append(f"File size {self.size_bytes} exceeds 10MB limit")

        # Validate timestamps
        if self.updated_at < self.created_at:
            errors.append("updated_at must be >= created_at")

        # Validate name
        if not self.name or len(self.name) > 100:
            errors.append("name must be 1-100 characters")
        if "/" in self.name or "\\" in self.name:
            errors.append("name cannot contain path separators")

        return errors


@dataclass
class Resource:
    """Parsed content of a resource file."""

    metadata: ResourceMetadata  # File metadata
    content: str  # Raw file content
    parsed: Dict[str, Any]  # Format-specific parsed data
    error: Optional[str] = None  # Parse error if any

    @property
    def is_valid(self) -> bool:
        """True if resource loaded successfully."""
        return self.error is None


@dataclass
class SpecialisationContext:
    """All specialisation information for a query."""

    staff_role: Optional[str]  # Requested role
    resources: Dict[str, Resource] = field(default_factory=dict)  # Loaded resources
    guide: Optional[str] = None  # resources-guide.md content
    status: SpecialisationStatus = SpecialisationStatus.LOADED
    error_message: Optional[str] = None  # If status=ERROR
    loaded_at: float = field(default_factory=time.time)  # Timestamp
    resource_count: int = field(init=False)  # Convenience field

    def __post_init__(self):
        """Calculate derived fields."""
        self.resource_count = len(self.resources)

    def is_available(self) -> bool:
        """True if specialisation context is usable."""
        return self.status == SpecialisationStatus.LOADED and len(self.resources) > 0

    def is_error(self) -> bool:
        """True if loading failed."""
        return self.status in (
            SpecialisationStatus.ERROR,
            SpecialisationStatus.INVALID_ROLE,
        )

    def validate(self) -> list[str]:
        """Validate context. Returns list of errors (empty if valid)."""
        errors = []

        # If status is LOADED, resources must not be empty
        if self.status == SpecialisationStatus.LOADED and len(self.resources) == 0:
            errors.append(
                "If status=LOADED, resources dict must not be empty (use NO_RESOURCES instead)"
            )

        # If status is ERROR, error_message must be set
        if self.status == SpecialisationStatus.ERROR and not self.error_message:
            errors.append("If status=ERROR, error_message must be set")

        # If status != LOADED, resources must be empty
        if self.status != SpecialisationStatus.LOADED and len(self.resources) > 0:
            errors.append(
                f"If status={self.status.value}, resources dict must be empty"
            )

        # loaded_at should be recent (within last hour)
        current_time = time.time()
        if current_time - self.loaded_at > 3600:
            errors.append("loaded_at is more than 1 hour old")

        return errors


__all__ = [
    "StaffRole",
    "ResourceFormat",
    "SpecialisationStatus",
    "ResourceMetadata",
    "Resource",
    "SpecialisationContext",
]
