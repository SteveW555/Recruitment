"""
Unit tests for AIRouter - Query routing orchestration.

Tests:
- Query validation and truncation
- Classification and routing flow
- Agent execution with retry logic
- Fallback handling
- Session context management
- Logging functionality
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, MagicMock, patch
from datetime import datetime

from utils.ai_router.router import AIRouter
from utils.ai_router.groq_classifier import GroqClassifier
from utils.ai_router.storage.session_store import SessionStore
from utils.ai_router.storage.log_repository import LogRepository
from utils.ai_router.agent_registry import AgentRegistry
from utils.ai_router.models.category import Category
from utils.ai_router.models.query import Query
from utils.ai_router.models.routing_decision import RoutingDecision
from utils.ai_router.agents.mock_agent import MockAgent, create_mock_agent


@pytest.fixture
def mock_classifier():
    """Create a mock Groq classifier."""
    classifier = Mock(spec=GroqClassifier)
    classifier.classify = Mock(return_value=RoutingDecision(
        query_id="test_1",
        primary_category=Category.INFORMATION_RETRIEVAL,
        primary_confidence=0.85,
        secondary_category=None,
        secondary_confidence=None,
        reasoning="Test classification",
        classification_latency_ms=50,
        fallback_triggered=False,
        user_override=False
    ))
    return classifier


@pytest.fixture
def mock_session_store():
    """Create a mock session store."""
    store = Mock(spec=SessionStore)
    store.load = Mock(return_value=None)
    store.save = Mock(return_value=True)
    return store


@pytest.fixture
def mock_log_repository():
    """Create a mock log repository."""
    repo = Mock(spec=LogRepository)
    repo.log_routing_decision = Mock(return_value=True)
    return repo


@pytest.fixture
def mock_agent_registry():
    """Create a mock agent registry."""
    registry = Mock(spec=AgentRegistry)

    # Create a mock agent
    mock_agent = create_mock_agent(
        Category.INFORMATION_RETRIEVAL,
        mock_response="Test response",
        simulate_latency_ms=100
    )

    registry.get_agent = Mock(return_value=mock_agent)
    registry.list_available_agents = Mock(return_value=[Category.INFORMATION_RETRIEVAL])

    return registry


@pytest.fixture
def router(mock_classifier, mock_session_store, mock_log_repository, mock_agent_registry):
    """Create a router with mocked dependencies."""
    return AIRouter(
        classifier=mock_classifier,
        session_store=mock_session_store,
        log_repository=mock_log_repository,
        agent_registry=mock_agent_registry,
        confidence_threshold=0.7,
        agent_timeout=2.0,
        max_retries=1,
        retry_delay_ms=100
    )


class TestQueryValidation:
    """Test query validation and processing."""

    @pytest.mark.asyncio
    async def test_valid_query_routing(self, router):
        """Test routing a valid query."""
        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        assert result['success'] is True
        assert result['query'] is not None
        assert result['decision'] is not None

    @pytest.mark.asyncio
    async def test_query_truncation(self, router):
        """Test that queries >1000 words are truncated."""
        long_query = "word " * 1500  # 7500 words

        result = await router.route(
            query_text=long_query,
            user_id="user_123",
            session_id="session_456"
        )

        # Query should be truncated
        assert len(result['query'].text.split()) <= 1000

    @pytest.mark.asyncio
    async def test_empty_query_rejection(self, router):
        """Test that empty queries are rejected."""
        with pytest.raises(ValueError):
            await router.route(
                query_text="",
                user_id="user_123",
                session_id="session_456"
            )

    @pytest.mark.asyncio
    async def test_missing_user_id(self, router):
        """Test that missing user_id is rejected."""
        with pytest.raises((ValueError, TypeError)):
            await router.route(
                query_text="test",
                user_id="",
                session_id="session_456"
            )


class TestClassificationRouting:
    """Test classification and routing logic."""

    @pytest.mark.asyncio
    async def test_routing_to_classified_category(self, router):
        """Test that query is routed to classified category."""
        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        assert result['decision'].primary_category == Category.INFORMATION_RETRIEVAL
        router.agent_registry.get_agent.assert_called_with(Category.INFORMATION_RETRIEVAL)

    @pytest.mark.asyncio
    async def test_low_confidence_triggers_clarification(self, router, mock_classifier):
        """Test that low confidence triggers clarification request."""
        mock_classifier.classify.return_value = RoutingDecision(
            query_id="test_1",
            primary_category=Category.INFORMATION_RETRIEVAL,
            primary_confidence=0.5,  # Below threshold
            secondary_category=None,
            secondary_confidence=None,
            reasoning="Low confidence",
            classification_latency_ms=50,
            fallback_triggered=True,
            user_override=False
        )

        result = await router.route(
            query_text="xyz abc 123",
            user_id="user_123",
            session_id="session_456"
        )

        assert result['success'] is False
        assert "clarification" in result['error'].lower()

    @pytest.mark.asyncio
    async def test_no_available_agent_returns_error(self, router, mock_agent_registry):
        """Test error when agent is not available."""
        mock_agent_registry.get_agent.return_value = None

        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        assert result['success'] is False
        assert "No agent available" in result['error']


class TestAgentExecution:
    """Test agent execution and response handling."""

    @pytest.mark.asyncio
    async def test_successful_agent_execution(self, router):
        """Test successful agent execution."""
        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        assert result['success'] is True
        assert result['agent_response'] is not None
        assert result['agent_response'].success is True
        assert len(result['agent_response'].content) > 0

    @pytest.mark.asyncio
    async def test_agent_latency_tracking(self, router):
        """Test that agent latency is tracked."""
        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        assert result['agent_response'].metadata.get('agent_latency_ms') is not None
        assert result['agent_response'].metadata['agent_latency_ms'] > 0

    @pytest.mark.asyncio
    async def test_agent_timeout_handling(self, router, mock_agent_registry):
        """Test handling of agent timeout."""
        # Create agent that always times out
        timeout_agent = Mock()
        timeout_agent.process = AsyncMock(side_effect=asyncio.TimeoutError())
        timeout_agent.enabled = True
        timeout_agent.config = {'category': 'INFORMATION_RETRIEVAL'}

        mock_agent_registry.get_agent.return_value = timeout_agent

        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        # Should have tried agent and failed
        assert timeout_agent.process.call_count > 0

    @pytest.mark.asyncio
    async def test_agent_retry_on_failure(self, router, mock_agent_registry):
        """Test that agent is retried on failure."""
        call_count = 0
        original_agent = mock_agent_registry.get_agent.return_value

        async def failing_agent(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Agent error")
            return await original_agent.process(*args, **kwargs)

        original_agent.process = AsyncMock(side_effect=failing_agent)

        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        # Should have retried (called agent more than once)
        assert original_agent.process.call_count > 1


class TestFallbackHandling:
    """Test fallback to general chat agent."""

    @pytest.mark.asyncio
    async def test_fallback_on_agent_failure(self, router, mock_agent_registry):
        """Test fallback to general chat when primary agent fails."""
        # Setup primary agent to fail
        failing_agent = Mock()
        failing_agent.process = AsyncMock(side_effect=Exception("Agent error"))
        failing_agent.enabled = True

        # Setup fallback agent
        fallback_agent = create_mock_agent(
            Category.GENERAL_CHAT,
            mock_response="Fallback response"
        )

        # Mock registry to return different agents for different categories
        def get_agent_side_effect(category):
            if category == Category.INFORMATION_RETRIEVAL:
                return failing_agent
            elif category == Category.GENERAL_CHAT:
                return fallback_agent
            return None

        mock_agent_registry.get_agent.side_effect = get_agent_side_effect

        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        # Should have used fallback
        assert result['decision'].fallback_triggered is True


class TestSessionManagement:
    """Test session context management."""

    @pytest.mark.asyncio
    async def test_session_context_loaded(self, router, mock_session_store):
        """Test that session context is loaded."""
        await router.route(
            query_text="test",
            user_id="user_123",
            session_id="session_456"
        )

        mock_session_store.load.assert_called()

    @pytest.mark.asyncio
    async def test_session_context_saved(self, router, mock_session_store):
        """Test that session context is saved after routing."""
        await router.route(
            query_text="test",
            user_id="user_123",
            session_id="session_456"
        )

        mock_session_store.save.assert_called()

    @pytest.mark.asyncio
    async def test_new_session_created_if_not_found(self, router, mock_session_store):
        """Test that new session is created if not found."""
        mock_session_store.load.return_value = None

        await router.route(
            query_text="test",
            user_id="user_123",
            session_id="session_456"
        )

        # Should have called save (creating new session)
        mock_session_store.save.assert_called()


class TestLogging:
    """Test routing decision logging."""

    @pytest.mark.asyncio
    async def test_routing_decision_logged(self, router, mock_log_repository):
        """Test that routing decisions are logged."""
        await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        mock_log_repository.log_routing_decision.assert_called()

    @pytest.mark.asyncio
    async def test_failure_logged(self, router, mock_classifier, mock_log_repository):
        """Test that failures are logged."""
        mock_classifier.classify.return_value = RoutingDecision(
            query_id="test_1",
            primary_category=Category.INFORMATION_RETRIEVAL,
            primary_confidence=0.5,  # Below threshold
            secondary_category=None,
            secondary_confidence=None,
            reasoning="Low confidence",
            classification_latency_ms=50,
            fallback_triggered=True,
            user_override=False
        )

        await router.route(
            query_text="xyz abc",
            user_id="user_123",
            session_id="session_456"
        )

        # Should have logged the failed routing
        mock_log_repository.log_routing_decision.assert_called()
        call_args = mock_log_repository.log_routing_decision.call_args
        assert call_args[1]['agent_success'] is False


class TestLatencyTracking:
    """Test end-to-end latency tracking."""

    @pytest.mark.asyncio
    async def test_total_latency_measured(self, router):
        """Test that total latency is measured."""
        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        assert 'latency_ms' in result
        assert result['latency_ms'] > 0
        assert result['latency_ms'] < 5000  # Should be less than 5 seconds

    @pytest.mark.asyncio
    async def test_latency_under_3_seconds(self, router):
        """Test that total latency stays under 3 seconds for successful queries."""
        result = await router.route(
            query_text="What are the top job boards?",
            user_id="user_123",
            session_id="session_456"
        )

        # Successful queries should complete in under 3 seconds
        if result['success']:
            assert result['latency_ms'] < 3000


class TestErrorHandling:
    """Test error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_unhandled_exception_returns_error(self, router, mock_classifier):
        """Test that unhandled exceptions return error result."""
        mock_classifier.classify.side_effect = Exception("Classifier error")

        result = await router.route(
            query_text="test",
            user_id="user_123",
            session_id="session_456"
        )

        assert result['success'] is False
        assert "Router error" in result['error'] or "error" in result['error'].lower()

    @pytest.mark.asyncio
    async def test_result_structure_on_success(self, router):
        """Test that result has correct structure on success."""
        result = await router.route(
            query_text="test",
            user_id="user_123",
            session_id="session_456"
        )

        assert 'success' in result
        assert 'query' in result
        assert 'decision' in result
        assert 'agent_response' in result
        assert 'error' in result
        assert 'latency_ms' in result

    @pytest.mark.asyncio
    async def test_result_structure_on_failure(self, router, mock_agent_registry):
        """Test that result has correct structure on failure."""
        mock_agent_registry.get_agent.return_value = None

        result = await router.route(
            query_text="test",
            user_id="user_123",
            session_id="session_456"
        )

        assert 'success' in result
        assert 'error' in result
        assert 'latency_ms' in result
