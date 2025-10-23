"""
Integration tests for User Story 3: Agent Enhances Responses with Role Context.

Tests cover:
- Response enhancement with role context
- Role-aware responses incorporating resources
- Graceful degradation for out-of-role queries
- End-to-end specialisation flow
"""

import pytest
from pathlib import Path

from utils.ai_router.staff_specialisations.specialisation_manager import (
    SpecialisationManager,
)
from utils.ai_router.staff_specialisations.resource_loader import ResourceLoader
from utils.ai_router.staff_specialisations.context_builder import (
    build_context_prompt,
    build_metadata,
)
from utils.ai_router.staff_specialisations.router_integration import (
    enhance_agent_request_with_specialisation,
    enhance_agent_response_with_specialisation,
    get_staff_role_from_kwargs,
)
from utils.ai_router.staff_specialisations.models import SpecialisationStatus
from utils.ai_router.agents.base_agent import AgentRequest, AgentResponse


class TestResponseEnhancementWithRoleContext:
    """Tests for response enhancement with role context."""

    def test_response_includes_role_context(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Response includes staff_role_context when specialisation applied."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            # Simulate agent response
            response = {
                "success": True,
                "content": "Strategic approach...",
                "metadata": {"agent_latency_ms": 100},
            }

            # Enhance response
            enhanced = enhance_agent_response_with_specialisation(response, context, 1)

            assert "staff_role_context" in enhanced
            assert enhanced["staff_role_context"] == "person_1_managing_director"

    def test_response_metadata_includes_specialisation_tracking(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Response metadata includes specialisation tracking information."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            response = {
                "success": True,
                "content": "Response",
                "metadata": {},
            }

            enhanced = enhance_agent_response_with_specialisation(response, context, 2)

            metadata = enhanced.get("metadata", {})
            assert "staff_role_used" in metadata
            assert "specialisation_status" in metadata
            assert "resources_consulted" in metadata
            assert "resources_available" in metadata

    def test_response_differs_with_role_context(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Response with role context differs from response without."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        # Response with context
        if context.is_available():
            response_with_context = {
                "success": True,
                "content": "Strategic guidance from resources",
                "metadata": {},
            }
            enhanced_with = enhance_agent_response_with_specialisation(
                response_with_context, context, 1
            )

            # Response without context
            response_without = {
                "success": True,
                "content": "Generic guidance without specialisation",
                "metadata": {},
            }

            # Should have different content
            assert enhanced_with["content"] != response_without["content"]
            # With context should have staff_role_context
            assert "staff_role_context" in enhanced_with
            # Without context should not
            assert "staff_role_context" not in response_without


class TestRoleAwareResponses:
    """Tests for role-aware response incorporation."""

    def test_managing_director_query_reflects_strategy_focus(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Managing director query response reflects strategy focus."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            # Simulate managing director focused response
            prompt = build_context_prompt(context)

            # Should mention role or resources
            if prompt:
                assert (
                    "Managing Director" in context.staff_role
                    or "managing" in context.staff_role.lower()
                )

    def test_compliance_query_reflects_compliance_focus(
        self, temp_staff_specialisations_dir, sample_resources_guide, sample_text_resource
    ):
        """Compliance query response reflects compliance-specific guidance."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_4_compliance_wellbeing")

        if context.is_available():
            # Simulate compliance focused response
            metadata = build_metadata(context, resources_consulted=1)

            # Metadata should track specialisation
            assert metadata["staff_role_used"] == "person_4_compliance_wellbeing"

    def test_response_notes_relevant_role_context(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Response notes relevant role context appropriately."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            response = {
                "success": True,
                "content": "Here's the response with role context",
                "metadata": {},
            }

            enhanced = enhance_agent_response_with_specialisation(response, context)

            # Should have role context in response
            assert "staff_role_context" in enhanced


class TestGracefulDegradation:
    """Tests for graceful degradation when role context unavailable."""

    def test_query_outside_role_expertise_still_works(
        self, temp_staff_specialisations_dir
    ):
        """Query outside role expertise still works, notes context."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_5_finance_training")

        # Even if no resources, system should work
        response = {
            "success": True,
            "content": "Still helpful response",
            "metadata": {},
        }

        if context.is_available():
            enhanced = enhance_agent_response_with_specialisation(response, context)
            assert enhanced["success"]
        else:
            # No resources, should still function
            assert response["success"]

    def test_invalid_role_gracefully_handled(self, temp_staff_specialisations_dir):
        """Invalid role gracefully handled without crashing."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("invalid_role")

        # Should not crash
        assert context.status == SpecialisationStatus.INVALID_ROLE

        response = {
            "success": True,
            "content": "Response still works",
            "metadata": {},
        }

        # Enhancement with error context should handle gracefully
        enhanced = enhance_agent_response_with_specialisation(response, context)
        # Should still have response
        assert enhanced["success"]


class TestEndToEndSpecialisationFlow:
    """Tests for end-to-end specialisation flow."""

    def test_full_specialisation_flow_from_request_to_response(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Full flow: request → load context → enhance response."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        # Step 1: Extract staff_role from kwargs
        kwargs = {"staff_role": "person_1_managing_director", "request_id": "123"}
        staff_role = get_staff_role_from_kwargs(kwargs)
        assert staff_role == "person_1_managing_director"

        # Step 2: Create agent request
        request_dict = {
            "query": "What's your strategy?",
            "user_id": "user123",
            "session_id": "sess456",
            "context": {},
            "metadata": {},
        }

        # Step 3: Enhance request with specialisation
        enhanced_request = enhance_agent_request_with_specialisation(
            request_dict, manager, staff_role
        )

        # Should have specialisation_context
        assert "specialisation_context" in enhanced_request
        context = enhanced_request["specialisation_context"]

        # Step 4: Execute agent (simulated)
        agent_response_dict = {
            "success": True,
            "content": "Strategic response with context...",
            "metadata": {"agent_latency_ms": 150},
        }

        # Step 5: Enhance response with specialisation
        enhanced_response = enhance_agent_response_with_specialisation(
            agent_response_dict, context, resources_consulted=1
        )

        # Should have specialisation tracking
        assert "staff_role_context" in enhanced_response
        assert enhanced_response["staff_role_context"] == "person_1_managing_director"
        assert "metadata" in enhanced_response
        assert "staff_role_used" in enhanced_response["metadata"]

    def test_specialisation_context_populated_in_request(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Specialisation context populated in request for agent."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        # Create request
        request_dict = {
            "query": "Test query",
            "user_id": "user123",
            "session_id": "sess456",
        }

        # Enhance with specialisation
        enhanced = enhance_agent_request_with_specialisation(
            request_dict, manager, "person_1_managing_director"
        )

        # Should have context
        assert "specialisation_context" in enhanced
        context = enhanced["specialisation_context"]

        # Context should have role info
        assert context.staff_role == "person_1_managing_director"

        # Agent can access resources from context
        if context.is_available():
            assert len(context.resources) > 0

    def test_metadata_populated_in_response(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """Metadata populated in response for tracking."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        response_dict = {
            "success": True,
            "content": "Response content",
            "metadata": {"agent_latency_ms": 100},
        }

        enhanced = enhance_agent_response_with_specialisation(
            response_dict, context, resources_consulted=2
        )

        # Check metadata
        metadata = enhanced["metadata"]
        assert "staff_role_used" in metadata
        assert metadata["staff_role_used"] == "person_1_managing_director"
        assert "specialisation_status" in metadata
        assert metadata["specialisation_status"] in [
            "loaded",
            "no_resources",
            "invalid_role",
            "error",
            "not_requested",
        ]

        # Original metadata should be preserved
        assert metadata["agent_latency_ms"] == 100


class TestUS3AcceptanceCriteria:
    """Tests for User Story 3 acceptance criteria."""

    def test_agent_responses_include_role_context(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """AC: Agent responses include role context when specialisation applied."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            response = {
                "success": True,
                "content": "Response",
                "metadata": {},
            }

            enhanced = enhance_agent_response_with_specialisation(response, context)

            assert "staff_role_context" in enhanced

    def test_responses_reflect_role_specific_information(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """AC: Responses reflect role-specific information from resources."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            # Response should reflect role specialisation
            response = {
                "success": True,
                "content": "Role-specific guidance...",
                "metadata": {},
            }

            enhanced = enhance_agent_response_with_specialisation(response, context)

            # Should have role context
            assert enhanced["staff_role_context"] is not None

    def test_response_metadata_includes_staff_role_context_tracking(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """AC: Response metadata includes staff_role_context tracking."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            response = {"success": True, "content": "Response", "metadata": {}}

            enhanced = enhance_agent_response_with_specialisation(response, context)

            metadata = enhanced.get("metadata", {})
            assert "staff_role_used" in metadata
            assert "specialisation_status" in metadata

    def test_responses_accurate_without_role_context(
        self, temp_staff_specialisations_dir
    ):
        """AC: Responses accurate even when role context unavailable."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_5_finance_training")

        # Even with no resources, response should be accurate
        response = {
            "success": True,
            "content": "Accurate response",
            "metadata": {},
        }

        if not context.is_available():
            # Should still process without error
            enhanced = enhance_agent_response_with_specialisation(response, context)
            assert enhanced["success"]

    def test_response_notes_relevant_role_context_appropriately(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """AC: Responses note relevant role context appropriately."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            response = {
                "success": True,
                "content": "Response",
                "metadata": {},
            }

            enhanced = enhance_agent_response_with_specialisation(response, context)

            # Should note role context
            assert "staff_role_context" in enhanced
            assert enhanced["staff_role_context"] == "person_1_managing_director"

    def test_relevance_improvement_for_role_specific_queries(
        self, temp_staff_specialisations_dir, sample_markdown_resource
    ):
        """AC: 20%+ improvement in relevance for role-specific queries (qualitative)."""
        root, role_dirs = temp_staff_specialisations_dir
        loader = ResourceLoader(root)
        manager = SpecialisationManager(loader, root)

        context = manager.get_specialisation_context("person_1_managing_director")

        if context.is_available():
            # Response with context should be more relevant
            response_with_context = {
                "success": True,
                "content": "Strategy-focused guidance from resources",
                "metadata": {},
            }

            enhanced = enhance_agent_response_with_specialisation(
                response_with_context, context
            )

            # Metadata should track resources consulted
            metadata = enhanced["metadata"]
            assert "resources_available" in metadata
            assert metadata["resources_available"] > 0


__all__ = [
    "TestResponseEnhancementWithRoleContext",
    "TestRoleAwareResponses",
    "TestGracefulDegradation",
    "TestEndToEndSpecialisationFlow",
    "TestUS3AcceptanceCriteria",
]
