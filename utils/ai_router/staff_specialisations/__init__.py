"""Staff Specialisations module for role-specific AI agent enhancement.

This module provides functionality to enhance AI agents with role-specific
resources and context based on organizational staff roles.

Exported Classes:
    - StaffRole: Enum of 5 organizational roles
    - SpecialisationContext: Container for role-specific resources
    - SpecialisationManager: Main manager for specialisation functionality
    - ResourceLoader: Handles resource discovery and loading
    - SpecialisationStatus: Enum for context loading status

Usage:
    from utils.ai_router.staff_specialisations import SpecialisationManager

    manager = SpecialisationManager()
    context = manager.get_specialisation_context(staff_role="person_1_managing_director")
"""

from .models import (
    StaffRole,
    ResourceFormat,
    SpecialisationStatus,
    ResourceMetadata,
    Resource,
    SpecialisationContext,
)
from .resource_loader import ResourceLoader
from .specialisation_manager import SpecialisationManager
from .context_builder import (
    build_context_prompt,
    select_relevant_resources,
    build_metadata,
)
from .validators import (
    validate_staff_role,
    validate_resource_path,
    validate_resource_content,
)
from .router_integration import (
    get_staff_role_from_kwargs,
    enhance_agent_request_with_specialisation,
    enhance_agent_response_with_specialisation,
)

__version__ = "0.1.0"
__author__ = "ProActive People"

__all__ = [
    "StaffRole",
    "ResourceFormat",
    "SpecialisationStatus",
    "ResourceMetadata",
    "Resource",
    "SpecialisationContext",
    "ResourceLoader",
    "SpecialisationManager",
    "build_context_prompt",
    "select_relevant_resources",
    "build_metadata",
    "validate_staff_role",
    "validate_resource_path",
    "validate_resource_content",
    "get_staff_role_from_kwargs",
    "enhance_agent_request_with_specialisation",
    "enhance_agent_response_with_specialisation",
]
