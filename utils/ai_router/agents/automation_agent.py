"""
Automation Agent - Workflow pipeline design and specification.

Handles automation requests by:
1. Understanding the repetitive process to automate
2. Designing workflow with triggers, actions, conditions
3. Specifying integration points
4. Ensuring implementability (70%+ without modification)

Uses Groq for fast workflow design and specification.
Outputs workflows compatible with n8n, Zapier, Make, etc.
"""

import asyncio
import time
from typing import Dict, Any, List
import json
import structlog
from groq import Groq

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category


logger = structlog.get_logger()


class AutomationAgent(BaseAgent):
    """
    Automation Agent for workflow pipeline design.

    Specializes in:
    - Understanding repetitive business processes
    - Designing structured workflows
    - Specifying triggers, actions, and conditions
    - Creating implementable automation specs
    - Integrations with common platforms (n8n, Zapier, Make)

    Uses Groq llama-3.3-70b-versatile for workflow design and specification.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Automation Agent.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Initialize Groq client
        self.client = Groq()

        # Supported automation platforms
        self.supported_platforms = [
            'n8n',
            'Zapier',
            'Make',
            'Airtable Automations',
            'Google Sheets Script',
            'IFTTT',
            'Integromat'
        ]

        # Common recruitment workflow components
        self.workflow_templates = self._load_workflow_templates()

    def _load_workflow_templates(self) -> Dict[str, List[str]]:
        """
        Load common recruitment workflow templates.

        Returns:
            Dictionary of workflow templates and their components
        """
        return {
            'candidate_onboarding': [
                'Trigger: New candidate registration',
                'Send welcome email',
                'Create profile in ATS',
                'Add to candidate database',
                'Schedule screening call',
                'Log activity'
            ],
            'job_posting_distribution': [
                'Trigger: New job created',
                'Validate job details',
                'Post to job boards',
                'Notify hiring managers',
                'Update tracking sheet',
                'Schedule review'
            ],
            'interview_scheduling': [
                'Trigger: Interview approved',
                'Find available slots',
                'Send calendar invite to candidate',
                'Send reminder to interviewer',
                'Log interview scheduled',
                'Send confirmation'
            ],
            'placement_followup': [
                'Trigger: Placement made',
                'Send placement confirmation',
                'Schedule 30-day check-in',
                'Request feedback from client',
                'Request feedback from candidate',
                'Update placement status',
                'Log outcome metrics'
            ],
            'weekly_reporting': [
                'Trigger: Weekly schedule (e.g., Friday 5pm)',
                'Aggregate placement data',
                'Calculate conversion rates',
                'Identify bottlenecks',
                'Generate report',
                'Send to team',
                'Update dashboards'
            ]
        }

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process workflow automation request.

        Steps:
        1. Validate request
        2. Analyze automation requirements
        3. Design workflow with triggers/actions/conditions
        4. Generate implementable specification
        5. Return structured workflow

        Args:
            request: AgentRequest with automation requirement

        Returns:
            AgentResponse with workflow specification
        """
        start_time = time.time()

        try:
            # Validate request
            if not self.validate_request(request):
                return AgentResponse(
                    success=False,
                    content="",
                    metadata={'agent_latency_ms': int((time.time() - start_time) * 1000)},
                    error="Invalid automation request"
                )

            # Analyze requirements
            automation_spec = await self._generate_workflow_spec(
                request.query,
                request
            )

            latency_ms = int((time.time() - start_time) * 1000)

            return AgentResponse(
                success=True,
                content=automation_spec,
                metadata={
                    'agent_latency_ms': latency_ms,
                    'workflow_type': 'business_process_automation',
                    'implementability_score': self._score_implementability(automation_spec),
                    'supported_platforms': self.supported_platforms[:3]
                }
            )

        except asyncio.TimeoutError:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.warning("automation_timeout", latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error="Workflow design timed out"
            )

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.error("automation_error", error=str(e), latency_ms=latency_ms)
            return AgentResponse(
                success=False,
                content="",
                metadata={'agent_latency_ms': latency_ms},
                error=f"Automation error: {str(e)}"
            )

    async def _generate_workflow_spec(
        self,
        requirement: str,
        request: AgentRequest
    ) -> str:
        """
        Generate detailed workflow specification.

        Args:
            requirement: Automation requirement description
            request: Original agent request

        Returns:
            Structured workflow specification
        """
        prompt = f"""You are an automation workflow designer for recruitment agencies.

AUTOMATION REQUIREMENT:
{requirement}

Please design a complete automation workflow with the following structure:

WORKFLOW NAME:
[Provide a clear, descriptive name]

OBJECTIVE:
[What is this workflow trying to achieve?]

TRIGGER(S):
[What event(s) start this workflow?]
Format each trigger as:
- Trigger Name: [name]
  Source: [system/event]
  Condition: [when exactly does it fire?]

ACTIONS (in sequence):
For each action, specify:
1. Action Name
2. What system/tool performs it
3. Input data needed
4. Output produced
5. Error handling (what if this fails?)

DECISION POINTS:
[Are there conditional branches? List them with conditions]

INTEGRATIONS NEEDED:
[What systems need to talk to each other?]
For each integration:
- System A: [name and what data it sends]
- System B: [name and what data it receives]

ESTIMATED IMPLEMENTABILITY:
[What percentage of this can be automated without custom code?]
- Fully automated: [%]
- Requires minimal customization: [%]
- Requires significant customization: [%]

RECOMMENDED PLATFORMS:
[Which platforms could implement this? (n8n, Zapier, Make, etc)]

POTENTIAL RISKS & MITIGATION:
[What could go wrong and how to prevent it?]

SUCCESS METRICS:
[How will we know this automation is working?]

ESTIMATED TIME SAVINGS:
[How much time does this save per occurrence?]
[How many times per week/month does this run?]
[Annual time savings?]

Make the workflow as detailed and implementable as possible.
Use clear, standard terminology that automation tools use.
Ensure each step is actionable and testable.

Keep response to 600-800 words maximum."""

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
            return self._generate_fallback_workflow(requirement)

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
            max_tokens=1000,
            temperature=0.3  # Lower temperature for structured output
        )

        return message.choices[0].message.content

    def _score_implementability(self, workflow_spec: str) -> float:
        """
        Score the implementability of the workflow.

        Args:
            workflow_spec: Generated workflow specification

        Returns:
            Implementability score (0.0-1.0)
        """
        # Score based on structure and clarity
        score = 0.0

        # Check for key components
        components = [
            ('WORKFLOW NAME', 0.1),
            ('OBJECTIVE', 0.1),
            ('TRIGGER', 0.15),
            ('ACTION', 0.15),
            ('DECISION', 0.1),
            ('INTEGRATIONS', 0.1),
            ('RISKS', 0.1),
            ('METRICS', 0.1),
            ('PLATFORMS', 0.08)
        ]

        for component, weight in components:
            if component.lower() in workflow_spec.lower():
                score += weight

        # Bonus for specific details
        if 'error handling' in workflow_spec.lower():
            score += 0.05

        return min(1.0, score)

    def _generate_fallback_workflow(self, requirement: str) -> str:
        """
        Generate fallback workflow if API fails.

        Args:
            requirement: Automation requirement

        Returns:
            Basic workflow specification
        """
        return f"""WORKFLOW SPECIFICATION

REQUIREMENT:
{requirement}

WORKFLOW DESIGN:

1. IDENTIFY THE TRIGGER
   What event starts this process?
   - User action?
   - Scheduled time?
   - Data change?
   - External trigger?

2. BREAK DOWN THE STEPS
   What are the sequential actions?
   - List each step in order
   - Identify what system does each step
   - Note any conditions or branches

3. DEFINE INTEGRATION POINTS
   What systems need to exchange data?
   - Source system: where data comes from
   - Destination system: where data goes
   - Data format: how to structure the data

4. ADD ERROR HANDLING
   What if something fails?
   - Retry logic?
   - Notification on failure?
   - Fallback actions?

5. SPECIFY OUTPUTS
   What happens at the end?
   - What data is logged?
   - What notifications are sent?
   - How is success confirmed?

IMPLEMENTATION PLATFORMS:
- n8n (open source, self-hosted)
- Zapier (cloud, user-friendly)
- Make (formerly Integromat, powerful)
- IFTTT (simple automations)
- Native platform scripts

NEXT STEPS:
1. Choose target platform based on complexity and cost
2. Create workflow in platform
3. Test with sample data
4. Monitor and refine based on actual usage
5. Document for team knowledge sharing

For detailed workflow design, provide more specific information about:
- Current systems in use
- Data formats and structures
- Required timing and dependencies
- Success and failure conditions"""

    def get_category(self) -> Category:
        """Return the category this agent handles."""
        return Category.AUTOMATION

    def validate_request(self, request: AgentRequest) -> bool:
        """
        Validate request for automation agent.

        Args:
            request: Agent request

        Returns:
            True if valid, False otherwise
        """
        # Call parent validation
        if not super().validate_request(request):
            return False

        # Automation requests should mention workflow or process concepts
        query_lower = request.query.lower()
        automation_indicators = [
            'automate',
            'automation',
            'workflow',
            'schedule',
            'trigger',
            'automatic',
            'every time',
            'whenever',
            'when',
            'process',
            'repetitive',
            'pipeline'
        ]

        if not any(indicator in query_lower for indicator in automation_indicators):
            return False

        return True
