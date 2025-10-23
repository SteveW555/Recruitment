"""
Specialisation manager for staff role resource context.

Manages loading and caching of specialisation context for agent requests.
"""

import logging
from pathlib import Path
from typing import List, Optional

from .models import StaffRole, SpecialisationContext, SpecialisationStatus
from .resource_loader import ResourceLoader
from .validators import validate_staff_role


logger = logging.getLogger(__name__)


class SpecialisationManager:
    """Manages specialisation context loading for agent requests."""

    def __init__(self, loader: Optional[ResourceLoader] = None, base_path: Optional[Path] = None):
        """
        Initialize SpecialisationManager.

        Args:
            loader: ResourceLoader instance (created if not provided)
            base_path: Base path to Staff Specialisation Resources directory
        """
        if loader is None:
            if base_path is None:
                base_path = Path(__file__).parent.parent.parent.parent / "Staff Specialisation Resources"
            loader = ResourceLoader(base_path)

        self.loader = loader
        self.base_path = loader.base_path

    def get_specialisation_context(self, staff_role: Optional[str]) -> SpecialisationContext:
        """
        Get specialisation context for a staff role.

        Validates the role, loads resources, and returns context with appropriate status.

        Args:
            staff_role: Staff role value (or None)

        Returns:
            SpecialisationContext with loaded resources or error information

        Example:
            ```python
            context = manager.get_specialisation_context("person_1_managing_director")
            if context.is_available():
                print(f"Loaded {context.resource_count} resources")
            ```
        """
        # Handle no staff_role
        if staff_role is None:
            return SpecialisationContext(
                staff_role=None,
                resources={},
                status=SpecialisationStatus.NOT_REQUESTED,
            )

        # Validate staff_role
        is_valid, error_message = validate_staff_role(staff_role)
        if not is_valid:
            logger.warning(f"Invalid staff_role: {staff_role}. Error: {error_message}")
            return SpecialisationContext(
                staff_role=staff_role,
                resources={},
                status=SpecialisationStatus.INVALID_ROLE,
                error_message=error_message,
            )

        # Check if directory exists
        role_dir = self.base_path / staff_role
        if not role_dir.exists():
            logger.info(f"No resources directory for {staff_role}")
            return SpecialisationContext(
                staff_role=staff_role,
                resources={},
                status=SpecialisationStatus.NO_RESOURCES,
            )

        # Load resources
        try:
            resources = self.loader.load_resources(staff_role)

            # Load guide
            guide = self.loader.load_guide(role_dir)

            # Determine status
            if resources:
                status = SpecialisationStatus.LOADED
            else:
                status = SpecialisationStatus.NO_RESOURCES

            context = SpecialisationContext(
                staff_role=staff_role,
                resources=resources,
                guide=guide,
                status=status,
            )

            logger.debug(
                f"Loaded specialisation context for {staff_role}: "
                f"status={status.value}, resources={len(resources)}"
            )
            return context

        except Exception as e:
            logger.error(f"Error loading specialisation context for {staff_role}: {e}")
            return SpecialisationContext(
                staff_role=staff_role,
                resources={},
                status=SpecialisationStatus.ERROR,
                error_message=f"Failed to load resources: {str(e)}",
            )

    def get_available_roles(self) -> List[str]:
        """
        Get list of valid staff roles.

        Returns:
            List of 5 valid role strings

        Example:
            ```python
            roles = manager.get_available_roles()
            # Returns: ["person_1_managing_director", "person_2_temp_consultant", ...]
            ```
        """
        return [role.value for role in StaffRole]

    def validate_staff_role(self, staff_role: Optional[str]) -> bool:
        """
        Convenience method to validate a staff_role.

        Args:
            staff_role: Staff role value to validate

        Returns:
            True if valid (or None), False otherwise

        Example:
            ```python
            if manager.validate_staff_role("person_1_managing_director"):
                print("Valid role")
            ```
        """
        is_valid, _ = validate_staff_role(staff_role)
        return is_valid

    def clear_cache(self, role_name: Optional[str] = None):
        """
        Clear resource cache.

        Args:
            role_name: Role name to clear (or None for all)

        Example:
            ```python
            manager.clear_cache("person_1_managing_director")
            manager.clear_cache()  # Clear all
            ```
        """
        self.loader.invalidate_cache(role_name)
        logger.debug(f"Cleared cache for {role_name or 'all roles'}")


__all__ = ["SpecialisationManager"]
