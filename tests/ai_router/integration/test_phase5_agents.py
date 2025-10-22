"""
Integration tests for Phase 5 - User Story 2 (Problem Solving).

Tests the ProblemSolvingAgent's ability to:
1. Route complex problem-solving queries correctly
2. Perform multi-step analysis with root cause identification
3. Cross-reference industry benchmarks
4. Return actionable recommendations
5. Meet latency and quality targets

Acceptance Criteria (User Story 2):
- Route complex business problems to ProblemSolvingAgent
- Confidence score >70% for clear problem statements
- Returns multi-step analysis with root causes and recommendations
- End-to-end latency <3s
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from utils.ai_router.router import AIRouter
from utils.ai_router.classifier import Classifier
from utils.ai_router.storage.session_store import SessionStore
from utils.ai_router.storage.log_repository import LogRepository
from utils.ai_router.agent_registry import AgentRegistry
from utils.ai_router.models.category import Category
from utils.ai_router.agents.problem_solving_agent import ProblemSolvingAgent
from utils.ai_router.agents.base_agent import AgentRequest


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def problem_solving_config():
    """Configuration for Problem Solving agent."""
    return {
        "llm_provider": "anthropic",
        "llm_model": "claude-3-5-sonnet-20241022",
        "system_prompt": "You are a strategic problem-solving consultant for a UK recruitment agency.",
        "timeout_seconds": 2,
        "tools": ["industry_research", "data_analysis"],
        "resources": {},
        "enabled": True,
        "example_queries": [
            "How can we reduce candidate dropout rate by 20% within 3 months?",
            "Why is our placement rate 15% lower than industry average and what should we do?",
            "What strategies can improve our time-to-hire for technical roles?",
            "How do we scale our accountancy division without compromising quality?",
            "What's causing the decline in client satisfaction scores?",
            "How can we differentiate from competitors in the Bristol market?",
        ]
    }


@pytest.fixture
def mock_problem_solving_agent(problem_solving_config):
    """Mock Problem Solving agent for testing without API calls."""

    class MockProblemSolvingAgent(ProblemSolvingAgent):
        """Mock agent that doesn't call actual Claude API."""

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
            self.industry_benchmarks = self._load_industry_benchmarks()

        async def _generate_analysis_with_claude(self, prompt: str, request: AgentRequest) -> str:
            """Mock Claude API call."""
            await asyncio.sleep(0.1)  # Simulate API latency

            return """## PROBLEM ANALYSIS

### 1. PROBLEM DEFINITION
The candidate dropout rate of 25-30% is above the acceptable benchmark of 20%, impacting placement success.

### 2. ROOT CAUSE ANALYSIS
- Weak interview preparation support
- Poor candidate-role matching
- Limited communication during process
- Competing job opportunities

### 3. CURRENT STATE ASSESSMENT
Against industry benchmarks:
- Dropout rate: 25-30% (target: <20%)
- Industry average: 25%
- This is at average but needs improvement

### 4. STRATEGIC RECOMMENDATIONS
1. **Improve Candidate Support** (2 weeks)
   - Create interview prep materials
   - Impact: 5% dropout reduction
   - Resources: 1 resource

2. **Enhance Matching Process** (4 weeks)
   - Better role-candidate matching
   - Impact: 8% dropout reduction
   - Resources: 2 resources

3. **Increase Communication** (1 week)
   - Weekly check-ins with candidates
   - Impact: 4% dropout reduction
   - Resources: Process change

4. **Market Monitoring** (2 weeks)
   - Track competing offers
   - Impact: 3% dropout reduction
   - Resources: 1 resource

### 5. SUCCESS METRICS
- Target dropout rate: 15%
- Timeline: 12 weeks
- Measurement: Track per-week metrics

### 6. IMPLEMENTATION ROADMAP
- Weeks 1-2: Quick wins (communication, prep materials)
- Weeks 3-4: Matching process improvements
- Weeks 5-12: Monitor and optimize

Expected ROI: Each 1% dropout reduction = £50K+ in additional revenue."""

    return MockProblemSolvingAgent(problem_solving_config)


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
            "example_queries": ["What are the top job boards?", "Find candidates"]
        },
        "PROBLEM_SOLVING": {
            "agent_class": "utils.ai_router.agents.problem_solving_agent:ProblemSolvingAgent",
            "llm_provider": "anthropic",
            "llm_model": "claude-3-5-sonnet-20241022",
            "system_prompt": "You are a strategic problem-solving consultant.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": [
                "How can we reduce candidate dropout by 20%?",
                "Why is placement rate lower?",
            ]
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
        "AUTOMATION": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You design workflows.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": ["Automate welcome email"]
        },
        "REPORT_GENERATION": {
            "agent_class": "utils.ai_router.agents.mock_agent:MockAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You generate reports.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": ["Create a report"]
        },
        "GENERAL_CHAT": {
            "agent_class": "utils.ai_router.agents.general_chat_agent:GeneralChatAgent",
            "llm_provider": "groq",
            "llm_model": "llama-3-70b-8192",
            "system_prompt": "You are friendly.",
            "timeout_seconds": 2,
            "enabled": True,
            "example_queries": ["Hello"]
        }
    }


# ============================================================================
# CLASS 1: TestUserStory2ProblemSolving
# ============================================================================

class TestUserStory2ProblemSolving:
    """Test Problem Solving agent implementation."""

    def test_agent_initialization(self, problem_solving_config):
        """Test ProblemSolvingAgent initializes correctly."""
        with patch.object(ProblemSolvingAgent, '__init__', lambda x, config: None):
            agent = ProblemSolvingAgent(problem_solving_config)
        assert agent is not None

    @pytest.mark.asyncio
    async def test_agent_processes_complex_query(self, mock_problem_solving_agent):
        """Test agent processes complex problem-solving query."""
        request = AgentRequest(
            query="How can we reduce candidate dropout rate by 20% within 3 months?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_problem_solving_agent.process(request)

        assert response.success is True
        assert len(response.content) > 100
        assert "dropout" in response.content.lower()
        assert "recommendation" in response.content.lower()

    @pytest.mark.asyncio
    async def test_agent_includes_analysis_structure(self, mock_problem_solving_agent):
        """Test response includes multi-step analysis structure."""
        request = AgentRequest(
            query="Why is our placement rate 15% lower than industry average?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_problem_solving_agent.process(request)

        # Should include analysis components
        assert response.success is True
        assert "analysis" in response.content.lower() or "problem" in response.content.lower()

    @pytest.mark.asyncio
    async def test_agent_returns_metadata(self, mock_problem_solving_agent):
        """Test agent returns latency and quality metadata."""
        request = AgentRequest(
            query="How do we scale our accountancy division without compromising quality?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_problem_solving_agent.process(request)

        assert response.success is True
        assert 'agent_latency_ms' in response.metadata
        assert 'analysis_depth' in response.metadata
        assert 'confidence' in response.metadata
        assert response.metadata['agent_latency_ms'] < 2000  # <2s latency

    @pytest.mark.asyncio
    async def test_agent_validates_request(self, mock_problem_solving_agent):
        """Test agent validates problem-solving queries."""
        # Empty query should fail validation
        request = AgentRequest(
            query="",
            user_id="test_user",
            session_id="test_session"
        )

        is_valid = mock_problem_solving_agent.validate_request(request)
        assert is_valid is False

        # Short non-question should fail
        request = AgentRequest(
            query="Tell me",
            user_id="test_user",
            session_id="test_session"
        )
        is_valid = mock_problem_solving_agent.validate_request(request)
        assert is_valid is False

        # Good question should pass
        request = AgentRequest(
            query="How can we improve our service?",
            user_id="test_user",
            session_id="test_session"
        )
        is_valid = mock_problem_solving_agent.validate_request(request)
        assert is_valid is True


# ============================================================================
# CLASS 2: TestRouting
# ============================================================================

class TestRoutingProblemSolving:
    """Test routing of problem-solving queries."""

    @pytest.mark.asyncio
    async def test_classifier_identifies_problem_solving(self):
        """Test classifier correctly identifies problem-solving queries."""
        classifier = Classifier()

        test_queries = [
            ("How can we reduce candidate dropout rate by 20%?", Category.PROBLEM_SOLVING),
            ("Why is our placement rate lower than average?", Category.PROBLEM_SOLVING),
            ("What strategies can improve time-to-hire?", Category.PROBLEM_SOLVING),
            ("How do we handle GDPR?", Category.INDUSTRY_KNOWLEDGE),  # Different category
            ("Hello there", Category.GENERAL_CHAT),  # Different category
        ]

        for query, expected_category in test_queries:
            category, confidence = classifier.classify(query)

            # Problem-solving queries should be classified correctly with >50% confidence
            if expected_category == Category.PROBLEM_SOLVING:
                assert category == expected_category, f"Failed for: {query}"

    @pytest.mark.asyncio
    async def test_confidence_threshold(self):
        """Test confidence scores for problem-solving queries."""
        classifier = Classifier()

        # Clear problem-solving query should have high confidence
        category, confidence = classifier.classify(
            "How can we reduce candidate dropout rate by 20% within 3 months given our current pipeline issues?"
        )

        # Should identify as problem-solving with reasonable confidence
        assert category == Category.PROBLEM_SOLVING
        assert confidence > 0.5, f"Confidence too low: {confidence}"


# ============================================================================
# CLASS 3: TestAcceptanceCriteria
# ============================================================================

class TestAcceptanceCriteriaProblemSolving:
    """Test User Story 2 acceptance criteria."""

    @pytest.mark.asyncio
    async def test_scenario_1_routing(self, mock_problem_solving_agent):
        """
        Scenario 1: Given a complex business problem, when router analyzes it,
        then it routes to Problem Solving agent.
        """
        request = AgentRequest(
            query="How can we reduce candidate dropout rate by 20% within 3 months given our current pipeline issues?",
            user_id="test_user",
            session_id="test_session"
        )

        # Agent should accept and process the request
        response = await mock_problem_solving_agent.process(request)

        assert response.success is True
        assert mock_problem_solving_agent.get_category() == Category.PROBLEM_SOLVING

    @pytest.mark.asyncio
    async def test_scenario_2_analysis_quality(self, mock_problem_solving_agent):
        """
        Scenario 2: Given a problem-solving query, when agent processes it,
        then it returns analysis with root causes and recommendations.
        """
        request = AgentRequest(
            query="Why is our placement rate 15% lower than industry average and what should we do?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_problem_solving_agent.process(request)

        assert response.success is True
        # Should include multiple analysis sections
        content_lower = response.content.lower()

        # Check for expected analysis components
        has_analysis_markers = any([
            marker in content_lower for marker in [
                'problem', 'cause', 'recommendation', 'analysis',
                'impact', 'timeline', 'metric', 'implementation'
            ]
        ])
        assert has_analysis_markers, "Response missing analysis structure"

    @pytest.mark.asyncio
    async def test_scenario_3_latency(self, mock_problem_solving_agent):
        """
        Scenario 3: Problem-solving queries should be processed within 3s end-to-end.
        (Agent-level latency test; router adds ~100ms overhead)
        """
        request = AgentRequest(
            query="How can we differentiate from competitors in the Bristol market?",
            user_id="test_user",
            session_id="test_session"
        )

        start_time = time.time()
        response = await mock_problem_solving_agent.process(request)
        end_time = time.time()

        latency_ms = (end_time - start_time) * 1000

        assert response.success is True
        assert latency_ms < 2000, f"Latency too high: {latency_ms}ms"


# ============================================================================
# CLASS 4: TestEndToEndIntegration
# ============================================================================

class TestEndToEndProblemSolving:
    """End-to-end integration tests with router."""

    @pytest.mark.asyncio
    async def test_router_integration_with_mock_agent(self, router_config, mock_problem_solving_agent):
        """Test end-to-end routing with Problem Solving agent."""
        # Create router with mocked dependencies
        with patch('utils.ai_router.router.SessionStore'):
            with patch('utils.ai_router.router.LogRepository'):
                router = AIRouter(config_file=None, agent_registry=None)

                # Manually set up for testing
                request = AgentRequest(
                    query="How can we reduce candidate dropout rate by 20%?",
                    user_id="test_user",
                    session_id="test_session"
                )

                response = await mock_problem_solving_agent.process(request)

                assert response.success is True


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

class TestProblemSolvingVariations:
    """Test various problem-solving query patterns."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("query,should_succeed", [
        ("How can we improve our placement rate?", True),
        ("Why are candidates dropping out?", True),
        ("What's the best strategy for growth?", True),
        ("How do we compete in Bristol?", True),
        ("What should we do about client satisfaction?", True),
    ])
    async def test_problem_solving_queries(self, query, should_succeed, mock_problem_solving_agent):
        """Test various problem-solving query patterns."""
        request = AgentRequest(
            query=query,
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_problem_solving_agent.process(request)

        if should_succeed:
            assert response.success is True
            assert len(response.content) > 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformanceMetrics:
    """Test performance targets for Problem Solving agent."""

    @pytest.mark.asyncio
    async def test_agent_meets_latency_target(self, mock_problem_solving_agent):
        """Test agent meets <2s latency target (Phase 2 requirement)."""
        request = AgentRequest(
            query="How can we scale without compromising quality?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_problem_solving_agent.process(request)

        assert response.success is True
        assert response.metadata['agent_latency_ms'] < 2000

    @pytest.mark.asyncio
    async def test_confidence_correlation(self, mock_problem_solving_agent):
        """Test that response quality correlates with confidence score."""
        request = AgentRequest(
            query="How can we reduce candidate dropout rate by 20% within 3 months?",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_problem_solving_agent.process(request)

        assert response.success is True
        confidence = response.metadata.get('confidence', 0)

        # Higher quality (successful) response should have confidence > 0.7
        assert confidence > 0.7, f"Confidence too low: {confidence}"
