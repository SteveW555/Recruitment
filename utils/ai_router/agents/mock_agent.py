"""
Mock Agent - Test implementation of BaseAgent for testing router logic.

Provides a simple agent that returns predictable responses without
calling real LLM APIs, useful for testing router behavior, classification,
and error handling.
"""

import asyncio
import time
from typing import Dict, Any

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from ..models.category import Category


class MockAgent(BaseAgent):
    """
    Mock agent for testing router and agent execution logic.

    Returns configurable mock responses with simulated latency.
    Useful for:
    - Testing router orchestration
    - Validating agent interface compliance
    - Testing retry and fallback logic
    - Performance testing without LLM latency
    """

    def __init__(
        self,
        config: Dict[str, Any],
        mock_response: str = "This is a mock response",
        simulate_latency_ms: int = 100,
        fail_on_attempt: int = -1,  # -1 = never fail, 0 = always fail, 1+ = fail on specific attempt
    ):
        """
        Initialize mock agent.

        Args:
            config: Agent configuration (must include category field)
            mock_response: Response to return
            simulate_latency_ms: Simulated processing time in milliseconds
            fail_on_attempt: Which attempt should fail (-1 = never, 0 = always)
        """
        super().__init__(config)
        self.mock_response = mock_response
        self.simulate_latency_ms = simulate_latency_ms
        self.fail_on_attempt = fail_on_attempt

        # Tracking for testing
        self.call_count = 0
        self.last_request = None
        self.call_history = []

    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process request and return mock response.

        Args:
            request: Agent request

        Returns:
            Mock agent response
        """
        start_time = time.time()
        self.call_count += 1
        self.last_request = request

        # Track call
        self.call_history.append({
            'attempt': request.metadata.get('attempt', 1),
            'query': request.query[:100],
            'timestamp': time.time()
        })

        # Simulate processing latency
        await asyncio.sleep(self.simulate_latency_ms / 1000.0)

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Determine if should fail
        attempt = request.metadata.get('attempt', 1)
        should_fail = (
            (self.fail_on_attempt == 0) or
            (self.fail_on_attempt > 0 and attempt == self.fail_on_attempt)
        )

        if should_fail:
            return AgentResponse(
                success=False,
                content="",
                metadata={
                    'agent_latency_ms': latency_ms,
                    'call_count': self.call_count,
                    'simulated': True
                },
                error=f"Mock agent simulated failure on attempt {attempt}"
            )

        # Return success
        return AgentResponse(
            success=True,
            content=self.mock_response,
            metadata={
                'agent_latency_ms': latency_ms,
                'sources': ['mock_source_1', 'mock_source_2'],
                'call_count': self.call_count,
                'simulated': True,
                'attempts': len(self.call_history)
            }
        )

    def get_category(self) -> Category:
        """
        Return the category this agent handles.

        Returns:
            Category from config
        """
        category_str = self.config.get('category', 'GENERAL_CHAT')
        return Category(category_str)

    def reset(self):
        """Reset call history for testing."""
        self.call_count = 0
        self.last_request = None
        self.call_history = []

    def get_call_history(self) -> list:
        """Get history of all calls for testing."""
        return self.call_history.copy()


def create_mock_agent(
    category: Category,
    mock_response: str = "Mock response",
    simulate_latency_ms: int = 100,
    fail_on_attempt: int = -1
) -> MockAgent:
    """
    Factory function to create a MockAgent easily.

    Args:
        category: Category for the agent
        mock_response: Response to return
        simulate_latency_ms: Simulated latency in milliseconds
        fail_on_attempt: Which attempt should fail

    Returns:
        Configured MockAgent instance
    """
    config = {
        'category': category.value,
        'llm_provider': 'mock',
        'llm_model': 'mock',
        'system_prompt': f'Mock agent for {category.value}',
        'timeout_seconds': 2,
        'enabled': True
    }

    return MockAgent(
        config=config,
        mock_response=mock_response,
        simulate_latency_ms=simulate_latency_ms,
        fail_on_attempt=fail_on_attempt
    )
