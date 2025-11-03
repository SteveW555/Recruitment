"""
AI Router - Main query routing orchestration.

Routes user queries to specialized agent handlers based on semantic classification.
Manages session context, handles retries, and logs all routing decisions.
"""

import asyncio
import sys
import time
import os
from typing import Optional, Dict, Any
from datetime import datetime

from logging_new import Logger

# Initialize logger for AI Router
logger = Logger("ai-router")

from .models.query import Query
from .models.routing_decision import RoutingDecision
from .models.session_context import SessionContext
from .models.category import Category
from .groq_classifier import GroqClassifier
from .storage.session_store import SessionStore
from .storage.log_repository import LogRepository
from .agent_registry import AgentRegistry
from .agents.base_agent import AgentRequest, AgentResponse
from .staff_specialisations import (
    SpecialisationManager,
    get_staff_role_from_kwargs,
    enhance_agent_request_with_specialisation,
    enhance_agent_response_with_specialisation,
)

# CV Matching bypass imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../backend/services/matching-engine"))
from cv_matcher.quick_match import quick_match, quick_match_multi
import json


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
    8. Support staff role specialisations (optional)

    Performance targets:
    - End-to-end latency: <3 seconds (95th percentile)
    - Agent timeout: 2 seconds with 1 retry
    - Specialisation overhead: <100ms

    Staff Specialisations:
    - When staff_role is provided in kwargs, loads role-specific resources
    - Passes specialisation context to agents via AgentRequest
    - Agents can use resources to enhance responses
    - Backward compatible (works without staff_role)
    """

    def __init__(
        self,
        classifier: GroqClassifier,
        session_store: SessionStore,
        log_repository: Optional[LogRepository],
        agent_registry: AgentRegistry,
        confidence_threshold: float = 0.65,
        agent_timeout: float = 2.0,
        max_retries: int = 1,
        retry_delay_ms: int = 500,
        enable_specialisations: bool = True,
    ):
        """
        Initialize router with dependencies.

        Args:
            classifier: GroqClassifier for query classification
            session_store: Redis session storage
            log_repository: PostgreSQL log repository (optional - None disables logging)
            agent_registry: Agent registry for loading agents
            confidence_threshold: Minimum confidence for routing (default 0.65)
            agent_timeout: Agent execution timeout in seconds (default 2)
            max_retries: Maximum retries for agent execution (default 1)
            retry_delay_ms: Delay between retries in ms (default 500)
            enable_specialisations: Enable staff role specialisations (default True)
        """
        self.classifier = classifier
        self.session_store = session_store
        self.log_repository = log_repository
        self.agent_registry = agent_registry
        self.confidence_threshold = confidence_threshold
        self.agent_timeout = agent_timeout
        self.max_retries = max_retries
        self.retry_delay_ms = retry_delay_ms

        # Initialize staff specialisation manager (if enabled)
        self.enable_specialisations = enable_specialisations
        self.specialisation_manager = SpecialisationManager() if enable_specialisations else None

    async def route(
        self,
        query_text: str,
        user_id: str,
        session_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        logger.info(f"router.py routing {user_id}, session {session_id}")

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
            **kwargs: Additional metadata (timestamps, request_id, etc.)F

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

        print(f"[Router] Routing Called:  query for user {user_id}, session {session_id}", file=sys.stderr)
        sys.stderr.flush()  # Force immediate output

        try:
            # CV MATCHING BYPASS: Check for exact match query
            # Load configuration
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            config_path = os.path.join(project_root, "config/cv_matching_config.json")

            cv_matching_config = None
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    cv_matching_config = json.load(f).get('cv_matching', {})

            trigger_query = cv_matching_config.get('trigger_query', 'Find best matching CVs') if cv_matching_config else 'Find best matching CVs'

            if query_text.strip() == trigger_query and cv_matching_config and cv_matching_config.get('enabled', True):
                logger.info("CV Matching Bypass activated - skipping AI routing")
                print("[Router] CV MATCHING BYPASS ACTIVATED", file=sys.stderr)
                sys.stderr.flush()

                try:
                    # Load scenario from config
                    default_scenario = cv_matching_config.get('default_scenario', 'elena_customer_support')
                    scenarios = cv_matching_config.get('scenarios', {})
                    scenario = scenarios.get(default_scenario, {})

                    if not scenario:
                        raise ValueError(f"Scenario '{default_scenario}' not found in config")

                    # Get job description
                    job_desc_path = os.path.join(project_root, scenario['job_description_path'])
                    logger.info(f"Using scenario: {default_scenario}")
                    logger.info(f"Reading job description from: {job_desc_path}")
                    with open(job_desc_path, 'r', encoding='utf-8') as f:
                        job_description = f.read()

                    # Check if we're doing single or multiple CV matching
                    find_multiple = scenario.get('find_multiple', False)

                    if find_multiple:
                        # MULTIPLE CV MATCHING
                        cv_paths = scenario.get('cv_paths', [])
                        candidate_names = scenario.get('candidate_names', [])

                        if not cv_paths:
                            raise ValueError("cv_paths list is required when find_multiple=true")

                        # Convert to absolute paths
                        cv_paths_abs = [os.path.join(project_root, p) for p in cv_paths]

                        logger.info(f"Matching {len(cv_paths)} CVs")
                        print(f"[Router] Calling quick_match_multi for {len(cv_paths)} candidates", file=sys.stderr)
                        sys.stderr.flush()

                        match_result = quick_match_multi(job_description, cv_paths_abs, candidate_names)
                    else:
                        # SINGLE CV MATCHING
                        cv_path = os.path.join(project_root, scenario['cv_path'])
                        candidate_name = scenario.get('candidate_name', 'Unknown')

                        logger.info(f"Matching CV: {cv_path}")
                        print(f"[Router] Calling quick_match for {candidate_name}", file=sys.stderr)
                        sys.stderr.flush()

                        match_result = quick_match(job_description, cv_path, candidate_name)

                    # Log the result to terminal
                    logger.info("CV MATCH RESULT:")
                    logger.info(match_result)
                    print("\n" + "="*60, file=sys.stderr)
                    print("CV MATCHING RESULT:", file=sys.stderr)
                    print("="*60, file=sys.stderr)
                    print(match_result, file=sys.stderr)
                    print("="*60 + "\n", file=sys.stderr)
                    sys.stderr.flush()

                    # Create a properly formatted AgentResponse
                    from .agents.base_agent import AgentResponse

                    # Build metadata based on matching mode
                    metadata = {
                        'agent_latency_ms': int((time.time() - start_time) * 1000),
                        'bypass': 'cv_matching',
                        'scenario': default_scenario,
                        'job': scenario.get('name', 'Unknown Job'),
                        'expected_outcome': scenario.get('expected_outcome', 'N/A'),
                        'find_multiple': find_multiple
                    }

                    if find_multiple:
                        metadata['candidates_count'] = len(cv_paths)
                        metadata['candidates'] = candidate_names if candidate_names else [f"Candidate {i+1}" for i in range(len(cv_paths))]
                    else:
                        metadata['candidate'] = candidate_name

                    agent_response = AgentResponse(
                        success=True,
                        content=f"CV Matching Complete:\n\n{match_result}",
                        metadata=metadata,
                        error=None
                    )

                    # Create a dummy decision for logging
                    from .models.routing_decision import RoutingDecision
                    decision = RoutingDecision(
                        query_id="bypass",
                        primary_category=Category.INFORMATION_RETRIEVAL,
                        primary_confidence=1.0,
                        reasoning="CV Matching Bypass",
                        timestamp=datetime.utcnow()
                    )

                    # Create query for result
                    query = Query(
                        text=query_text,
                        user_id=user_id,
                        session_id=session_id
                    )

                    result = {
                        'success': True,
                        'query': query,
                        'decision': decision,
                        'agent_response': agent_response,
                        'error': None,
                        'latency_ms': int((time.time() - start_time) * 1000)
                    }

                    return result

                except Exception as e:
                    error_msg = f"CV Matching failed: {str(e)}"
                    logger.error(error_msg)
                    print(f"[Router] CV MATCHING ERROR: {error_msg}", file=sys.stderr)
                    sys.stderr.flush()

                    # Fall through to normal routing on error
                    pass

            # Step 1: Extract staff_role from kwargs (if provided)
            staff_role = get_staff_role_from_kwargs(kwargs) if self.enable_specialisations else None

            # Step 2: Validate and create Query
            query = Query(
                text=query_text,
                user_id=user_id,
                session_id=session_id
            )

            # Step 3: Load session context
            if self.session_store:
                session_context = self.session_store.load(user_id, session_id)
            else:
                session_context = None

            if not session_context:
                session_context = SessionContext(
                    user_id=user_id,
                    session_id=session_id
                )

            # Step 3: Classify query (with context awareness)
            # Get previous agent from session context for follow-up detection
            previous_agent = None
            if session_context and len(session_context.routing_history) > 0:
                # Get the most recent routing decision
                previous_agent = session_context.routing_history[-1].get('category')

            # DIAGNOSTIC: Log before classify() call
            print(f"[Router] ABOUT TO CALL classifier.classify() for query_id: {query.id}", file=sys.stderr)
            logger.info(f"About to call classifier.classify() for query_id: {query.id}")
            sys.stderr.flush()

            decision = self.classifier.classify(query.text, query.id, previous_agent)

            # DIAGNOSTIC: Log after classify() call
            print(f"[Router] classifier.classify() RETURNED for query_id: {query.id}", file=sys.stderr)
            logger.info(f"classifier.classify() returned for query_id: {query.id}")
            sys.stderr.flush()

            # Step 4: Check confidence and route
            print(f"[Router] Checking confidence: {decision.primary_confidence} against threshold {self.confidence_threshold}", file=sys.stderr)
            if decision.primary_confidence < self.confidence_threshold:
                # Low confidence - route to general chat with warning
                warning_message = f"⚠ Low confidence ({decision.primary_confidence:.1%}). Routing to general chat."
                print(f"[Router] LOW CONFIDENCE DETECTED - Routing to general chat", file=sys.stderr)

                # Override decision to use general chat
                decision.primary_category = Category.GENERAL_CHAT
                decision.fallback_triggered = True

                # Get general chat agent
                agent = self.agent_registry.get_agent(Category.GENERAL_CHAT)

                if not agent:
                    # Fallback failed - return error
                    error_msg = "General chat agent unavailable"
                    result = {
                        'success': False,
                        'query': query,
                        'decision': decision,
                        'agent_response': None,
                        'error': error_msg,
                        'latency_ms': int((time.time() - start_time) * 1000)
                    }

                    if self.log_repository:
                        self.log_repository.log_routing_decision(
                            query, decision, False,
                            error_message=error_msg
                        )

                    return result

                # Execute general chat agent
                agent_response = await self._execute_agent_with_retry(
                    agent, query, session_context, staff_role, decision
                )

                # Save conversation history for low-confidence fallback
                session_context.add_message('user', query_text)
                session_context.add_routing_decision(
                    query.id,
                    category=decision.primary_category.value
                )
                if agent_response and agent_response.success and agent_response.content:
                    session_context.add_message(
                        'assistant',
                        agent_response.content,
                        category='general-chat'
                    )
                if self.session_store:
                    self.session_store.save(session_context)

                # Add warning to metadata (not to chat response)
                # Note: Specialisation context is passed to agent via AgentRequest,
                # and agents are responsible for using it and adding metadata
                result = {
                    'success': agent_response.success,
                    'query': query,
                    'decision': decision,
                    'agent_response': agent_response,
                    'error': None if agent_response.success else agent_response.error,
                    'latency_ms': int((time.time() - start_time) * 1000),
                    'low_confidence_warning': warning_message  # For console logging
                }

                # Log decision
                if self.log_repository:
                    self.log_repository.log_routing_decision(
                        query, decision, agent_response.success,
                        agent_name="GeneralChatAgent (low confidence)",
                        error_message=None if agent_response.success else agent_response.error
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
                agent, query, session_context, staff_role, decision
            )

            # Step 7: Handle agent failure - fallback to general chat
            if not agent_response.success:
                fallback_response = await self._fallback_to_general_chat(
                    query, session_context, agent_response, staff_role
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
            session_context.add_message('user', query_text)
            session_context.add_routing_decision(
                query.id,
                category=decision.primary_category.value
            )

            # Save assistant's response to conversation history
            if agent_response and agent_response.success and agent_response.content:
                session_context.add_message(
                    'assistant',
                    agent_response.content,
                    category=decision.primary_category.value if decision else None
                )

            if self.session_store:
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
    #========================================================================
    #  _execute_agent_with_retry
    #========================================================================
    async def _execute_agent_with_retry(
        self,
        agent,
        query: Query,
        session_context: SessionContext,
        staff_role: Optional[str] = None,
        decision: Optional[Any] = None
    ) -> AgentResponse:
        """
        Execute agent with retry logic.

        Attempts agent execution up to max_retries times with exponential backoff.
        Implements timeout handling per spec.

        Args:
            agent: Agent instance to execute
            query: Query being processed
            session_context: Session context for agent
            staff_role: Optional staff role for specialisation

        Returns:
            AgentResponse (success or failure)
        """

        print(f"[*] **** Router._execute_agent_with_retry() CALLED: agent={agent.__class__.__name__}, query_id={query.id}", file=sys.stderr)
        sys.stderr.flush()

        for attempt in range(self.max_retries + 1):
            try:
                # Create agent request
                request_dict = {
                    'query': query.text,
                    'user_id': query.user_id,
                    'session_id': query.session_id,
                    'context': session_context.to_dict(),
                    'metadata': {'attempt': attempt + 1}
                }

                # Add suggested_table from routing decision (if available)
                if decision and hasattr(decision, 'suggested_table'):
                    request_dict['suggested_table'] = decision.suggested_table

                # Enhance with staff specialisation context (if enabled and staff_role provided)
                if self.enable_specialisations and staff_role:
                    request_dict = enhance_agent_request_with_specialisation(
                        request_dict,
                        self.specialisation_manager,
                        staff_role
                    )

                # Convert to AgentRequest object
                request = AgentRequest(**request_dict)

                # Execute agent with timeout
                response = await asyncio.wait_for(
                    agent.process(request),
                    timeout=self.agent_timeout
                )

                print(f"[*] Router._execute_agent_with_retry() SUCCESS: agent={agent.__class__.__name__}, success={response.success}", file=sys.stderr)
                sys.stderr.flush()
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
        failed_response: AgentResponse,
        staff_role: Optional[str] = None
    ) -> AgentResponse:
        """
        Fallback to general chat agent if primary agent fails.

        Args:
            query: Original query
            session_context: Session context
            failed_response: Response from failed agent (for error context)
            staff_role: Optional staff role for specialisation

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
            request_dict = {
                'query': query.text,
                'user_id': query.user_id,
                'session_id': query.session_id,
                'context': session_context.to_dict(),
                'metadata': {
                    'fallback': True,
                    'original_error': failed_response.error
                }
            }

            # Enhance with staff specialisation context (if enabled and staff_role provided)
            if self.enable_specialisations and staff_role:
                request_dict = enhance_agent_request_with_specialisation(
                    request_dict,
                    self.specialisation_manager,
                    staff_role
                )

            # Convert to AgentRequest object
            request = AgentRequest(**request_dict)

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
