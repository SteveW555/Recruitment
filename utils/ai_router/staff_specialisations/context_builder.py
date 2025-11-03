"""
Context builder for specialisation resources.

Builds prompt additions and metadata from specialisation context to enhance
agent responses with role-specific information.
"""

import logging
from typing import Dict, List, Any, Optional

from .models import SpecialisationContext, Resource


logger = logging.getLogger(__name__)


def build_context_prompt(context: SpecialisationContext) -> str:
    """
    Build a prompt addition from specialisation context.

    Generates text to be prepended to the agent's system prompt that includes
    resource guides and relevant information for the role.

    Args:
        context: SpecialisationContext with loaded resources

    Returns:
        Prompt text to add to agent's system prompt (empty if not available)

    Example:
        ```python
        context = manager.get_specialisation_context("person_1_managing_director")
        prompt_addition = build_context_prompt(context)
        system_prompt = base_prompt + "\n\n" + prompt_addition
        ```
    """
    if not context.is_available():
        return ""

    lines = []
    lines.append(f"## Role Context: {context.staff_role}")
    lines.append("")

    # Add guide if available
    if context.guide:
        lines.append("### Resource Guide")
        lines.append(context.guide)
        lines.append("")

    # Add resource summaries
    if context.resources:
        lines.append("### Available Resources")
        for name, resource in sorted(context.resources.items()):
            if resource.is_valid:
                lines.append(f"- **{name}** ({resource.metadata.format.value})")
        lines.append("")

    lines.append("Use the resources above to provide role-specific guidance and information.")

    prompt_text = "\n".join(lines)
    logger.debug(f"Built context prompt ({len(prompt_text)} chars) for {context.staff_role}")
    return prompt_text


def select_relevant_resources(
    context: SpecialisationContext, query: str, max_resources: int = 3
) -> List[Resource]:
    """
    Select most relevant resources for a query.

    Agent-driven selection: returns all resources and lets agent decide,
    but can use resources-guide.md as hint for priority ordering.

    Args:
        context: SpecialisationContext with loaded resources
        query: User query to match against resources
        max_resources: Maximum resources to return

    Returns:
        List of Resource objects, up to max_resources

    Example:
        ```python
        resources = select_relevant_resources(context, "How do I manage key accounts?")
        for resource in resources:
            print(f"- {resource.metadata.name}: {resource.metadata.format.value}")
        ```
    """
    if not context.is_available():
        return []

    # Build list of all resources with relevance scores
    scored_resources = []

    for name, resource in context.resources.items():
        if not resource.is_valid:
            continue

        # Score based on query match (simple keyword matching)
        score = _compute_relevance_score(resource, query)
        scored_resources.append((score, name, resource))

    # Sort by score (highest first)
    scored_resources.sort(key=lambda x: x[0], reverse=True)

    # Return top resources
    selected = [resource for _, _, resource in scored_resources[:max_resources]]
    logger.debug(
        f"Selected {len(selected)} resources for query "
        f"(from {len(context.resources)} available)"
    )
    return selected


def build_metadata(
    context: SpecialisationContext, resources_consulted: int = 0
) -> Dict[str, Any]:
    """
    Build response metadata dict from specialisation context.

    Creates metadata fields for tracking specialisation in responses.

    Args:
        context: SpecialisationContext with loaded resources
        resources_consulted: Number of resources consulted in response

    Returns:
        Dict with metadata fields for response

    Example:
        ```python
        metadata = build_metadata(context, resources_consulted=2)
        # Returns: {
        #     "staff_role_used": "person_1_managing_director",
        #     "specialisation_status": "loaded",
        #     "resources_consulted": 2,
        #     "resources_available": 4,
        # }
        ```
    """
    metadata = {
        "staff_role_used": context.staff_role,
        "specialisation_status": context.status.value,
    }

    if context.is_available():
        metadata["resources_consulted"] = resources_consulted
        metadata["resources_available"] = len(context.resources)
        metadata["has_guide"] = context.guide is not None

    return metadata


# Private helper functions


def _compute_relevance_score(resource: Resource, query: str) -> float:
    """
    Compute relevance score between resource and query.

    Simple keyword-matching based scoring. Higher scores = more relevant.

    Args:
        resource: Resource to score
        query: User query

    Returns:
        Relevance score (0.0 to 1.0)
    """
    if not resource.is_valid:
        return 0.0

    # Normalize to lowercase for comparison
    query_lower = query.lower()
    content_lower = resource.content.lower()

    # Basic scoring: exact word matches
    score = 0.0

    # Extract key terms from query (split on whitespace/punctuation)
    import re

    query_terms = re.findall(r"\b\w+\b", query_lower)

    if not query_terms:
        return 0.0

    # Count matches in content
    matches = 0
    for term in query_terms:
        if term in content_lower:
            matches += 1

    # Score = fraction of query terms found
    score = matches / len(query_terms) if query_terms else 0.0

    # Bonus for metadata matching
    resource_name_lower = resource.metadata.name.lower()
    if any(term in resource_name_lower for term in query_terms):
        score = min(1.0, score + 0.2)

    return score


__all__ = [
    "build_context_prompt",
    "select_relevant_resources",
    "build_metadata",
]
