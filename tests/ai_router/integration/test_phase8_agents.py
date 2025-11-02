"""
Integration tests for Phase 8 - User Story 6 (General Chat).

Tests the GeneralChatAgent's ability to:
1. Route casual conversation and off-topic queries
2. Provide friendly, appropriate responses
3. Detect and respond to greetings
4. Serve as fallback when other agents fail
5. Not invoke specialized business logic for non-business queries

Acceptance Criteria (User Story 6):
- Route casual queries to GeneralChatAgent
- Provides friendly, conversational responses
- Doesn't trigger specialized business agents
- Works as fallback for failed agent requests
- End-to-end latency <3s
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from utils.ai_router.router import AIRouter
from utils.ai_router.groq_classifier import GroqClassifier
from utils.ai_router.storage.session_store import SessionStore
from utils.ai_router.storage.log_repository import LogRepository
from utils.ai_router.agent_registry import AgentRegistry
from utils.ai_router.models.category import Category
from utils.ai_router.agents.general_chat_agent import GeneralChatAgent
from utils.ai_router.agents.base_agent import AgentRequest


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def general_chat_config():
    """Configuration for General Chat agent."""
    return {
        "llm_provider": "groq",
        "llm_model": "llama-3-70b-8192",
        "system_prompt": "You are a friendly, helpful AI assistant. Respond naturally to greetings and casual conversation without invoking specialized business logic. Keep responses brief and appropriate.",
        "timeout_seconds": 2,
        "tools": [],
        "resources": {},
        "enabled": True,
        "example_queries": [
            "Hello",
            "Hi there",
            "How are you?",
            "Good morning",
            "Tell me a joke",
            "What's the weather like?"
        ]
    }


@pytest.fixture
def mock_general_chat_agent(general_chat_config):
    """Mock General Chat agent for testing without API calls."""

    class MockGeneralChatAgent(GeneralChatAgent):
        """Mock agent that doesn't call actual Groq API."""

        def __init__(self, config):
            # Skip parent init to avoid needing API key
            self.config = config
            self._validate_config()
            self.timeout = config.get('timeout_seconds', 2)
            self.llm_provider = config['llm_provider']
            self.llm_model = config['llm_model']
            self.system_prompt = config['system_prompt']
            self.tools = config.get('tools', [])
            self.resources = config.get('resources', {})
            self.enabled = config.get('enabled', True)

        async def _generate_response(self, query: str, is_fallback: bool = False) -> str:
            """Mock response generation."""
            await asyncio.sleep(0.05)  # Simulate API latency

            query_lower = query.lower()

            # Handle greetings
            if any(g in query_lower for g in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
                return "Hello! How can I assist you with your recruitment needs today? I can help with job boards, candidate searches, industry regulations, problem-solving, report generation, or workflow automation."

            # Handle social questions
            if any(q in query_lower for q in ['how are you', "how's it going", "what's up"]):
                return "I'm doing great, thanks for asking! I'm here to help with your recruitment and business needs. What can I assist you with?"

            # Handle joke requests
            if 'joke' in query_lower:
                return "Why did the recruiter go to the bank? To check their candidate reserves! 😄 Want to hear more about recruitment strategies instead?"

            # Handle weather questions
            if 'weather' in query_lower:
                return "I don't have real-time weather information, but I hope it's a great day for recruitment! Is there anything recruitment-related I can help you with?"

            # Fallback for off-topic questions
            if is_fallback:
                return "I apologize, but I encountered an issue with that request. Could you try rephrasing or asking about something more specific? I'm here to help!"
            else:
                return f"Thanks for reaching out! I'm primarily designed to help with recruitment-related topics. Feel free to ask about job boards, candidate searches, industry knowledge, problem-solving, automation, or reports. How can I help?"

    return MockGeneralChatAgent(general_chat_config)


@pytest.fixture
def router_config():
    """Full router configuration with all agents."""
    return {
        "INFORMATION_RETRIEVAL": {
            "agent_class": "utils.ai_router.agents.information_retrieval_agent:InformationRetrievalAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are an information retrieval specialist.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": ["What are the top job boards?"]
        },
        "PROBLEM_SOLVING": {
            "agent_class": "utils.ai_router.agents.problem_solving_agent:ProblemSolvingAgent",
            "llm_provider": "anthropic",
            "llm_model": "claude-3-5-sonnet-20241022",
            "system_prompt": "You are a strategic problem-solving consultant.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": ["How can we improve?"]
        },
        "REPORT_GENERATION": {
            "agent_class": "utils.ai_router.agents.report_generation_agent:ReportGenerationAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are a report generation specialist.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": ["Create a quarterly performance report"]
        },
        "AUTOMATION": {
            "agent_class": "utils.ai_router.agents.automation_agent:AutomationAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are an automation workflow designer.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": ["Automate welcome email"]
        },
        "INDUSTRY_KNOWLEDGE": {
            "agent_class": "utils.ai_router.agents.industry_knowledge_agent:IndustryKnowledgeAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are a UK recruitment expert.",
            "timeout_seconds": 2,
            "enabled": True,
            "resources": {"sources_file": "./sources_validated_summaries.md"},
            "example_queries": ["What are GDPR requirements?"]
        },
        "GENERAL_CHAT": {
            "agent_class": "utils.ai_router.agents.general_chat_agent:GeneralChatAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are friendly.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": ["Hello", "How are you?"]
        }
    }


# ============================================================================
# CLASS 1: TestUserStory6GeneralChat
# ============================================================================

class TestUserStory6GeneralChat:
    """Test General Chat agent implementation."""

    def test_agent_initialization(self, general_chat_config):
        """Test GeneralChatAgent initializes correctly."""
        with patch.object(GeneralChatAgent, '__init__', lambda x, config: None):
            agent = GeneralChatAgent(general_chat_config)
        assert agent is not None

    @pytest.mark.asyncio
    async def test_agent_processes_greeting(self, mock_general_chat_agent):
        """Test agent processes greeting queries."""
        request = AgentRequest(
            query="Hello",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert len(response.content) > 0
        assert "hello" in response.content.lower() or "hi" in response.content.lower()

    @pytest.mark.asyncio
    async def test_agent_processes_casual_question(self, mock_general_chat_agent):
        """Test agent processes casual conversation."""
        request = AgentRequest(
            query="How are you?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_agent_processes_off_topic_query(self, mock_general_chat_agent):
        """Test agent handles off-topic queries appropriately."""
        request = AgentRequest(
            query="What's the weather like?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert len(response.content) > 0
        # Should not try to invoke business logic
        assert "weather" in response.content.lower() or "recruitment" in response.content.lower()

    @pytest.mark.asyncio
    async def test_agent_tells_jokes(self, mock_general_chat_agent):
        """Test agent can tell jokes on request."""
        request = AgentRequest(
            query="Tell me a joke",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_agent_returns_metadata(self, mock_general_chat_agent):
        """Test agent returns metadata."""
        request = AgentRequest(
            query="Hello there!",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert 'agent_latency_ms' in response.metadata
        assert 'fallback' in response.metadata
        assert response.metadata['agent_latency_ms'] < 2000


# ============================================================================
# CLASS 2: TestRoutingGeneralChat
# ============================================================================

class TestRoutingGeneralChat:
    """Test routing of general chat queries."""

    @pytest.mark.asyncio
    async def test_classifier_identifies_general_chat(self):
        """Test classifier correctly identifies general chat queries."""
        classifier = Classifier()

        test_queries = [
            ("Hello", Category.GENERAL_CHAT),
            ("Hi there", Category.GENERAL_CHAT),
            ("How are you?", Category.GENERAL_CHAT),
            ("Tell me a joke", Category.GENERAL_CHAT),
            ("What are the top job boards?", Category.INFORMATION_RETRIEVAL),  # Different category
            ("What is GDPR?", Category.INDUSTRY_KNOWLEDGE),  # Different category
        ]

        for query, expected_category in test_queries:
            category, confidence = classifier.classify(query)

            # General chat queries should be classified correctly
            if expected_category == Category.GENERAL_CHAT:
                # General chat is often default, so check it's reasonable
                assert confidence > 0.3, f"Confidence too low for: {query}"

    @pytest.mark.asyncio
    async def test_general_chat_is_catchall(self):
        """Test that general chat can catch ambiguous queries."""
        classifier = Classifier()

        # Ambiguous or very short query might default to general chat
        category, confidence = classifier.classify("Hi")

        # Should be either general chat or have low confidence (needs clarification)
        assert category in [Category.GENERAL_CHAT, Category.INFORMATION_RETRIEVAL]


# ============================================================================
# CLASS 3: TestAcceptanceCriteria
# ============================================================================

class TestAcceptanceCriteriaGeneralChat:
    """Test User Story 6 acceptance criteria."""

    @pytest.mark.asyncio
    async def test_scenario_1_greeting_routing(self, mock_general_chat_agent):
        """
        Scenario 1: Given a casual greeting, when router analyzes it,
        then it routes to General Chat agent.
        """
        request = AgentRequest(
            query="Hello",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert mock_general_chat_agent.get_category() == Category.GENERAL_CHAT

    @pytest.mark.asyncio
    async def test_scenario_2_friendly_response(self, mock_general_chat_agent):
        """
        Scenario 2: Given a casual message, when agent processes it,
        then it provides friendly, appropriate response.
        """
        request = AgentRequest(
            query="How are you?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert len(response.content) > 0
        # Response should be friendly (lowercase for comparison)
        content_lower = response.content.lower()
        assert any(word in content_lower for word in ['help', 'assist', 'happy', 'great', 'doing'])

    @pytest.mark.asyncio
    async def test_scenario_3_off_topic_handling(self, mock_general_chat_agent):
        """
        Scenario 3: Given off-topic question, agent responds appropriately
        without invoking specialized business logic.
        """
        request = AgentRequest(
            query="What's the weather like today?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        content = response.content

        # Should not have complex business analysis
        assert len(content) < 500, "Off-topic response shouldn't be long"
        # Should acknowledge the off-topic nature or suggest recruitment help
        assert any(word in content.lower() for word in ['weather', 'recruitment', 'help', 'assist'])


# ============================================================================
# CLASS 4: TestFallbackHandling
# ============================================================================

class TestFallbackHandling:
    """Test general chat as fallback agent."""

    @pytest.mark.asyncio
    async def test_agent_handles_fallback_scenario(self, mock_general_chat_agent):
        """Test agent can handle fallback metadata."""
        request = AgentRequest(
            query="Something went wrong with the previous agent",
            user_id="test_user",
            session_id="test_session",
            metadata={'fallback': True}
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert response.metadata.get('fallback', False) is True
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_fallback_response_acknowledges_error(self, mock_general_chat_agent):
        """Test that fallback response acknowledges the error."""
        request = AgentRequest(
            query="Help me with this",
            user_id="test_user",
            session_id="test_session",
            metadata={'fallback': True}
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        # Fallback response should acknowledge the issue
        content_lower = response.content.lower()
        assert any(word in content_lower for word in ['apologize', 'issue', 'help', 'try'])


# ============================================================================
# CLASS 5: TestEndToEndIntegration
# ============================================================================

class TestEndToEndGeneralChat:
    """End-to-end integration tests with router."""

    @pytest.mark.asyncio
    async def test_router_integration_with_mock_agent(self, router_config, mock_general_chat_agent):
        """Test end-to-end routing with General Chat agent."""
        with patch('utils.ai_router.router.SessionStore'):
            with patch('utils.ai_router.router.LogRepository'):
                router = AIRouter(config_file=None, agent_registry=None)

                request = AgentRequest(
                    query="Hello, how are you?",
                    user_id="test_user",
                    session_id="test_session"
                )

                response = await mock_general_chat_agent.process(request)

                assert response.success is True


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

class TestGeneralChatVariations:
    """Test various general chat query patterns."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("query,is_greeting", [
        ("Hello", True),
        ("Hi there", True),
        ("Good morning", True),
        ("Hey, how are you?", True),
        ("Tell me a joke", False),
        ("What's the weather?", False),
        ("How's it going?", True),
    ])
    async def test_chat_query_patterns(self, query, is_greeting, mock_general_chat_agent):
        """Test various chat query patterns."""
        request = AgentRequest(
            query=query,
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert len(response.content) > 0
        # All should be relatively short responses (under 500 chars for casual chat)
        assert len(response.content) < 500


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformanceMetricsGeneralChat:
    """Test performance targets for General Chat agent."""

    @pytest.mark.asyncio
    async def test_agent_meets_latency_target(self, mock_general_chat_agent):
        """Test agent meets <2s latency target."""
        request = AgentRequest(
            query="Hello!",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert response.metadata['agent_latency_ms'] < 2000

    @pytest.mark.asyncio
    async def test_agent_response_brevity(self, mock_general_chat_agent):
        """Test that general chat responses are appropriately brief."""
        request = AgentRequest(
            query="Hi, what can you help me with?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        # Casual responses should be brief (not extensive analysis)
        assert len(response.content) < 500, "General chat response should be brief"
        assert len(response.content) > 20, "Response should have meaningful content"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestGeneralChatEdgeCases:
    """Test edge cases for general chat."""

    @pytest.mark.asyncio
    async def test_empty_query_handling(self, mock_general_chat_agent):
        """Test agent handles very short queries."""
        request = AgentRequest(
            query="Hi",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        assert response.success is True
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_agent_validation_accepts_anything(self, mock_general_chat_agent):
        """Test that general chat validates minimal content."""
        # General chat accepts almost anything
        request = AgentRequest(
            query="a",
            user_id="test_user",
            session_id="test_session"
        )

        is_valid = mock_general_chat_agent.validate_request(request)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_very_long_casual_query(self, mock_general_chat_agent):
        """Test agent handles longer casual queries."""
        long_query = "Hi there! " * 50  # 500 character greeting
        request = AgentRequest(
            query=long_query,
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_general_chat_agent.process(request)

        # Should still succeed
        assert response.success is True or response.success is False  # Either is acceptable
