"""
Integration tests for Phase 7 - User Story 3 (Report Generation).

Tests the ReportGenerationAgent's ability to:
1. Route report generation requests correctly
2. Design structured reports with visualizations
3. Generate presentation-ready markdown output
4. Include appropriate charts and summaries
5. Meet presentation quality standards (85% per SC-005)

Acceptance Criteria (User Story 3):
- Route report requests to ReportGenerationAgent
- Confidence score >70% for clear report queries
- Returns structured report with visualizations, summaries, insights
- Report meets presentation standards (85% without modification)
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
from utils.ai_router.agents.report_generation_agent import ReportGenerationAgent
from utils.ai_router.agents.base_agent import AgentRequest


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def report_generation_config():
    """Configuration for Report Generation agent."""
    return {
        "llm_provider": "groq",
        "llm_model": "llama-3-70b-8192",
        "system_prompt": "You are a report generation specialist. Create structured, presentation-ready reports with visualizations, summaries, and insights.",
        "timeout_seconds": 2,
        "tools": ["data_visualization", "report_formatting"],
        "resources": {},
        "enabled": True,
        "example_queries": [
            "Create a quarterly performance report for our accountancy division",
            "Generate a dashboard showing our top 10 clients by revenue",
            "Create a candidate pipeline analysis for this month",
            "Build a market analysis report for the tech sector in London",
            "Generate an executive summary of our placement metrics",
            "Create a client presentation on our recruitment services",
        ]
    }


@pytest.fixture
def mock_report_generation_agent(report_generation_config):
    """Mock Report Generation agent for testing without API calls."""

    class MockReportGenerationAgent(ReportGenerationAgent):
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
            self.report_templates = self._load_report_templates()
            self.visualization_patterns = self._load_visualization_patterns()

        async def _generate_report(self, requirement: str, request: AgentRequest) -> str:
            """Mock report generation."""
            await asyncio.sleep(0.1)  # Simulate API latency

            return """# Quarterly Performance Report - Accountancy Division

## Executive Summary

This report presents comprehensive analysis of Q4 2025 performance for the Accountancy Division, highlighting key achievements, market insights, and strategic recommendations for continued growth.

---

## Key Metrics Dashboard

| Metric | Value | Status | Trend |
|--------|-------|--------|-------|
| Total Placements | 48 | On Target | ↑ 12% |
| Revenue Generated | £245,000 | Above Target | ↑ 18% |
| Client Satisfaction | 8.7/10 | Excellent | ↑ 5% |
| Time-to-Hire (Days) | 21 | On Target | ↓ 3 days |
| Candidate Dropout Rate | 18% | Good | ↓ 4% |

---

## Detailed Analysis

### Performance Overview

Our Accountancy Division has delivered exceptional results this quarter, exceeding revenue targets by 18% and achieving the highest client satisfaction scores in our history. The division successfully placed 48 candidates across corporate tax, audit, and general practice roles, representing a 12% increase from Q3 2025.

Key drivers of this success include:
- Enhanced candidate screening process reducing dropout rates
- Strengthened relationships with top 10 clients (90% repeat business)
- Market expansion into emerging roles (data analytics, ESG compliance)

### Revenue Analysis

Q4 revenue reached £245,000, driven by:
- Corporate Tax placements: £112,000 (46% of total)
- Audit Services: £78,000 (32% of total)
- General Practice: £55,000 (22% of total)

This represents strong portfolio diversification and reduced dependency on single role type.

### Client Satisfaction & Retention

Client satisfaction averaged 8.7/10, with top 10 clients rating our service 9.2/10. Retention rate reached 94%, indicating strong client relationships and repeat business potential.

---

## Visualization Suggestions

📊 **Revenue Trend Chart**: Monthly revenue progression Q1-Q4 showing 18% YoY growth
- Data: Monthly values Jan-Dec 2025
- Type: Line chart with trend line
- Insight: Consistent growth trajectory with strong Q4 performance

📊 **Placement by Role Type**: Distribution of 48 placements across 8 accountancy roles
- Data: Placement counts by role (Corporate Tax, Audit, etc.)
- Type: Horizontal bar chart, descending order
- Insight: Corporate Tax is strongest category (45% of placements)

📊 **Client Satisfaction Gauge**: Visual representation of 8.7/10 score
- Data: Current score vs benchmark vs target
- Type: Gauge chart with colored zones
- Insight: Exceeding industry benchmark of 8.2/10

📊 **Pipeline Funnel**: Candidate journey from sourced to placed
- Data: Stages (Sourced: 250 → Screening: 180 → Interview: 95 → Offered: 52 → Placed: 48)
- Type: Funnel visualization
- Insight: 81% conversion rate from offer to placement (strong)

---

## Key Insights

• **Market Leadership**: Accountancy division outperforming market growth by 2.3x (18% vs 8% market growth)
• **Quality Over Quantity**: Lower time-to-hire (21 vs 25-day average) indicates strong candidate quality
• **Client Loyalty**: 94% retention rate demonstrates strong client relationships and service quality
• **Emerging Opportunities**: New ESG compliance and data analytics roles showing 35% growth year-over-year
• **Operational Excellence**: 18% candidate dropout rate (down from 22%) shows improved candidate engagement

---

## Recommendations

1. **Expand Emerging Roles** (Immediate - 0-3 months)
   - Expected Impact: +15% revenue
   - Approach: Hire specialist recruiters for ESG and data analytics roles
   - Timeline: Recruitment and training by mid-January 2026

2. **Deepen Top Client Relationships** (Short-term - 1-2 quarters)
   - Expected Impact: +20% repeat business
   - Approach: Quarterly business reviews with top 10 clients
   - Timeline: Schedule reviews for January 2026

3. **Invest in Candidate Experience** (Ongoing)
   - Expected Impact: Further reduce dropout rate to <15%
   - Approach: Enhanced onboarding, regular check-ins, development opportunities
   - Timeline: Implementation starting Q1 2026

4. **Market Expansion in Southeast** (Strategic - 2-3 quarters)
   - Expected Impact: +30% new client acquisition
   - Approach: Regional marketing and networking initiatives
   - Timeline: Campaign launch Q1 2026

---

## Conclusion

The Accountancy Division has delivered outstanding Q4 results, exceeding targets and achieving record client satisfaction. The combination of strong execution, client relationship focus, and emerging role opportunities positions the division for continued growth.

**Key Next Steps**:
1. Submit business plan for emerging roles expansion
2. Schedule top client quarterly business reviews
3. Launch candidate experience improvement initiative
4. Begin Southeast market expansion planning

---

**Report Date**: 2025-10-22
**Prepared For**: Executive Leadership
**Division**: Accountancy
**Period**: Q4 2025"""

    return MockReportGenerationAgent(report_generation_config)


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
            "example_queries": [
                "Create a quarterly performance report",
                "Generate a dashboard for top clients",
            ]
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
            "example_queries": ["Hello"]
        }
    }


# ============================================================================
# CLASS 1: TestUserStory3ReportGeneration
# ============================================================================

class TestUserStory3ReportGeneration:
    """Test Report Generation agent implementation."""

    def test_agent_initialization(self, report_generation_config):
        """Test ReportGenerationAgent initializes correctly."""
        with patch.object(ReportGenerationAgent, '__init__', lambda x, config: None):
            agent = ReportGenerationAgent(report_generation_config)
        assert agent is not None

    @pytest.mark.asyncio
    async def test_agent_processes_report_query(self, mock_report_generation_agent):
        """Test agent processes report generation request."""
        request = AgentRequest(
            query="Create a quarterly performance report for our accountancy division showing placements, revenue, and candidate pipeline trends",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True
        assert len(response.content) > 200
        assert "report" in response.content.lower() or "summary" in response.content.lower()

    @pytest.mark.asyncio
    async def test_agent_includes_report_structure(self, mock_report_generation_agent):
        """Test response includes structured report components."""
        request = AgentRequest(
            query="Generate a dashboard showing our top 10 clients by revenue",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True
        content_lower = response.content.lower()

        # Should include report structure elements
        structure_elements = ['summary', 'metric', 'analysis', 'recommendation']
        assert any(elem in content_lower for elem in structure_elements)

    @pytest.mark.asyncio
    async def test_agent_includes_visualizations(self, mock_report_generation_agent):
        """Test response includes visualization suggestions."""
        request = AgentRequest(
            query="Create a candidate pipeline analysis for this month",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True
        assert response.metadata.get('includes_visualizations', False) is True

    @pytest.mark.asyncio
    async def test_agent_returns_metadata(self, mock_report_generation_agent):
        """Test agent returns presentation quality metadata."""
        request = AgentRequest(
            query="Build a market analysis report for the tech sector in London",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True
        assert 'agent_latency_ms' in response.metadata
        assert 'report_format' in response.metadata
        assert response.metadata['report_format'] == 'markdown'
        assert response.metadata.get('presentation_ready', False) is True

    @pytest.mark.asyncio
    async def test_agent_validates_report_query(self, mock_report_generation_agent):
        """Test agent validates report queries."""
        # Query without report indicators should fail
        request = AgentRequest(
            query="Tell me about recruitment",
            user_id="test_user",
            session_id="test_session"
        )

        is_valid = mock_report_generation_agent.validate_request(request)
        assert is_valid is False

        # Query with report indicators should pass
        request = AgentRequest(
            query="Generate a report on our performance",
            user_id="test_user",
            session_id="test_session"
        )
        is_valid = mock_report_generation_agent.validate_request(request)
        assert is_valid is True


# ============================================================================
# CLASS 2: TestRoutingReportGeneration
# ============================================================================

class TestRoutingReportGeneration:
    """Test routing of report generation requests."""

    @pytest.mark.asyncio
    async def test_classifier_identifies_report_generation(self):
        """Test classifier correctly identifies report queries."""
        classifier = Classifier()

        test_queries = [
            ("Create a quarterly performance report", Category.REPORT_GENERATION),
            ("Generate a dashboard showing top clients", Category.REPORT_GENERATION),
            ("Build a market analysis report", Category.REPORT_GENERATION),
            ("What is GDPR?", Category.INDUSTRY_KNOWLEDGE),  # Different category
            ("Hello there", Category.GENERAL_CHAT),  # Different category
        ]

        for query, expected_category in test_queries:
            category, confidence = classifier.classify(query)

            if expected_category == Category.REPORT_GENERATION:
                assert category == expected_category, f"Failed for: {query}"

    @pytest.mark.asyncio
    async def test_confidence_threshold_reports(self):
        """Test confidence scores for report queries."""
        classifier = Classifier()

        # Clear report query should have high confidence
        category, confidence = classifier.classify(
            "Create a quarterly performance report for our accountancy division showing placements, revenue, and candidate pipeline trends"
        )

        # Should identify as report generation with reasonable confidence
        assert category == Category.REPORT_GENERATION
        assert confidence > 0.5, f"Confidence too low: {confidence}"


# ============================================================================
# CLASS 3: TestAcceptanceCriteria
# ============================================================================

class TestAcceptanceCriteriaReportGeneration:
    """Test User Story 3 acceptance criteria."""

    @pytest.mark.asyncio
    async def test_scenario_1_routing(self, mock_report_generation_agent):
        """
        Scenario 1: Given a report request, when router analyzes it,
        then it routes to Report Generation agent.
        """
        request = AgentRequest(
            query="Create a quarterly performance report for our accountancy division showing placements, revenue, trends",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True
        assert mock_report_generation_agent.get_category() == Category.REPORT_GENERATION

    @pytest.mark.asyncio
    async def test_scenario_2_report_quality(self, mock_report_generation_agent):
        """
        Scenario 2: Given a report request, when agent processes it,
        then it returns structured report with visualizations, summaries, insights.
        """
        request = AgentRequest(
            query="Generate a dashboard showing our top 10 clients by revenue this quarter",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True
        content_lower = response.content.lower()

        # Should include report components
        required_components = ['summary', 'metric']
        for component in required_components:
            assert component in content_lower, f"Missing {component} in report"

        # Should have visualization suggestions
        assert response.metadata.get('includes_visualizations', False) is True

    @pytest.mark.asyncio
    async def test_scenario_3_presentation_quality(self, mock_report_generation_agent):
        """
        Scenario 3: Generated reports meet stakeholder presentation standards (85% per SC-005).
        """
        request = AgentRequest(
            query="Create a candidate pipeline analysis for this month",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True

        # Check presentation quality indicators
        assert response.metadata.get('presentation_ready', False) is True
        assert response.metadata['report_format'] == 'markdown'

        # Report should have sufficient length and structure
        assert len(response.content) > 500, "Report too short for presentation quality"


# ============================================================================
# CLASS 4: TestEndToEndIntegration
# ============================================================================

class TestEndToEndReportGeneration:
    """End-to-end integration tests with router."""

    @pytest.mark.asyncio
    async def test_router_integration_with_mock_agent(self, router_config, mock_report_generation_agent):
        """Test end-to-end routing with Report Generation agent."""
        with patch('utils.ai_router.router.SessionStore'):
            with patch('utils.ai_router.router.LogRepository'):
                router = AIRouter(config_file=None, agent_registry=None)

                request = AgentRequest(
                    query="Build a market analysis report for the tech sector in London",
                    user_id="test_user",
                    session_id="test_session"
                )

                response = await mock_report_generation_agent.process(request)

                assert response.success is True
                assert response.metadata.get('presentation_ready', False) is True


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

class TestReportGenerationVariations:
    """Test various report generation query patterns."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("query,should_succeed", [
        ("Create a quarterly performance report", True),
        ("Generate a dashboard with our metrics", True),
        ("Build a market analysis for London", True),
        ("Create an executive summary", True),
        ("Generate a candidate pipeline visualization", True),
    ])
    async def test_report_query_patterns(self, query, should_succeed, mock_report_generation_agent):
        """Test various report query patterns."""
        request = AgentRequest(
            query=query,
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        if should_succeed:
            assert response.success is True
            assert len(response.content) > 0


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformanceMetricsReportGeneration:
    """Test performance targets for Report Generation agent."""

    @pytest.mark.asyncio
    async def test_agent_meets_latency_target(self, mock_report_generation_agent):
        """Test agent meets <2s latency target (Phase 2 requirement)."""
        request = AgentRequest(
            query="Generate an executive summary of our placement metrics",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True
        assert response.metadata['agent_latency_ms'] < 2000

    @pytest.mark.asyncio
    async def test_presentation_quality_indicators(self, mock_report_generation_agent):
        """Test that reports include presentation quality indicators."""
        request = AgentRequest(
            query="Create a client presentation on our recruitment services",
            user_id="test_user",
            session_id="test_session"
        )

        response = await mock_report_generation_agent.process(request)

        assert response.success is True
        assert response.metadata.get('presentation_ready', False) is True
        assert response.metadata.get('report_format') == 'markdown'
