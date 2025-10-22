"""
Pytest configuration and shared fixtures for AI Router tests.

Provides:
- Fixture factories for common objects
- Mock setup helpers
- Test data generators
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from utils.ai_router.models.category import Category
from utils.ai_router.models.query import Query
from utils.ai_router.models.routing_decision import RoutingDecision
from utils.ai_router.models.session_context import SessionContext


@pytest.fixture
def test_config_file():
    """Create a test configuration file with agent examples."""
    config = {
        "INFORMATION_RETRIEVAL": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are an information retrieval agent.",
            "timeout_seconds": 2,
            "example_queries": [
                "What are the top job boards?",
                "Where can I find candidates?",
                "How do I search for talent online?",
            ]
        },
        "PROBLEM_SOLVING": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "anthropic",
            "llm_model": "claude-3-5-sonnet-20241022",
            "system_prompt": "You are a problem solving agent.",
            "timeout_seconds": 2,
            "example_queries": [
                "How can we improve placement rates?",
                "What strategies reduce candidate dropout?",
            ]
        },
        "INDUSTRY_KNOWLEDGE": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are an industry knowledge agent for recruitment.",
            "timeout_seconds": 2,
            "example_queries": [
                "What are GDPR requirements for CVs?",
                "What's the typical notice period?",
            ]
        },
        "GENERAL_CHAT": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are a general chat assistant.",
            "timeout_seconds": 2,
            "example_queries": [
                "Hello",
                "How are you?",
                "What time is it?",
            ]
        },
        "REPORT_GENERATION": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "anthropic",
            "llm_model": "claude-3-5-sonnet-20241022",
            "system_prompt": "You generate reports from data.",
            "timeout_seconds": 2,
            "example_queries": [
                "Generate a recruitment report",
                "Create a placement summary",
            ]
        },
        "AUTOMATION": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You design automation workflows.",
            "timeout_seconds": 2,
            "example_queries": [
                "Automate the candidate screening process",
                "Create a workflow for interview scheduling",
            ]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        return f.name


@pytest.fixture
def sample_query():
    """Create a sample Query object for testing."""
    return Query(
        text="What are the top job boards in the UK?",
        user_id="test_user_123",
        session_id="test_session_456"
    )


@pytest.fixture
def sample_routing_decision():
    """Create a sample RoutingDecision object for testing."""
    return RoutingDecision(
        query_id="query_123",
        primary_category=Category.INFORMATION_RETRIEVAL,
        primary_confidence=0.85,
        secondary_category=Category.INDUSTRY_KNOWLEDGE,
        secondary_confidence=0.62,
        reasoning="Query matched information retrieval patterns with high confidence.",
        classification_latency_ms=45,
        fallback_triggered=False,
        user_override=False
    )


@pytest.fixture
def sample_session_context():
    """Create a sample SessionContext object for testing."""
    context = SessionContext(
        user_id="test_user_123",
        session_id="test_session_456"
    )

    context.add_message("test_user_123", "What are the top job boards?")
    context.add_routing_history("INFORMATION_RETRIEVAL", 0.85)

    return context


@pytest.fixture
def mock_async_context_manager():
    """Create a mock async context manager for testing."""
    async_cm = AsyncMock()
    async_cm.__aenter__ = AsyncMock()
    async_cm.__aexit__ = AsyncMock()
    return async_cm


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Pytest plugins
pytest_plugins = ['pytest_asyncio']
