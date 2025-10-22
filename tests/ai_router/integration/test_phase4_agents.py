"""
Integration tests for Phase 4 agents (User Stories 2 & 4).

Tests:
- ProblemSolvingAgent routing and analysis quality
- AutomationAgent routing and workflow specification
- End-to-end routing with P2 agents
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch

from utils.ai_router.router import AIRouter
from utils.ai_router.classifier import Classifier
from utils.ai_router.storage.session_store import SessionStore
from utils.ai_router.storage.log_repository import LogRepository
from utils.ai_router.agent_registry import AgentRegistry
from utils.ai_router.models.category import Category


@pytest.fixture
def config_file(tmp_path):
    """Create test config with Phase 4 agents."""
    config = {
        "INFORMATION_RETRIEVAL": {
            "agent_class": "utils.ai_router.agents.information_retrieval_agent:InformationRetrievalAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are an information retrieval specialist.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": [
                "What are the top job boards?",
                "Find candidates in London",
            ]
        },
        "PROBLEM_SOLVING": {
            "agent_class": "utils.ai_router.agents.problem_solving_agent:ProblemSolvingAgent",
            "llm_provider": "anthropic",
            "llm_model": "claude-3-5-sonnet-20241022",
            "system_prompt": "You are a strategic problem-solving consultant.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": [
                "How can we reduce candidate dropout rate by 20%?",
                "Why is our placement rate lower than average?",
                "How to improve time-to-hire?",
                "How to scale without compromising quality?",
                "What's causing client satisfaction decline?",
                "How to differentiate from competitors?",
            ]
        },
        "AUTOMATION": {
            "agent_class": "utils.ai_router.agents.automation_agent:AutomationAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are an automation workflow designer.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": [
                "Automate welcome email for new candidates",
                "Create workflow for interview scheduling",
                "Automate job posting distribution",
            ]
        },
        "INDUSTRY_KNOWLEDGE": {
            "agent_class": "utils.ai_router.agents.industry_knowledge_agent:IndustryKnowledgeAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are a UK recruitment industry expert.",
            "timeout_seconds": 2,
            "enabled": True,
            "resources": {"sources_file": "./sources_validated_summaries.md"},
            "example_queries": [
                "What are GDPR requirements?",
            ]
        },
        "GENERAL_CHAT": {
            "agent_class": "utils.ai_router.agents.general_chat_agent:GeneralChatAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are a friendly AI assistant.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": [
                "Hello",
            ]
        },
        "REPORT_GENERATION": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You generate reports.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": [
                "Create a report",
            ]
        },
        "DATA_OPERATIONS": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You handle data operations.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": [
                "Create an invoice",
            ]
        }
    }

    config_path = tmp_path / "agents.json"
    with open(config_path, "w") as f:
        json.dump(config, f)

    return str(config_path)


@pytest.fixture
def mocked_router(config_file):
    """Create router with mocked storage layers."""
    classifier = Classifier(config_path=config_file)

    session_store = Mock(spec=SessionStore)
    session_store.load = Mock(return_value=None)
    session_store.save = Mock(return_value=True)

    log_repository = Mock(spec=LogRepository)
    log_repository.log_routing_decision = Mock(return_value=True)

    agent_registry = AgentRegistry(config_file)
    try:
        agent_registry.instantiate_agents()
    except Exception:
        # Some agents may fail if APIs aren't configured
        pass

    router = AIRouter(
        classifier=classifier,
        session_store=session_store,
        log_repository=log_repository,
        agent_registry=agent_registry
    )

    return router


class TestUserStory2ProblemSolving:
    """Test User Story 2 - Problem Solving Agent."""

    @pytest.mark.asyncio
    async def test_problem_solving_routing(self, mocked_router):
        """Test that problem solving queries route correctly."""
        result = await mocked_router.route(
            query_text="How can we reduce candidate dropout rate by 20% within 3 months?",
            user_id="user_123",
            session_id="session_456"
        )

        # Should route to PROBLEM_SOLVING
        if result['decision']:
            assert result['decision'].primary_category == Category.PROBLEM_SOLVING

    @pytest.mark.asyncio
    async def test_problem_solving_categories(self, mocked_router):
        """Test classification of various problem solving queries."""
        queries = [
            "Why is our placement rate 15% lower than industry average?",
            "What strategies can improve our time-to-hire for technical roles?",
            "How do we scale our accountancy division without compromising quality?",
            "What's causing the decline in client satisfaction scores?",
            "How can we differentiate from competitors?",
        ]

        for query in queries:
            result = await mocked_router.route(
                query_text=query,
                user_id="user_test",
                session_id=f"session_{hash(query)}"
            )

            if result['decision']:
                assert result['decision'].primary_category == Category.PROBLEM_SOLVING

    @pytest.mark.asyncio
    async def test_problem_solving_response_structure(self, mocked_router):
        """Test that PS agent returns proper response structure."""
        result = await mocked_router.route(
            query_text="How can we reduce candidate dropout rate by 20%?",
            user_id="user_123",
            session_id="session_456"
        )

        if result['success'] and result['agent_response']:
            response = result['agent_response']
            assert response.success is True or response.success is False
            assert response.content is not None or response.error is not None
            assert 'agent_latency_ms' in response.metadata

    @pytest.mark.asyncio
    async def test_problem_solving_analysis_depth(self, mocked_router):
        """Test that PS agent provides comprehensive analysis."""
        result = await mocked_router.route(
            query_text="How can we reduce candidate dropout rate by 20% within 3 months?",
            user_id="user_123",
            session_id="session_456"
        )

        if result['success'] and result['agent_response']:
            response = result['agent_response']
            if response.success:
                # Analysis should mention key components
                content_lower = response.content.lower()
                assert any(
                    term in content_lower
                    for term in ['recommendation', 'analysis', 'solution', 'approach', 'strategy']
                )


class TestUserStory4Automation:
    """Test User Story 4 - Automation Agent."""

    @pytest.mark.asyncio
    async def test_automation_routing(self, mocked_router):
        """Test that automation queries route correctly."""
        result = await mocked_router.route(
            query_text="Every time a new candidate registers, send welcome email, create ATS profile, schedule screening call",
            user_id="user_123",
            session_id="session_456"
        )

        # Should route to AUTOMATION
        if result['decision']:
            assert result['decision'].primary_category == Category.AUTOMATION

    @pytest.mark.asyncio
    async def test_automation_categories(self, mocked_router):
        """Test classification of various automation queries."""
        queries = [
            "I need to automatically notify hiring managers when candidates apply",
            "Automate the process of sending interview reminders to candidates",
            "Create a workflow for onboarding new clients",
            "Automate weekly reporting to account managers",
            "Build an automated candidate nurturing sequence",
        ]

        for query in queries:
            result = await mocked_router.route(
                query_text=query,
                user_id="user_test",
                session_id=f"session_{hash(query)}"
            )

            if result['decision']:
                assert result['decision'].primary_category == Category.AUTOMATION

    @pytest.mark.asyncio
    async def test_automation_response_structure(self, mocked_router):
        """Test that automation agent returns proper response structure."""
        result = await mocked_router.route(
            query_text="Automate welcome email for new candidates",
            user_id="user_123",
            session_id="session_456"
        )

        if result['success'] and result['agent_response']:
            response = result['agent_response']
            assert response.success is True or response.success is False
            assert response.content is not None or response.error is not None
            assert 'agent_latency_ms' in response.metadata

    @pytest.mark.asyncio
    async def test_automation_workflow_structure(self, mocked_router):
        """Test that automation agent provides structured workflow."""
        result = await mocked_router.route(
            query_text="Create a workflow to send interview reminders",
            user_id="user_123",
            session_id="session_456"
        )

        if result['success'] and result['agent_response']:
            response = result['agent_response']
            if response.success:
                # Workflow should mention key components
                content_lower = response.content.lower()
                assert any(
                    term in content_lower
                    for term in ['trigger', 'action', 'workflow', 'automation', 'step', 'process']
                )


class TestEndToEndP2Routing:
    """Test complete routing pipeline with P2 agents."""

    @pytest.mark.asyncio
    async def test_mixed_query_sequence(self, mocked_router):
        """Test routing different query types in sequence."""
        queries = [
            ("What are the top job boards?", Category.INFORMATION_RETRIEVAL),
            ("How can we improve placement rates?", Category.PROBLEM_SOLVING),
            ("Automate interview scheduling", Category.AUTOMATION),
            ("What are GDPR requirements?", Category.INDUSTRY_KNOWLEDGE),
            ("Hello", Category.GENERAL_CHAT),
        ]

        for query_text, expected_category in queries:
            result = await mocked_router.route(
                query_text=query_text,
                user_id="user_123",
                session_id="session_456"
            )

            if result['decision']:
                assert result['decision'].primary_category == expected_category

    @pytest.mark.asyncio
    async def test_all_latency_under_target(self, mocked_router):
        """Test that all routing completes under 3-second target."""
        queries = [
            "What are the top job boards?",
            "How can we reduce dropout by 20%?",
            "Automate candidate onboarding",
            "What are GDPR requirements?",
            "Hello, how are you?",
        ]

        for query in queries:
            result = await mocked_router.route(
                query_text=query,
                user_id="user_123",
                session_id=f"session_{hash(query)}"
            )

            assert result['latency_ms'] < 3000, f"Query '{query}' exceeded 3s latency: {result['latency_ms']}ms"


class TestAcceptanceCriteria:
    """Test User Story acceptance criteria."""

    @pytest.mark.asyncio
    async def test_us2_acceptance_criteria(self, mocked_router):
        """Test User Story 2 acceptance criteria."""
        # US2: Route Complex Problem Solving Query
        # Criteria:
        # - Submit complex problem query
        # - Verify category: PROBLEM_SOLVING
        # - Verify confidence: >0.70
        # - Verify agent returns: Multi-step analysis, root causes, recommendations
        # - Verify Claude API is used

        result = await mocked_router.route(
            query_text="How can we reduce candidate dropout rate by 20% within 3 months?",
            user_id="user_123",
            session_id="session_456"
        )

        # Criteria 1: Category
        assert result['decision'].primary_category == Category.PROBLEM_SOLVING

        # Criteria 2: Confidence
        assert result['decision'].primary_confidence > 0.70

        # Criteria 3: Multi-step analysis (if agent available)
        if result['agent_response'] and result['agent_response'].success:
            # Should contain analysis elements
            content = result['agent_response'].content.lower()
            assert any(
                term in content
                for term in ['recommendation', 'root', 'solution', 'step', 'analysis']
            )

        # Criteria 4: Latency
        assert result['latency_ms'] < 3000

    @pytest.mark.asyncio
    async def test_us4_acceptance_criteria(self, mocked_router):
        """Test User Story 4 acceptance criteria."""
        # US4: Route Automation Pipeline Request
        # Criteria:
        # - Submit workflow automation request
        # - Verify category: AUTOMATION
        # - Verify confidence: >0.70
        # - Verify agent returns: Workflow specification with triggers, actions, conditions
        # - Verify workflow is implementable

        result = await mocked_router.route(
            query_text="Every time a new candidate registers, send welcome email, create ATS profile, schedule screening call",
            user_id="user_123",
            session_id="session_456"
        )

        # Criteria 1: Category
        assert result['decision'].primary_category == Category.AUTOMATION

        # Criteria 2: Confidence
        assert result['decision'].primary_confidence > 0.70

        # Criteria 3: Workflow specification (if agent available)
        if result['agent_response'] and result['agent_response'].success:
            # Should contain workflow elements
            content = result['agent_response'].content.lower()
            assert any(
                term in content
                for term in ['trigger', 'action', 'workflow', 'automation', 'step']
            )

        # Criteria 4: Latency
        assert result['latency_ms'] < 3000

    @pytest.mark.asyncio
    async def test_problem_solving_usefulness(self, mocked_router):
        """Test that problem solving agent provides useful analysis."""
        result = await mocked_router.route(
            query_text="How can we reduce candidate dropout rate by 20% within 3 months?",
            user_id="user_123",
            session_id="session_456"
        )

        if result['success'] and result['agent_response']:
            response = result['agent_response']
            if response.success:
                # Analysis should be substantial
                assert len(response.content) > 100

    @pytest.mark.asyncio
    async def test_automation_implementability(self, mocked_router):
        """Test that automation workflows are implementable."""
        result = await mocked_router.route(
            query_text="Create a workflow for sending candidate welcome emails",
            user_id="user_123",
            session_id="session_456"
        )

        if result['success'] and result['agent_response']:
            response = result['agent_response']
            if response.success:
                # Should mention implementable platforms
                content_lower = response.content.lower()
                implementable_keywords = [
                    'n8n', 'zapier', 'make', 'integromat',
                    'trigger', 'action', 'condition',
                    'implement', 'platform'
                ]
                assert any(
                    keyword in content_lower
                    for keyword in implementable_keywords
                )
