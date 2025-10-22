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
from typing import Dict, Any, List
import structlog
from groq import Groq

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category


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

        # Common report types and structures
        self.report_templates = self._load_report_templates()

        # Visualization recommendations
        self.visualization_patterns = self._load_visualization_patterns()

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

            # Generate report
            report_content = await self._generate_report(
                request.query,
                request
            )

            latency_ms = int((time.time() - start_time) * 1000)

            return AgentResponse(
                success=True,
                content=report_content,
                metadata={
                    'agent_latency_ms': latency_ms,
                    'report_format': 'markdown',
                    'presentation_ready': True,
                    'includes_visualizations': self._has_visualizations(report_content)
                }
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
