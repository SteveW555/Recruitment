"""
Integration tests for Report Generation Agent with Graph Analysis and SQL Generation.

Tests the new graph suitability analysis and SQL generation capabilities.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from utils.ai_router.agents.report_generation_agent import ReportGenerationAgent
from utils.ai_router.agents.base_agent import AgentRequest, AgentResponse
from utils.ai_router.models.category import Category


@pytest.fixture
def agent_config():
    """Configuration for Report Generation Agent."""
    return {
        'name': 'Report Generation',
        'priority': 3,
        'agent_class': 'utils.ai_router.agents.report_generation_agent:ReportGenerationAgent',
        'llm_provider': 'groq',
        'llm_model': 'llama-3-70b-8192',
        'timeout_seconds': 2,
        'system_prompt': 'You are a report generation specialist with data visualization expertise.',
        'enabled': True
    }


@pytest.fixture
def mock_groq_client():
    """Mock Groq API client."""
    mock_client = Mock()
    mock_completion = Mock()
    mock_choice = Mock()
    mock_message = Mock()

    mock_message.content = "Mock report content"
    mock_choice.message = mock_message
    mock_completion.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_completion

    return mock_client


class TestGraphAnalysis:
    """Test suite for graph suitability analysis."""

    @pytest.mark.asyncio
    async def test_graph_analysis_suitable_query(self, agent_config, mock_groq_client):
        """Test that graph analysis correctly identifies queries suitable for graphing."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        # Mock the graph analysis response
        analysis_response = """{
            "requires_graph": true,
            "reasoning": "Time series data shows trends over 12 months",
            "graph_type": "line",
            "recommended_chart_library": "Plotly",
            "data_description": "Monthly placement counts over last 12 months",
            "sql_query": "SELECT DATE_TRUNC('month', p.start_date) as month, COUNT(*) as placement_count FROM placements p WHERE p.start_date >= NOW() - INTERVAL '12 months' GROUP BY month ORDER BY month ASC",
            "x_axis": "month",
            "y_axis": "placement_count",
            "group_by": null
        }"""

        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = analysis_response

        query = "Show me placement trends over the last 12 months"
        analysis = await agent._analyze_graph_suitability(query)

        assert analysis['requires_graph'] is True
        assert analysis['graph_type'] == 'line'
        assert analysis['sql_query'] is not None
        assert 'placements' in analysis['sql_query'].lower()
        assert analysis['x_axis'] == 'month'
        assert analysis['y_axis'] == 'placement_count'

    @pytest.mark.asyncio
    async def test_graph_analysis_unsuitable_query(self, agent_config, mock_groq_client):
        """Test that graph analysis correctly identifies queries NOT suitable for graphing."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        # Mock the graph analysis response
        analysis_response = """{
            "requires_graph": false,
            "reasoning": "Query requests textual company profile information, not numeric data",
            "graph_type": "none",
            "recommended_chart_library": "none",
            "data_description": "N/A",
            "sql_query": null,
            "x_axis": null,
            "y_axis": null,
            "group_by": null
        }"""

        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = analysis_response

        query = "Create a company profile report for client ABC Corp"
        analysis = await agent._analyze_graph_suitability(query)

        assert analysis['requires_graph'] is False
        assert analysis['graph_type'] == 'none'
        assert analysis['sql_query'] is None

    @pytest.mark.asyncio
    async def test_graph_analysis_bar_chart(self, agent_config, mock_groq_client):
        """Test graph analysis recommends bar chart for comparison data."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        analysis_response = """{
            "requires_graph": true,
            "reasoning": "Comparing revenue across multiple divisions - bar chart ideal",
            "graph_type": "bar",
            "recommended_chart_library": "Recharts",
            "data_description": "Total revenue by division",
            "sql_query": "SELECT cl.industry as division, SUM(p.fee) as total_revenue FROM placements p JOIN clients cl ON p.client_id = cl.id WHERE p.start_date >= NOW() - INTERVAL '3 months' GROUP BY cl.industry ORDER BY total_revenue DESC",
            "x_axis": "division",
            "y_axis": "total_revenue",
            "group_by": "division"
        }"""

        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = analysis_response

        query = "Show revenue by division for the last quarter"
        analysis = await agent._analyze_graph_suitability(query)

        assert analysis['requires_graph'] is True
        assert analysis['graph_type'] == 'bar'
        assert 'total_revenue' in analysis['sql_query'].lower()

    @pytest.mark.asyncio
    async def test_graph_analysis_pie_chart(self, agent_config, mock_groq_client):
        """Test graph analysis recommends pie chart for composition data."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        analysis_response = """{
            "requires_graph": true,
            "reasoning": "Showing composition/distribution of candidates by status - pie chart suitable",
            "graph_type": "pie",
            "recommended_chart_library": "Plotly",
            "data_description": "Candidate distribution by current status",
            "sql_query": "SELECT c.status, COUNT(*) as count FROM candidates c WHERE c.created_at >= NOW() - INTERVAL '6 months' GROUP BY c.status ORDER BY count DESC",
            "x_axis": "status",
            "y_axis": "count",
            "group_by": "status"
        }"""

        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = analysis_response

        query = "Show candidate distribution by status"
        analysis = await agent._analyze_graph_suitability(query)

        assert analysis['requires_graph'] is True
        assert analysis['graph_type'] == 'pie'
        assert 'candidates' in analysis['sql_query'].lower()


class TestSQLGeneration:
    """Test suite for SQL query generation."""

    @pytest.mark.asyncio
    async def test_sql_safety_select_only(self, agent_config, mock_groq_client):
        """Test that generated SQL contains only SELECT statements."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        analysis_response = """{
            "requires_graph": true,
            "reasoning": "Time series analysis",
            "graph_type": "line",
            "recommended_chart_library": "Plotly",
            "data_description": "Monthly job postings",
            "sql_query": "SELECT DATE_TRUNC('month', j.created_at) as month, COUNT(*) as job_count FROM jobs j WHERE j.created_at >= NOW() - INTERVAL '12 months' GROUP BY month ORDER BY month ASC",
            "x_axis": "month",
            "y_axis": "job_count",
            "group_by": null
        }"""

        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = analysis_response

        query = "Show me job posting trends"
        analysis = await agent._analyze_graph_suitability(query)

        sql = analysis['sql_query'].upper()
        assert 'SELECT' in sql
        assert 'INSERT' not in sql
        assert 'UPDATE' not in sql
        assert 'DELETE' not in sql
        assert 'DROP' not in sql

    @pytest.mark.asyncio
    async def test_sql_includes_aggregation(self, agent_config, mock_groq_client):
        """Test that SQL includes proper aggregation functions."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        analysis_response = """{
            "requires_graph": true,
            "reasoning": "Aggregate data comparison",
            "graph_type": "bar",
            "recommended_chart_library": "Chart.js",
            "data_description": "Average salaries by location",
            "sql_query": "SELECT c.location, AVG(c.salary) as avg_salary FROM candidates c WHERE c.salary IS NOT NULL GROUP BY c.location ORDER BY avg_salary DESC LIMIT 10",
            "x_axis": "location",
            "y_axis": "avg_salary",
            "group_by": "location"
        }"""

        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = analysis_response

        query = "Compare average salaries by location"
        analysis = await agent._analyze_graph_suitability(query)

        sql = analysis['sql_query'].upper()
        assert any(agg in sql for agg in ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'])
        assert 'GROUP BY' in sql


class TestEndToEndReportWithGraph:
    """Test complete report generation with graph analysis."""

    @pytest.mark.asyncio
    async def test_report_with_graph_recommendation(self, agent_config, mock_groq_client):
        """Test that report includes graph recommendation when suitable."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        # Mock graph analysis response
        analysis_response = """{
            "requires_graph": true,
            "reasoning": "Time series showing placement trends",
            "graph_type": "line",
            "recommended_chart_library": "Plotly",
            "data_description": "Monthly placement counts for Q4 2024",
            "sql_query": "SELECT DATE_TRUNC('month', p.start_date) as month, COUNT(*) as placements FROM placements p WHERE p.start_date BETWEEN '2024-10-01' AND '2024-12-31' GROUP BY month ORDER BY month ASC",
            "x_axis": "month",
            "y_axis": "placements",
            "group_by": null
        }"""

        # Mock report generation response
        report_response = """# Quarterly Performance Report - Q4 2024

## Executive Summary
Strong performance in Q4 2024 with 120 placements...

## Key Metrics
- Total Placements: 120
- Revenue: £450,000
- Client Satisfaction: 92%"""

        # Set up mock to return different responses for different calls
        mock_groq_client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content=analysis_response))]),  # Graph analysis
            Mock(choices=[Mock(message=Mock(content=report_response))])      # Report generation
        ]

        request = AgentRequest(
            query="Create a quarterly performance report for Q4 2024",
            user_id="test_user",
            session_id="test_session"
        )

        response = await agent.process(request)

        assert response.success is True
        assert '📊 Data Visualization Recommendation' in response.content
        assert 'sql' in response.content.lower()
        assert response.metadata['graph_analysis']['requires_graph'] is True
        assert response.metadata['graph_analysis']['sql_query'] is not None

    @pytest.mark.asyncio
    async def test_report_without_graph_recommendation(self, agent_config, mock_groq_client):
        """Test that report explicitly states no graph when not suitable."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        # Mock graph analysis response - NO GRAPH
        analysis_response = """{
            "requires_graph": false,
            "reasoning": "Textual company profile without numeric trends",
            "graph_type": "none",
            "recommended_chart_library": "none",
            "data_description": "N/A",
            "sql_query": null,
            "x_axis": null,
            "y_axis": null,
            "group_by": null
        }"""

        # Mock report generation response
        report_response = """# Client Profile: ABC Corporation

## Company Overview
ABC Corporation is a leading fintech company..."""

        mock_groq_client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content=analysis_response))]),  # Graph analysis
            Mock(choices=[Mock(message=Mock(content=report_response))])      # Report generation
        ]

        request = AgentRequest(
            query="Create a company profile report for ABC Corp",
            user_id="test_user",
            session_id="test_session"
        )

        response = await agent.process(request)

        assert response.success is True
        assert 'No graph recommended' in response.content
        assert response.metadata['graph_analysis']['requires_graph'] is False


class TestMetadataStructure:
    """Test that metadata is correctly structured."""

    @pytest.mark.asyncio
    async def test_metadata_includes_graph_analysis(self, agent_config, mock_groq_client):
        """Test that response metadata includes complete graph analysis."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        analysis_response = """{
            "requires_graph": true,
            "reasoning": "Comparative analysis",
            "graph_type": "bar",
            "recommended_chart_library": "Recharts",
            "data_description": "Top clients by revenue",
            "sql_query": "SELECT cl.name, SUM(p.fee) as revenue FROM placements p JOIN clients cl ON p.client_id = cl.id GROUP BY cl.name ORDER BY revenue DESC LIMIT 10",
            "x_axis": "name",
            "y_axis": "revenue",
            "group_by": "name"
        }"""

        report_response = "# Report Content"

        mock_groq_client.chat.completions.create.side_effect = [
            Mock(choices=[Mock(message=Mock(content=analysis_response))]),
            Mock(choices=[Mock(message=Mock(content=report_response))])
        ]

        request = AgentRequest(
            query="Show top 10 clients by revenue",
            user_id="test_user",
            session_id="test_session"
        )

        response = await agent.process(request)

        assert 'graph_analysis' in response.metadata
        graph_meta = response.metadata['graph_analysis']

        assert 'requires_graph' in graph_meta
        assert 'graph_type' in graph_meta
        assert 'reasoning' in graph_meta
        assert 'sql_query' in graph_meta
        assert 'x_axis' in graph_meta
        assert 'y_axis' in graph_meta
        assert 'recommended_library' in graph_meta


class TestErrorHandling:
    """Test error handling in graph analysis."""

    @pytest.mark.asyncio
    async def test_graceful_fallback_on_json_error(self, agent_config, mock_groq_client):
        """Test that agent handles malformed JSON gracefully."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        # Return invalid JSON
        invalid_response = "This is not valid JSON at all"

        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = invalid_response

        query = "Create some report"
        analysis = await agent._analyze_graph_suitability(query)

        # Should fallback to no graph
        assert analysis['requires_graph'] is False
        assert 'error' in analysis['reasoning'].lower() or 'parse' in analysis['reasoning'].lower()

    @pytest.mark.asyncio
    async def test_timeout_handling(self, agent_config, mock_groq_client):
        """Test that graph analysis handles API timeout."""
        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        # Simulate timeout
        async def slow_call(*args, **kwargs):
            await asyncio.sleep(5)  # Longer than 2s timeout
            return Mock(choices=[Mock(message=Mock(content="response"))])

        with patch.object(agent, '_call_groq_api_for_analysis', side_effect=lambda x: asyncio.sleep(5)):
            query = "Create report"
            analysis = await agent._analyze_graph_suitability(query)

            # Should fallback to no graph
            assert analysis['requires_graph'] is False
            assert 'timeout' in analysis['reasoning'].lower()


class TestPerformance:
    """Test performance characteristics."""

    @pytest.mark.asyncio
    async def test_graph_analysis_completes_quickly(self, agent_config, mock_groq_client):
        """Test that graph analysis completes within reasonable time."""
        import time

        agent = ReportGenerationAgent(agent_config)
        agent.client = mock_groq_client

        analysis_response = '{"requires_graph": true, "reasoning": "test", "graph_type": "bar", "recommended_chart_library": "Plotly", "data_description": "test", "sql_query": "SELECT 1", "x_axis": "x", "y_axis": "y", "group_by": null}'
        mock_groq_client.chat.completions.create.return_value.choices[0].message.content = analysis_response

        start = time.time()
        query = "Test query"
        await agent._analyze_graph_suitability(query)
        duration = time.time() - start

        # Should complete in under 2 seconds
        assert duration < 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
