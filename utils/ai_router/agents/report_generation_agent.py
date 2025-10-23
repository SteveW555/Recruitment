"""
Report Generation Agent - Visualization and presentation report creation.

Handles report generation requests by:
1. Understanding data requirements and scope
2. Designing report structure with sections and visualizations
3. Creating markdown-formatted reports with suggestions for charts/tables
4. Providing presentation-ready output suitable for stakeholders

Uses Groq for fast report design and content generation.
Outputs reports in markdown with visualization guidance for tools like Tableau, PowerBI, etc.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
import structlog
from groq import Groq
import pandas as pd
from pathlib import Path

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category
from ..visualization.chart_generator import ChartGenerator


logger = structlog.get_logger()


class ReportGenerationAgent(BaseAgent):
    """
    Report Generation Agent for creating presentation reports.

    Specializes in:
    - Understanding reporting requirements and data scope
    - Designing report structure with sections and insights
    - Suggesting appropriate visualizations (charts, tables, dashboards)
    - Creating markdown-formatted reports
    - Ensuring presentation quality and professional appearance

    Uses Groq llama-3-70b-8192 for fast report generation.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Report Generation Agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Initialize Groq client
        self.client = Groq()

        # Initialize Chart Generator
        self.chart_generator = ChartGenerator(output_dir="./generated_charts")

        # Common report types and structures
        self.report_templates = self._load_report_templates()

        # Visualization recommendations
        self.visualization_patterns = self._load_visualization_patterns()

        # Data source paths
        self.data_sources = {
            'advertising': 'finance_test_data/financial_records/11_job_board_advertising.csv',
            'job_board': 'finance_test_data/financial_records/11_job_board_advertising.csv'
        }

    def _load_report_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load common recruitment report templates.

        Returns:
            Dictionary of report templates with sections and guidance
        """
        return {
            'quarterly_performance': {
                'sections': [
                    'Executive Summary',
                    'Key Metrics',
                    'Placements Overview',
                    'Revenue Analysis',
                    'Candidate Pipeline',
                    'Client Satisfaction',
                    'Challenges & Opportunities',
                    'Next Quarter Outlook'
                ],
                'visualizations': [
                    'Placement trend line chart',
                    'Revenue pie chart by division',
                    'Pipeline funnel visualization',
                    'Client satisfaction gauge'
                ]
            },
            'division_performance': {
                'sections': [
                    'Division Overview',
                    'Performance Metrics',
                    'Placement Details',
                    'Top Clients',
                    'Top Placements',
                    'Staff Performance',
                    'Key Achievements',
                    'Improvement Areas'
                ],
                'visualizations': [
                    'KPI dashboard',
                    'Placement success rate gauge',
                    'Top clients bar chart',
                    'Staff performance comparison'
                ]
            },
            'market_analysis': {
                'sections': [
                    'Market Overview',
                    'Sector Trends',
                    'Salary Benchmarks',
                    'Demand Analysis',
                    'Competitive Landscape',
                    'Skills in Demand',
                    'Market Opportunities',
                    'Recommendations'
                ],
                'visualizations': [
                    'Market size trend chart',
                    'Sector distribution pie chart',
                    'Salary band distribution',
                    'Skills demand heatmap'
                ]
            },
            'candidate_pipeline': {
                'sections': [
                    'Pipeline Summary',
                    'Stage Distribution',
                    'Conversion Metrics',
                    'Dropout Analysis',
                    'Time-to-Hire',
                    'Quality Metrics',
                    'Bottlenecks',
                    'Optimization Recommendations'
                ],
                'visualizations': [
                    'Pipeline funnel chart',
                    'Stage duration timeline',
                    'Conversion rate by stage',
                    'Bottleneck identification'
                ]
            },
            'executive_summary': {
                'sections': [
                    'Highlights',
                    'Key Metrics',
                    'Performance vs Target',
                    'Major Achievements',
                    'Challenges',
                    'Strategic Focus',
                    'Next Steps'
                ],
                'visualizations': [
                    'KPI scorecard',
                    'Performance gauge charts',
                    'Achievement highlights',
                    'Target vs actual comparison'
                ]
            }
        }

    def _load_visualization_patterns(self) -> Dict[str, List[str]]:
        """
        Load visualization recommendations for different data types.

        Returns:
            Dictionary mapping data types to recommended visualizations
        """
        return {
            'trends_over_time': [
                'Line chart (best)',
                'Area chart (filled)',
                'Bar chart (if discrete periods)',
                'Combination chart (trend + actuals)'
            ],
            'comparison': [
                'Bar chart (horizontal or vertical)',
                'Grouped bar chart (multiple comparisons)',
                'Box plot (distribution)',
                'Radar chart (many dimensions)'
            ],
            'composition': [
                'Pie chart (simple, clear breakdown)',
                'Donut chart (variation)',
                'Stacked bar chart (multiple compositions)',
                'Treemap (hierarchical)'
            ],
            'distribution': [
                'Histogram (frequency distribution)',
                'Box plot (quartiles and outliers)',
                'Scatter plot (with density)',
                'Violin plot (shape and density)'
            ],
            'relationships': [
                'Scatter plot (X-Y relationship)',
                'Bubble chart (3+ variables)',
                'Heatmap (correlation)',
                'Network graph (connections)'
            ],
            'proportions': [
                'Gauge chart (single KPI)',
                'Progress bar (vs target)',
                'Bullet chart (performance)',
                'Waterfall chart (cumulative change)'
            ]
        }

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process report generation request.

        Steps:
        1. Validate request
        2. Identify report type and requirements
        3. Design report structure with sections and visualizations
        4. Generate markdown-formatted report
        5. Return presentation-ready content

        Args:
            request: AgentRequest with report requirement

        Returns:
            AgentResponse with report content
        """
        start_time = time.time()

        try:
            # Validate request
            if not self.validate_request(request):
                return AgentResponse(
                    success=False,
                    content="",
                    metadata={'agent_latency_ms': int((time.time() - start_time) * 1000)},
                    error="Invalid report request"
                )

            # Check if we should generate charts
            charts = await self._generate_charts_if_needed(request.query)

            # Generate report text
            report_content = await self._generate_report(
                request.query,
                request
            )

            # Embed chart references if charts were generated
            if charts:
                report_content = self._embed_chart_references(report_content, charts)

            latency_ms = int((time.time() - start_time) * 1000)

            # Get graph analysis from request if available
            graph_analysis = getattr(request, '_graph_analysis', None)

            metadata = {
                'agent_latency_ms': latency_ms,
                'report_format': 'markdown',
                'presentation_ready': True,
                'includes_visualizations': self._has_visualizations(report_content)
            }

            if charts:
                metadata['charts'] = charts
                metadata['chart_count'] = len(charts)

            # Add graph analysis to metadata
            if graph_analysis:
                metadata['graph_analysis'] = {
                    'requires_graph': graph_analysis.get('requires_graph', False),
                    'graph_type': graph_analysis.get('graph_type'),
                    'reasoning': graph_analysis.get('reasoning'),
                    'recommended_library': graph_analysis.get('recommended_chart_library'),
                    'data_description': graph_analysis.get('data_description'),
                    'sql_query': graph_analysis.get('sql_query'),
                    'x_axis': graph_analysis.get('x_axis'),
                    'y_axis': graph_analysis.get('y_axis'),
                    'group_by': graph_analysis.get('group_by')
                }

                # Add human-readable message to content if graph is appropriate
                if graph_analysis.get('requires_graph') and graph_analysis.get('sql_query'):
                    graph_section = f"""

---

## 📊 Data Visualization Recommendation

**Graph Type:** {graph_analysis.get('graph_type', 'N/A')}
**Library:** {graph_analysis.get('recommended_chart_library', 'N/A')}
**Data:** {graph_analysis.get('data_description', 'N/A')}

**SQL Query for Data Extraction:**
```sql
{graph_analysis.get('sql_query')}
```

**Chart Configuration:**
- X-Axis: {graph_analysis.get('x_axis', 'N/A')}
- Y-Axis: {graph_analysis.get('y_axis', 'N/A')}
- Grouping: {graph_analysis.get('group_by', 'None')}

**Reasoning:** {graph_analysis.get('reasoning', 'N/A')}

*Note: The SQL query above can be executed against the database to retrieve the data needed for visualization.*
"""
                    report_content += graph_section
                elif not graph_analysis.get('requires_graph'):
                    # Explicitly state no graph is recommended
                    no_graph_section = f"""

---

## 📊 Visualization Assessment

**No graph recommended** - {graph_analysis.get('reasoning', 'This report is better suited for textual presentation.')}
"""
                    report_content += no_graph_section

            return AgentResponse(
                success=True,
                content=report_content,
                metadata=metadata
            )

        except asyncio.TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.warning("report_generation_timeout", latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error="Report generation timed out"
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("report_generation_error", error=str(e), latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error=f"Report generation error: {str(e)}"
            )

    async def _generate_charts_if_needed(self, query: str) -> Optional[List[Dict[str, Any]]]:
        """
        Detect if query requires charts and generate them.

        Args:
            query: User query

        Returns:
            List of chart metadata dicts, or None if no charts needed
        """
        query_lower = query.lower()
        charts = []

        try:
            # Advertising/Job Board Reports
            if any(keyword in query_lower for keyword in ['advertising', 'job board', 'ad spend', 'marketing cost']):
                csv_path = Path(self.data_sources.get('advertising', ''))

                if not csv_path.exists():
                    logger.warning("data_source_not_found", path=str(csv_path))
                    return None

                # Load data
                df = pd.read_csv(csv_path)
                df['expense_date'] = pd.to_datetime(df['expense_date'])

                # Chart 1: Costs by job board (bar chart)
                costs_by_board = df.groupby('job_board')['amount'].sum().reset_index()
                costs_by_board = costs_by_board.sort_values('amount', ascending=False)

                chart1 = self.chart_generator.bar_chart(
                    data=costs_by_board,
                    x_column='job_board',
                    y_column='amount',
                    title='Total Advertising Costs by Job Board (2024)',
                    output_filename='advertising_costs_by_board'
                )
                charts.append(chart1)

                # Chart 2: Monthly trend (line chart)
                df['month'] = df['expense_date'].dt.to_period('M').astype(str)
                monthly_costs = df.groupby('month')['amount'].sum().reset_index()

                chart2 = self.chart_generator.line_chart(
                    data=monthly_costs,
                    x_column='month',
                    y_column='amount',
                    title='Monthly Advertising Spend Trend (2024)',
                    output_filename='advertising_monthly_trend'
                )
                charts.append(chart2)

                # Chart 3: Cost distribution (pie chart)
                chart3 = self.chart_generator.pie_chart(
                    data=costs_by_board,
                    names_column='job_board',
                    values_column='amount',
                    title='Advertising Cost Distribution by Platform (2024)',
                    output_filename='advertising_cost_distribution'
                )
                charts.append(chart3)

                logger.info("charts_generated", count=len(charts), type="advertising")

            return charts if charts else None

        except Exception as e:
            logger.error("chart_generation_failed", error=str(e))
            return None

    def _embed_chart_references(self, report: str, charts: List[Dict[str, Any]]) -> str:
        """
        Embed chart references into the markdown report.

        Args:
            report: Original markdown report
            charts: List of chart metadata dicts

        Returns:
            Enhanced report with chart embeddings
        """
        chart_section = "\n\n## 📊 Interactive Visualizations\n\n"
        chart_section += "*The following interactive charts have been generated. Click the links to view them in your browser with zoom, hover, and pan capabilities.*\n\n"

        for i, chart in enumerate(charts, 1):
            chart_section += f"### {i}. {chart['title']}\n\n"

            # Add HTML link
            chart_section += f"**[🔗 View Interactive Chart]({chart['html_path']})** (opens in browser)\n\n"

            # Add PNG link if available
            if chart.get('png_path'):
                chart_section += f"**[📥 Download PNG]({chart['png_path']})** (static image)\n\n"

            # Add description based on chart type
            if chart['type'] == 'bar':
                chart_section += "*Bar chart showing comparison across categories*\n\n"
            elif chart['type'] == 'line':
                chart_section += "*Line chart showing trends over time*\n\n"
            elif chart['type'] == 'pie':
                chart_section += "*Pie chart showing composition and distribution*\n\n"

        # Try to insert after Executive Summary
        parts = report.split('## Key Metrics', 1)
        if len(parts) == 2:
            return parts[0] + chart_section + '## Key Metrics' + parts[1]
        else:
            # Append at the end if no Key Metrics section found
            return report + "\n\n---\n" + chart_section

    async def _analyze_graph_suitability(self, query: str) -> Dict[str, Any]:
        """
        Analyze if the query would benefit from graphed data and generate SQL.

        Args:
            query: User's report query

        Returns:
            Dictionary with graph analysis results
        """
        analysis_prompt = f"""Analyze this report request to determine if it would benefit from graphical data visualization:

QUERY: {query}

Available database tables:
- candidates: candidate information, skills, status, registration dates, salaries, locations
- jobs: job postings, titles, salaries, locations, statuses, client associations, dates
- clients: client companies, industries, locations, account status, relationships
- placements: successful placements linking candidates to jobs, start dates, fees, durations
- applications: job applications, status, dates, candidate-job relationships
- interviews: interview records, dates, outcomes, feedback

Analyze the query and respond with a JSON object:
{{
  "requires_graph": true/false,
  "reasoning": "Brief explanation of why graph is/isn't suitable",
  "graph_type": "line/bar/pie/scatter/heatmap/none",
  "recommended_chart_library": "Plotly/Recharts/Chart.js/none",
  "data_description": "What data should be graphed",
  "sql_query": "PostgreSQL SELECT statement to extract the data OR null if no graph",
  "x_axis": "Column name for X-axis OR null",
  "y_axis": "Column name for Y-axis OR null",
  "group_by": "Column name for grouping/segmentation OR null"
}}

Guidelines:
- Graphs are suitable for: trends over time, comparisons, distributions, compositions, relationships
- Graphs are NOT suitable for: single values, text-heavy reports, non-numeric data
- SQL should be PostgreSQL compatible, safe (SELECT only), and efficient
- Use table aliases (c for candidates, j for jobs, cl for clients, p for placements)
- Include WHERE clauses for date ranges if relevant (e.g., last 12 months)
- Aggregate data appropriately (COUNT, SUM, AVG, etc.)
- Order results meaningfully (DESC for top performers, ASC for time series)

Return ONLY the JSON object, no other text."""

        try:
            message = await asyncio.wait_for(
                asyncio.to_thread(
                    self._call_groq_api_for_analysis,
                    analysis_prompt
                ),
                timeout=2.0
            )

            # Parse JSON response
            import json
            # Clean response - extract JSON if wrapped in markdown
            if '```json' in message:
                message = message.split('```json')[1].split('```')[0].strip()
            elif '```' in message:
                message = message.split('```')[1].split('```')[0].strip()

            analysis = json.loads(message.strip())

            # Validate required fields
            if 'requires_graph' not in analysis:
                logger.warning("graph_analysis_missing_field", field="requires_graph")
                return {"requires_graph": False, "reasoning": "Analysis failed"}

            logger.info("graph_analysis_complete",
                       requires_graph=analysis.get('requires_graph'),
                       graph_type=analysis.get('graph_type'))

            return analysis

        except asyncio.TimeoutError:
            logger.warning("graph_analysis_timeout")
            return {"requires_graph": False, "reasoning": "Analysis timeout"}
        except json.JSONDecodeError as e:
            logger.error("graph_analysis_json_error", error=str(e), response=message[:200])
            return {"requires_graph": False, "reasoning": "JSON parse error"}
        except Exception as e:
            logger.error("graph_analysis_error", error=str(e))
            return {"requires_graph": False, "reasoning": f"Analysis error: {str(e)}"}

    def _call_groq_api_for_analysis(self, prompt: str) -> str:
        """
        Call Groq API for graph analysis (synchronous).

        Args:
            prompt: Analysis prompt

        Returns:
            JSON response from Groq
        """
        message = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a data visualization expert. Analyze queries and determine optimal graph types and data extraction SQL. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self.llm_model,
            max_tokens=800,
            temperature=0.3  # Low temperature for structured output
        )

        return message.choices[0].message.content

    async def _generate_report(
        self,
        requirement: str,
        request: AgentRequest
    ) -> str:
        """
        Generate structured report with visualizations.

        Args:
            requirement: Report requirement description
            request: Original agent request

        Returns:
            Markdown-formatted report content
        """
        # First, analyze graph suitability
        graph_analysis = await self._analyze_graph_suitability(requirement)

        # Store analysis in request metadata for later use
        if not hasattr(request, '_graph_analysis'):
            request._graph_analysis = graph_analysis

        prompt = f"""You are a professional report designer for a UK recruitment agency.

REPORT REQUIREMENT:
{requirement}

Please create a professional, presentation-ready report with the following structure:

1. TITLE & EXECUTIVE SUMMARY
   - Clear title
   - 2-3 sentence executive summary with key insights
   - Report date and prepared for

2. KEY METRICS (Dashboard)
   - 3-5 most important KPIs
   - Format as: **Metric Name**: Value (with context/trend)
   - Example: **Total Placements**: 45 (↑ 15% vs previous quarter)

3. DETAILED FINDINGS (2-3 sections)
   - Each section with:
     * Clear heading
     * 2-3 paragraphs of analysis
     * Key insights highlighted
     * Recommendations where applicable
   - Include data-driven insights and observations

4. VISUALIZATION SUGGESTIONS
   - For each major data set, suggest a chart type:
     * Chart Type: [e.g., "Line Chart"]
     * Data: [e.g., "Placement trend over 12 months"]
     * Tool: [e.g., "Use Tableau, PowerBI, or Excel"]
   - Format as: `📊 [Chart Type]: [Description]`

5. DATA TABLES (where helpful)
   - Format key data in markdown tables
   - Clear column headers
   - Sort by most important values

6. KEY INSIGHTS (Bullet points)
   - 5-7 most important findings
   - Format: "• [Insight with quantified impact]"

7. RECOMMENDATIONS
   - 3-5 actionable recommendations
   - Each with: Action, Expected Impact, Timeline
   - Format as numbered list

8. CONCLUSION & NEXT STEPS
   - Summary of key findings
   - Immediate next steps
   - Follow-up actions and timeline

FORMATTING GUIDELINES:
- Use markdown formatting for professional appearance
- Use **bold** for emphasis on key metrics
- Use [brackets] for chart/visualization suggestions
- Keep paragraphs concise (2-3 sentences max)
- Use bullet points for lists
- Include data where relevant and realistic

VISUALIZATION RECOMMENDATIONS:
For trends: Use line charts
For comparisons: Use bar charts
For composition: Use pie/donut charts
For status: Use gauge charts or KPI cards
For performance: Use bullet charts

Make the report:
- Professional and presentation-ready
- Data-driven with specific numbers
- Actionable with clear recommendations
- Suitable for C-level stakeholder review
- Implementable insights

Keep response to 1000-1200 words maximum."""

        try:
            message = await asyncio.wait_for(
                asyncio.to_thread(
                    self._call_groq_api,
                    prompt
                ),
                timeout=self.timeout - 0.5
            )

            return message

        except Exception as e:
            logger.error("groq_api_error", error=str(e))
            return self._generate_fallback_report(requirement)

    def _call_groq_api(self, prompt: str) -> str:
        """
        Call Groq API synchronously.

        Args:
            prompt: Prompt for Groq

        Returns:
            Response from Groq
        """
        message = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=self.llm_model,
            max_tokens=1500,
            temperature=0.5  # Balanced for both structure and content
        )

        return message.choices[0].message.content

    def _has_visualizations(self, report_content: str) -> bool:
        """
        Check if report includes visualization suggestions.

        Args:
            report_content: Generated report content

        Returns:
            True if visualizations are suggested, False otherwise
        """
        visualization_keywords = ['chart', 'graph', '📊', 'visualization', 'dashboard', 'table']
        content_lower = report_content.lower()
        return any(keyword in content_lower for keyword in visualization_keywords)

    def _generate_fallback_report(self, requirement: str) -> str:
        """
        Generate fallback report if API fails.

        Args:
            requirement: Report requirement

        Returns:
            Basic structured report
        """
        return f"""# Report Generation

## Executive Summary

This report addresses your request: {requirement}

The analysis below provides key metrics, findings, and recommendations for stakeholder review.

---

## Key Metrics Dashboard

| Metric | Value | Status |
|--------|-------|--------|
| Overall Performance | Pending Data | — |
| Key Achievement 1 | To be calculated | — |
| Key Achievement 2 | To be calculated | — |
| Key Achievement 3 | To be calculated | — |

---

## Detailed Analysis

### Finding 1: Current State Assessment
To provide accurate analysis, we recommend gathering the following data:
- Current operational metrics
- Historical performance trends
- Comparative benchmarks
- Resource allocation details

### Finding 2: Key Insights
- Insight based on provided requirements
- Areas of strength and opportunity
- Relevant market context
- Stakeholder implications

### Finding 3: Performance Drivers
- Contributing factors to current performance
- Market influences
- Internal operational factors
- Strategic alignment

---

## Visualization Recommendations

📊 **Line Chart**: Show key metrics trends over time
📊 **Bar Chart**: Compare performance across divisions or periods
📊 **Pie Chart**: Show composition of key categories
📊 **KPI Dashboard**: Display critical metrics at a glance

---

## Key Insights

• Performance metrics indicate areas for targeted improvement
• Market conditions present both challenges and opportunities
• Operational efficiency can be optimized through focused initiatives
• Stakeholder engagement and communication are critical

---

## Recommendations

1. **Gather Complete Data**: Collect comprehensive metrics for detailed analysis
2. **Define Success Criteria**: Establish clear targets for next period
3. **Implement Monitoring**: Set up dashboards for ongoing performance tracking
4. **Stakeholder Communication**: Share findings and align on priorities
5. **Action Planning**: Create detailed implementation roadmap

---

## Conclusion

To provide a comprehensive, data-driven report with specific insights and recommendations, please provide:
- Specific performance data
- Historical trends
- Division/department breakdown
- Comparative benchmarks

Once data is provided, a detailed report with actionable recommendations will be generated.

---

**Next Steps**: Share data specifications and we'll create a detailed, presentation-ready report."""

    def get_category(self) -> Category:
        """Return the category this agent handles."""
        return Category.REPORT_GENERATION

    def validate_request(self, request: AgentRequest) -> bool:
        """
        Validate request for report generation agent.

        Args:
            request: Agent request

        Returns:
            True if valid, False otherwise
        """
        # Call parent validation
        if not super().validate_request(request):
            return False

        # Report requests should mention report, dashboard, analysis, or presentation concepts
        query_lower = request.query.lower()
        report_indicators = [
            'report',
            'dashboard',
            'analysis',
            'presentation',
            'visualize',
            'visualization',
            'summary',
            'chart',
            'graph',
            'data breakdown',
            'performance review',
            'metrics'
        ]

        if not any(indicator in query_lower for indicator in report_indicators):
            return False

        return True
