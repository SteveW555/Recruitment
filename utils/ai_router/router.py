"""
AI Router - Main query routing orchestration.

Routes user queries to specialized agent handlers based on semantic classification.
Manages session context, handles retries, and logs all routing decisions.
"""

import asyncio
import time
from typing import Optional, Dict, Any
from datetime import datetime

from .models.query import Query
from .models.routing_decision import RoutingDecision
from .models.session_context import SessionContext
from .models.category import Category
from .classifier import Classifier
from .storage.session_store import SessionStore
from .storage.log_repository import LogRepository
from .agent_registry import AgentRegistry
from .agents.base_agent import AgentRequest, AgentResponse


class AIRouter:
    """
    Main AI routing orchestrator.

    Responsibilities:
    1. Validate incoming queries (truncate if >1000 words)
    2. Manage session context (load/save from Redis)
    3. Classify queries using Classifier
    4. Route to appropriate agent
    5. Handle retries and fallback logic
    6. Log all decisions to PostgreSQL
    7. Implement graceful error handling

    Performance targets:
    - End-to-end latency: <3 seconds (95th percentile)
    - Agent timeout: 2 seconds with 1 retry
    """

    def __init__(
        self,
        classifier: Classifier,
        session_store: SessionStore,
        log_repository: Optional[LogRepository],
        agent_registry: AgentRegistry,
        confidence_threshold: float = 0.7,
        agent_timeout: float = 2.0,
        max_retries: int = 1,
        retry_delay_ms: int = 500,
    ):
        """
        Initialize router with dependencies.

        Args:
            classifier: Classifier for query classification
            session_store: Redis session storage
            log_repository: PostgreSQL log repository (optional - None disables logging)
            agent_registry: Agent registry for loading agents
            confidence_threshold: Minimum confidence for routing (default 0.7)
            agent_timeout: Agent execution timeout in seconds (default 2)
            max_retries: Maximum retries for agent execution (default 1)
            retry_delay_ms: Delay between retries in ms (default 500)
        """
        self.classifier = classifier
        self.session_store = session_store
        self.log_repository = log_repository
        self.agent_registry = agent_registry
        self.confidence_threshold = confidence_threshold
        self.agent_timeout = agent_timeout
        self.max_retries = max_retries
        self.retry_delay_ms = retry_delay_ms

    async def route(
        self,
        query_text: str,
        user_id: str,
        session_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route a query to the appropriate agent.

        Main public API for the router. Handles full routing pipeline:
        1. Validate query
        2. Load session context
        3. Classify query
        4. Route to agent or trigger clarification
        5. Execute agent with retry logic
        6. Log decision

        Args:
            query_text: User's query (will be truncated to 1000 words)
            user_id: Authenticated user ID
            session_id: Session UUID for context continuity
            **kwargs: Additional metadata (timestamps, request_id, etc.)

        Returns:
            Dictionary with routing result:
            {
                'success': bool,
                'query': Query,
                'decision': RoutingDecision,
                'agent_response': Optional[AgentResponse],
                'error': Optional[str],
                'latency_ms': int
            }
        """
        start_time = time.time()

        try:
            # Step 1: Validate and create Query
            query = Query(
                text=query_text,
                user_id=user_id,
                session_id=session_id
            )

            # Step 2: Load session context
            session_context = self.session_store.load(user_id, session_id)
            if not session_context:
                session_context = SessionContext(
                    user_id=user_id,
                    session_id=session_id
                )

            # Step 3: Classify query
            decision = self.classifier.classify(query.text, query.id)

            # Step 4: Check confidence and route
            if decision.primary_confidence < self.confidence_threshold:
                # Low confidence - trigger clarification
                result = {
                    'success': False,
                    'query': query,
                    'decision': decision,
                    'agent_response': None,
                    'error': f"Query confidence {decision.primary_confidence:.1%} below threshold {self.confidence_threshold:.0%}. Please clarify your request.",
                    'latency_ms': int((time.time() - start_time) * 1000)
                }

                # Log decision (if logging enabled)
                if self.log_repository:
                    self.log_repository.log_routing_decision(
                        query, decision, False,
                        error_message=result['error']
                    )

                return result

            # Step 5: Get agent and execute
            agent = self.agent_registry.get_agent(decision.primary_category)

            if not agent:
                error_msg = f"No agent available for {decision.primary_category.value}"
                result = {
                    'success': False,
                    'query': query,
                    'decision': decision,
                    'agent_response': None,
                    'error': error_msg,
                    'latency_ms': int((time.time() - start_time) * 1000)
                }

                # Log decision (if logging enabled)
                if self.log_repository:
                    self.log_repository.log_routing_decision(
                        query, decision, False,
                        error_message=error_msg
                    )

                return result

            # Step 6: Execute agent with retry logic
            agent_response = await self._execute_agent_with_retry(
                agent, query, session_context
            )

            # Step 7: Handle agent failure - fallback to general chat
            if not agent_response.success:
                fallback_response = await self._fallback_to_general_chat(
                    query, session_context, agent_response
                )
                decision.fallback_triggered = True

                result = {
                    'success': fallback_response.success,
                    'query': query,
                    'decision': decision,
                    'agent_response': fallback_response,
                    'error': None if fallback_response.success else fallback_response.error,
                    'latency_ms': int((time.time() - start_time) * 1000)
                }
            else:
                result = {
                    'success': True,
                    'query': query,
                    'decision': decision,
                    'agent_response': agent_response,
                    'error': None,
                    'latency_ms': int((time.time() - start_time) * 1000)
                }

            # Step 8: Save/update session context
            session_context.add_message(user_id, query_text)
            session_context.add_routing_history(decision.primary_category.value, decision.primary_confidence)
            self.session_store.save(session_context)

            # Step 9: Log decision (if logging enabled)
            if self.log_repository:
                agent_latency = None
                if agent_response and agent_response.metadata:
                    agent_latency = agent_response.metadata.get('agent_latency_ms')

                self.log_repository.log_routing_decision(
                    query, decision,
                    agent_success=agent_response.success if agent_response else False,
                    agent_latency_ms=agent_latency,
                    error_message=result.get('error')
                )

            return result

        except Exception as e:
            # Unhandled exception - return error result
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                'success': False,
                'query': None,
                'decision': None,
                'agent_response': None,
                'error': f"Router error: {str(e)}",
                'latency_ms': latency_ms
            }

    async def _execute_agent_with_retry(
        self,
        agent,
        query: Query,
        session_context: SessionContext
    ) -> AgentResponse:
        """
        Execute agent with retry logic.

        Attempts agent execution up to max_retries times with exponential backoff.
        Implements timeout handling per spec.

        Args:
            agent: Agent instance to execute
            query: Query being processed
            session_context: Session context for agent

        Returns:
            AgentResponse (success or failure)
        """
        for attempt in range(self.max_retries + 1):
            try:
                # Create agent request
                request = AgentRequest(
                    query=query.text,
                    user_id=query.user_id,
                    session_id=query.session_id,
                    context=session_context.to_dict(),
                    metadata={'attempt': attempt + 1}
                )

                # Execute agent with timeout
                response = await asyncio.wait_for(
                    agent.process(request),
                    timeout=self.agent_timeout
                )

                return response

            except asyncio.TimeoutError:
                if attempt < self.max_retries:
                    # Retry with backoff
                    await asyncio.sleep(self.retry_delay_ms / 1000.0)
                    continue
                else:
                    # Final attempt failed
                    return AgentResponse(
                        success=False,
                        content="",
                        metadata={'agent_latency_ms': int(self.agent_timeout * 1000)},
                        error=f"Agent execution timeout after {self.max_retries + 1} attempt(s)"
                    )

            except Exception as e:
                if attempt < self.max_retries:
                    # Retry on other errors
                    await asyncio.sleep(self.retry_delay_ms / 1000.0)
                    continue
                else:
                    # Final attempt failed
                    return AgentResponse(
                        success=False,
                        content="",
                        metadata={},
                        error=f"Agent error: {str(e)}"
                    )

    async def _fallback_to_general_chat(
        self,
        query: Query,
        session_context: SessionContext,
        failed_response: AgentResponse
    ) -> AgentResponse:
        """
        Fallback to general chat agent if primary agent fails.

        Args:
            query: Original query
            session_context: Session context
            failed_response: Response from failed agent (for error context)

        Returns:
            AgentResponse from general chat agent
        """
        general_chat_agent = self.agent_registry.get_agent(Category.GENERAL_CHAT)

        if not general_chat_agent:
            # No fallback available
            return AgentResponse(
                success=False,
                content="",
                metadata={},
                error="Primary agent failed and no fallback available"
            )

        try:
            # Create request with error context
            request = AgentRequest(
                query=query.text,
                user_id=query.user_id,
                session_id=query.session_id,
                context=session_context.to_dict(),
                metadata={
                    'fallback': True,
                    'original_error': failed_response.error
                }
            )

            # Execute fallback agent
            response = await asyncio.wait_for(
                general_chat_agent.process(request),
                timeout=self.agent_timeout
            )

            return response

        except Exception as e:
            return AgentResponse(
                success=False,
                content="",
                metadata={},
                error=f"Fallback agent error: {str(e)}"
            )

    def get_stats(self) -> Dict[str, Any]:
        """
        Get router statistics.

        Returns:
            Dictionary with operational stats
        """
        return {
            'classifier': str(self.classifier),
            'agents_available': len(self.agent_registry.list_available_agents()),
            'session_store': self.session_store.get_stats(),
            'log_repository': 'connected' if (self.log_repository and self.log_repository.test_connection()) else 'not configured'
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"AIRouter(agents={len(self.agent_registry.list_available_agents())}, threshold={self.confidence_threshold})"
