"""
Router integration for Staff Specialisations.

Provides integration functions to add staff specialisation support to the AIRouter
without modifying the core router implementation.

This allows agents to receive and process role-specific resources while maintaining
full backward compatibility with existing router behavior.
"""

import logging
from typing import Optional, Dict, Any

from .specialisation_manager import SpecialisationManager
from .context_builder import build_metadata


logger = logging.getLogger(__name__)


def enhance_agent_request_with_specialisation(
    request_dict: Dict[str, Any],
    specialisation_manager: SpecialisationManager,
    staff_role: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Enhance an agent request with specialisation context.

    This function is called before agent execution to load and attach
    specialisation resources if a staff_role is provided.

    Args:
        request_dict: Original request dictionary (from AgentRequest)
        specialisation_manager: Manager for loading specialisation context
        staff_role: Optional staff role from request kwargs

    Returns:
        Enhanced request dictionary with specialisation_context added

    Example:
        ```python
        request = {"query": "...", "user_id": "...", ...}
        staff_role = kwargs.get("staff_role")
        enhanced = enhance_agent_request_with_specialisation(
            request, manager, staff_role
        )
        # enhanced now has "specialisation_context" field
        ```
    """
    if not staff_role:
        # No specialisation requested
        return request_dict

    # Load specialisation context
    context = specialisation_manager.get_specialisation_context(staff_role)

    # Add to request (will be None if not available, but that's OK)
    request_dict["specialisation_context"] = context

    logger.debug(
        f"Enhanced request with specialisation: "
        f"role={staff_role}, status={context.status.value}"
    )

    return request_dict


def enhance_agent_response_with_specialisation(
    response_dict: Dict[str, Any],
    specialisation_context: Optional[Any] = None,
    resources_consulted: int = 0,
) -> Dict[str, Any]:
    """
    Enhance an agent response with specialisation metadata.

    This function is called after agent execution to add specialisation
    tracking information to the response metadata.

    Args:
        response_dict: Original response dictionary (from AgentResponse)
        specialisation_context: SpecialisationContext if specialisation was used
        resources_consulted: Number of resources consulted in response

    Returns:
        Enhanced response dictionary with specialisation metadata

    Example:
        ```python
        response = {"success": True, "content": "...", "metadata": {...}}
        enhanced = enhance_agent_response_with_specialisation(
            response, context, resources_consulted=2
        )
        # response.metadata now includes specialisation tracking
        ```
    """
    if not specialisation_context or not specialisation_context.is_available():
        # No specialisation to track
        return response_dict

    # Add specialisation context to response
    response_dict["staff_role_context"] = specialisation_context.staff_role

    # Add specialisation metadata
    specialisation_metadata = build_metadata(
        specialisation_context,
        resources_consulted=resources_consulted,
    )

    # Merge with existing metadata
    if "metadata" not in response_dict:
        response_dict["metadata"] = {}

    response_dict["metadata"].update(specialisation_metadata)

    logger.debug(
        f"Enhanced response with specialisation: "
        f"role={specialisation_context.staff_role}, "
        f"resources={len(specialisation_context.resources)}"
    )

    return response_dict


def get_staff_role_from_kwargs(kwargs: Dict[str, Any]) -> Optional[str]:
    """
    Extract staff_role from request kwargs.

    Looks for 'staff_role' key in kwargs and returns it if present.

    Args:
        kwargs: Request keyword arguments

    Returns:
        Staff role value if present, None otherwise

    Example:
        ```python
        staff_role = get_staff_role_from_kwargs(kwargs)
        if staff_role:
            # Use specialisation
        ```
    """
    return kwargs.get("staff_role")


__all__ = [
    "enhance_agent_request_with_specialisation",
    "enhance_agent_response_with_specialisation",
    "get_staff_role_from_kwargs",
]
