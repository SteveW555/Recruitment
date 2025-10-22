"""
Problem Solving Agent - Complex business analysis and recommendations.

Handles strategic problem-solving queries requiring:
1. Multi-step analysis
2. Root cause identification
3. Evidence-based recommendations
4. Industry benchmark cross-referencing

Uses Claude 3.5 Sonnet (Anthropic) for superior reasoning and analysis.
"""

import asyncio
import time
from typing import Dict, Any, List
import structlog
from anthropic import Anthropic

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category


logger = structlog.get_logger()


class ProblemSolvingAgent(BaseAgent):
    """
    Problem Solving Agent for complex business analysis.

    Specializes in:
    - Identifying root causes of business problems
    - Multi-step analysis and decomposition
    - Cross-referencing recruitment industry benchmarks
    - Evidence-based recommendations
    - Actionable solutions

    Uses Claude 3.5 Sonnet for superior reasoning capabilities.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Problem Solving Agent.

        Args:
            config: Agent configuration with llm_provider, llm_model, system_prompt
        """
        super().__init__(config)

        # Initialize Anthropic client
        self.client = Anthropic()

        # Industry benchmarks for recruitment
        self.industry_benchmarks = self._load_industry_benchmarks()

    def _load_industry_benchmarks(self) -> Dict[str, Any]:
        """
        Load UK recruitment industry benchmarks for reference.

        Returns:
            Dictionary with industry benchmarks
        """
        return {
            'placement_rate': {
                'average': 0.65,
                'high_performing': 0.80,
                'low_performing': 0.50,
                'sector': 'UK Recruitment'
            },
            'time_to_hire': {
                'average_days': 23,
                'sales_roles': 18,
                'technical_roles': 28,
                'management_roles': 32
            },
            'candidate_dropout_rate': {
                'average': 0.25,  # 25% typical
                'acceptable': 0.20,
                'concerning': 0.35
            },
            'client_satisfaction': {
                'average_score': 7.8,  # Out of 10
                'target_score': 8.5,
                'high_performing': 9.0
            },
            'fee_recovery_rate': {
                'average': 0.92,  # 92% of expected fees collected
                'good': 0.95,
                'excellent': 0.98
            },
            'salary_growth_trajectory': {
                'junior_to_mid_growth': 0.35,  # 35% increase
                'mid_to_senior_growth': 0.25,  # 25% increase
                'senior_progression': 0.15  # 15% increase
            }
        }

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process complex problem-solving query.

        Steps:
        1. Validate request
        2. Structure analysis prompt with industry context
        3. Call Claude API for deep analysis
        4. Extract and format recommendations
        5. Return structured analysis

        Args:
            request: AgentRequest with problem query and context

        Returns:
            AgentResponse with comprehensive analysis
        """
        start_time = time.time()

        try:
            # Validate request
            if not self.validate_request(request):
                return AgentResponse(
                    success=False,
                    content="",
                    metadata={'agent_latency_ms': int((time.time() - start_time) * 1000)},
                    error="Invalid request"
                )

            # Build analysis prompt with industry context
            analysis_prompt = self._build_analysis_prompt(request.query)

            # Call Claude API for deep analysis
            response = await self._generate_analysis_with_claude(
                analysis_prompt,
                request
            )

            latency_ms = int((time.time() - start_time) * 1000)

            # Extract confidence (Claude tends to be thorough)
            confidence_score = self._estimate_response_quality(response)

            return AgentResponse(
                success=True,
                content=response,
                metadata={
                    'agent_latency_ms': latency_ms,
                    'analysis_depth': 'comprehensive',
                    'confidence': confidence_score,
                    'benchmarks_used': True
                }
            )

        except asyncio.TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.warning("problem_solving_timeout", latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error="Problem solving analysis timed out"
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("problem_solving_error", error=str(e), latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error=f"Problem solving error: {str(e)}"
            )

    def _build_analysis_prompt(self, query: str) -> str:
        """
        Build structured analysis prompt with industry benchmarks.

        Args:
            query: Problem statement from user

        Returns:
            Detailed analysis prompt
        """
        benchmarks_text = self._format_benchmarks_for_context()

        prompt = f"""You are a strategic business consultant specializing in UK recruitment operations.

PROBLEM STATEMENT:
{query}

INDUSTRY CONTEXT & BENCHMARKS:
{benchmarks_text}

Please provide a comprehensive analysis following this structure:

1. PROBLEM DEFINITION
   - What is the core issue?
   - How significant is it (quantify if possible)?
   - What are the immediate impacts?

2. ROOT CAUSE ANALYSIS
   - What are the underlying factors?
   - Is it operational, strategic, market-related, or people-related?
   - Rank likely causes by probability

3. CURRENT STATE ASSESSMENT
   - Compare to industry benchmarks where relevant
   - Identify gaps and opportunities
   - Highlight what's working well

4. STRATEGIC RECOMMENDATIONS
   - What are 3-5 key recommendations to address this problem?
   - For each recommendation:
     * How to implement it
     * Expected impact (quantified where possible)
     * Timeline (short-term: <1 month, medium: 1-3 months, long-term: 3+ months)
     * Resource requirements
     * Potential risks and mitigation

5. SUCCESS METRICS
   - How will you measure improvement?
   - What are realistic targets?
   - What is the success timeframe?

6. IMPLEMENTATION ROADMAP
   - Quick wins (immediate actions, 0-2 weeks)
   - Phase 1 (weeks 2-4)
   - Phase 2 (weeks 5-12)
   - Long-term (3+ months)

Ensure your analysis is:
- Evidence-based and grounded in recruitment industry best practices
- Specific to UK context where relevant
- Actionable with clear next steps
- Realistic about timelines and resources
- Focused on measurable outcomes

Keep the response to 800-1000 words maximum."""

        return prompt

    def _format_benchmarks_for_context(self) -> str:
        """
        Format industry benchmarks for inclusion in prompt.

        Returns:
            Formatted benchmarks text
        """
        return """
UK RECRUITMENT INDUSTRY BENCHMARKS:

Placement Rate:
  - Industry Average: 65%
  - High Performing: 80%+
  - Concerning: Below 50%

Time-to-Hire (by role type):
  - Sales Roles: 18 days
  - Technical Roles: 28 days
  - Management Roles: 32 days
  - Overall Average: 23 days

Candidate Dropout Rate:
  - Acceptable: ~20%
  - Industry Average: ~25%
  - Concerning: 35%+

Client Satisfaction:
  - Industry Average: 7.8/10
  - Target (good agency): 8.5/10
  - High Performing: 9.0/10

Fee Recovery Rate:
  - Average: 92%
  - Good: 95%+
  - Excellent: 98%+

Salary Growth Expectations:
  - Junior to Mid-level: 35% increase
  - Mid to Senior: 25% increase
  - Senior Progression: 15% increase
"""

    async def _generate_analysis_with_claude(
        self,
        prompt: str,
        request: AgentRequest
    ) -> str:
        """
        Generate comprehensive analysis using Claude API.

        Args:
            prompt: Analysis prompt
            request: Original agent request

        Returns:
            Comprehensive analysis text
        """
        try:
            message = await asyncio.wait_for(
                asyncio.to_thread(
                    self._call_claude_api,
                    prompt
                ),
                timeout=self.timeout - 0.5
            )

            return message

        except asyncio.TimeoutError:
            logger.error("claude_api_timeout")
            return self._generate_fallback_analysis(request.query)

        except Exception as e:
            logger.error("claude_api_error", error=str(e))
            return self._generate_fallback_analysis(request.query)

    def _call_claude_api(self, prompt: str) -> str:
        """
        Call Claude API synchronously.

        Args:
            prompt: Prompt for Claude

        Returns:
            Response from Claude
        """
        message = self.client.messages.create(
            model=self.llm_model,
            max_tokens=2000,
            system=self.system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return message.content[0].text

    def _estimate_response_quality(self, response: str) -> float:
        """
        Estimate quality/confidence of the analysis.

        Args:
            response: Generated analysis

        Returns:
            Confidence score (0.0-1.0)
        """
        # Simple heuristic: look for structured analysis markers
        quality_indicators = [
            'root cause',
            'recommendation',
            'timeline',
            'metric',
            'implementation',
            'impact'
        ]

        found_indicators = sum(
            1 for indicator in quality_indicators
            if indicator.lower() in response.lower()
        )

        # Base score on number of quality indicators found
        confidence = min(0.95, 0.7 + (found_indicators * 0.05))

        return confidence

    def _generate_fallback_analysis(self, problem: str) -> str:
        """
        Generate fallback analysis if Claude API fails.

        Args:
            problem: Problem statement

        Returns:
            Basic analysis structure
        """
        return f"""PROBLEM ANALYSIS

Problem: {problem}

ROOT CAUSE ANALYSIS:
Based on the problem statement, potential root causes may include:
- Operational inefficiencies in current processes
- Resource constraints or skill gaps
- Market or external factors
- Strategic misalignment

RECOMMENDATIONS:
1. Assess current state - Conduct interviews, data analysis
2. Identify gaps - Compare to industry benchmarks
3. Develop strategy - Create actionable improvement plan
4. Execute in phases - Quick wins first, then medium/long-term
5. Measure results - Track KPIs and adjust as needed

NEXT STEPS:
- Schedule discovery session to understand problem deeper
- Gather relevant data and metrics
- Benchmark against industry standards
- Develop detailed implementation roadmap

For comprehensive analysis, please work with a strategic consultant who can review your specific data and market context.
"""

    def get_category(self) -> Category:
        """Return the category this agent handles."""
        return Category.PROBLEM_SOLVING

    def validate_request(self, request: AgentRequest) -> bool:
        """
        Validate request for problem solving agent.

        Args:
            request: Agent request

        Returns:
            True if valid, False otherwise
        """
        # Call parent validation
        if not super().validate_request(request):
            return False

        # Problem solving requires substantial query
        if len(request.query.strip()) < 20:
            return False

        # Should sound like a problem/question
        query_lower = request.query.lower()
        problem_indicators = ['how', 'why', 'what', 'can', 'should', 'could', 'problem', 'issue']
        if not any(indicator in query_lower for indicator in problem_indicators):
            return False

        return True
