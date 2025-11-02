"""
Agent Interface Contract

This module defines the contract that all agent implementations must follow.
Used for contract testing to ensure all agents implement the interface correctly.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class Category(str, Enum):
    """Six predefined routing categories"""
    INFORMATION_RETRIEVAL = "INFORMATION_RETRIEVAL"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    REPORT_GENERATION = "REPORT_GENERATION"
    AUTOMATION = "AUTOMATION"
    INDUSTRY_KNOWLEDGE = "INDUSTRY_KNOWLEDGE"
    GENERAL_CHAT = "GENERAL_CHAT"


@dataclass
class AgentRequest:
    """
    Request object passed to agent for processing

    Attributes:
        query (str): User's question or request (max 1000 words, pre-validated)
        user_id (str): Authenticated user identifier
        session_id (str): Session UUID for context continuity
        context (Optional[Dict]): Session context including previous messages and routing history
        metadata (Dict): Additional request metadata (timestamps, request_id, etc.)
        staff_role (Optional[str]): Optional staff role for specialisation (e.g., "person_1_managing_director")
        specialisation_context (Optional[Dict]): Loaded specialisation resources and context (if staff_role specified)
    """
    query: str
    user_id: str
    session_id: str
    context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    staff_role: Optional[str] = None
    specialisation_context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate request after initialization"""
        if not self.query or not self.query.strip():
            raise ValueError("Query cannot be empty")
        if not self.user_id:
            raise ValueError("User ID is required")
        if not self.session_id:
            raise ValueError("Session ID is required")

        # Truncate query to 1000 words if needed (defensive check, should be pre-validated)
        words = self.query.split()
        if len(words) > 1000:
            self.query = ' '.join(words[:1000])
            if self.metadata is None:
                self.metadata = {}
            self.metadata['truncated'] = True


@dataclass
class AgentResponse:
    """
    Response object returned by agent after processing

    Attributes:
        success (bool): Whether agent execution succeeded
        content (str): Agent's response text (empty if success=False)
        metadata (Dict): Additional response metadata (sources, timing, tokens, etc.)
        error (Optional[str]): Error message if success=False
        staff_role_context (Optional[str]): Staff role used for specialisation (if applicable)

    Contract Requirements:
        - If success=True, content must be non-empty
        - If success=False, error must be set
        - metadata should include 'agent_latency_ms' for performance tracking
        - metadata should include 'sources' (List[str]) if agent cites external sources
        - metadata may include 'tokens_used' (int) for LLM cost tracking
        - metadata may include 'staff_role_used', 'specialisation_status', 'resources_consulted' for specialisation tracking
    """
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    staff_role_context: Optional[str] = None

    def __post_init__(self):
        """Validate response after initialization"""
        if self.success and not self.content:
            raise ValueError("Content cannot be empty when success=True")
        if not self.success and not self.error:
            raise ValueError("Error message required when success=False")


class BaseAgent(ABC):
    """
    Abstract base class for all agent implementations

    All agents must:
    1. Inherit from BaseAgent
    2. Implement process() method (async, returns AgentResponse)
    3. Implement get_category() method (returns Category enum)
    4. Respect timeout specified in config (default 2 seconds)
    5. Handle errors gracefully and return AgentResponse with success=False

    Configuration:
        Passed as dict in __init__, must include:
        - 'timeout_seconds' (int): Max execution time (default: 2)
        - 'llm_provider' (str): "groq" or "anthropic"
        - 'llm_model' (str): Model identifier
        - 'system_prompt' (str): Agent instructions
        - Optional: 'tools', 'resources', 'retry_count', 'retry_delay_ms'
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize agent with configuration

        Args:
            config: Configuration dictionary with agent settings

        Raises:
            ValueError: If required config fields are missing or invalid
        """
        self.config = config
        self._validate_config()

        # Core settings (with defaults)
        self.timeout = config.get('timeout_seconds', 2)
        self.llm_provider = config['llm_provider']
        self.llm_model = config['llm_model']
        self.system_prompt = config['system_prompt']

        # Optional settings
        self.tools = config.get('tools', [])
        self.resources = config.get('resources', {})
        self.retry_count = config.get('retry_count', 1)
        self.retry_delay_ms = config.get('retry_delay_ms', 500)
        self.enabled = config.get('enabled', True)

    def _validate_config(self):
        """Validate required configuration fields"""
        required_fields = ['llm_provider', 'llm_model', 'system_prompt']
        for field in required_fields:
            if field not in self.config:
                raise ValueError(f"Missing required config field: {field}")

        if self.config['llm_provider'] not in ['groq', 'anthropic']:
            raise ValueError("llm_provider must be 'groq' or 'anthropic'")

        timeout = self.config.get('timeout_seconds', 2)
        if timeout > 2:
            raise ValueError("timeout_seconds must be <= 2 to meet latency requirements")

    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """
        Process request and return response

        This method MUST:
        - Complete within self.timeout seconds
        - Return AgentResponse with success=True on successful execution
        - Return AgentResponse with success=False and error message on failure
        - Handle all exceptions internally (never raise to caller)
        - Include 'agent_latency_ms' in response.metadata

        Args:
            request: AgentRequest containing query and context

        Returns:
            AgentResponse: Response object with success status and content/error

        Example:
            ```python
            async def process(self, request: AgentRequest) -> AgentResponse:
                start_time = time.time()
                try:
                    result = await asyncio.wait_for(
                        self._execute_agent_logic(request.query),
                        timeout=self.timeout
                    )
                    latency_ms = int((time.time() - start_time) * 1000)
                    return AgentResponse(
                        success=True,
                        content=result,
                        metadata={
                            'agent_latency_ms': latency_ms,
                            'sources': ['source1', 'source2']
                        }
                    )
                except asyncio.TimeoutError:
                    latency_ms = int((time.time() - start_time) * 1000)
                    return AgentResponse(
                        success=False,
                        content="",
                        metadata={'agent_latency_ms': latency_ms},
                        error="Agent timeout exceeded"
                    )
                except Exception as e:
                    latency_ms = int((time.time() - start_time) * 1000)
                    return AgentResponse(
                        success=False,
                        content="",
                        metadata={'agent_latency_ms': latency_ms},
                        error=f"Agent error: {str(e)}"
                    )
            ```
        """
        pass

    @abstractmethod
    def get_category(self) -> Category:
        """
        Return the category this agent handles

        Returns:
            Category: One of the six predefined categories

        Example:
            ```python
            def get_category(self) -> Category:
                return Category.INFORMATION_RETRIEVAL
            ```
        """
        pass

    def validate_request(self, request: AgentRequest) -> bool:
        """
        Validate request before processing

        Default implementation checks for non-empty query.
        Override this method to add agent-specific validation.

        Args:
            request: AgentRequest to validate

        Returns:
            bool: True if request is valid, False otherwise

        Example Override:
            ```python
            def validate_request(self, request: AgentRequest) -> bool:
                # Call parent validation first
                if not super().validate_request(request):
                    return False

                # Add agent-specific validation
                if self.get_category() == Category.INDUSTRY_KNOWLEDGE:
                    # Ensure sources file is accessible
                    if 'sources_file' not in self.resources:
                        return False

                return True
            ```
        """
        return len(request.query.strip()) > 0


class AgentRegistry:
    """
    Registry for managing agent instances and configurations

    Used by router to:
    1. Load agent configurations from JSON/YAML
    2. Instantiate agents dynamically
    3. Get agent for specific category
    4. Check agent availability

    Not part of agent contract, but provided for reference.
    """

    def __init__(self):
        self._agents: Dict[Category, BaseAgent] = {}
        self._configs: Dict[Category, Dict[str, Any]] = {}

    def register_agent(self, agent: BaseAgent):
        """Register an agent instance"""
        category = agent.get_category()
        self._agents[category] = agent
        self._configs[category] = agent.config

    def get_agent(self, category: Category) -> Optional[BaseAgent]:
        """Get agent for specified category"""
        return self._agents.get(category)

    def is_agent_available(self, category: Category) -> bool:
        """Check if agent is registered and enabled"""
        agent = self._agents.get(category)
        return agent is not None and agent.enabled

    def list_available_agents(self) -> List[Category]:
        """List all registered and enabled agents"""
        return [
            category for category, agent in self._agents.items()
            if agent.enabled
        ]


# Contract Testing Helpers

class MockAgent(BaseAgent):
    """
    Mock agent for testing

    Always returns success with configurable response
    """

    def __init__(self, config: Dict[str, Any], mock_response: str = "Mock response"):
        super().__init__(config)
        self.mock_response = mock_response
        self.call_count = 0
        self.last_request = None

    async def process(self, request: AgentRequest) -> AgentResponse:
        """Return mock response"""
        import asyncio
        import time

        self.call_count += 1
        self.last_request = request

        start_time = time.time()
        # Simulate some processing time
        await asyncio.sleep(0.1)
        latency_ms = int((time.time() - start_time) * 1000)

        return AgentResponse(
            success=True,
            content=self.mock_response,
            metadata={
                'agent_latency_ms': latency_ms,
                'sources': ['mock_source'],
                'call_count': self.call_count
            }
        )

    def get_category(self) -> Category:
        """Return category from config"""
        return Category(self.config.get('category', 'GENERAL_CHAT'))


def create_test_config(
    category: Category = Category.GENERAL_CHAT,
    llm_provider: str = "groq",
    llm_model: str = "llama-3.3-70b-versatile",
    timeout: int = 2
) -> Dict[str, Any]:
    """
    Create a valid test configuration for agent testing

    Args:
        category: Agent category
        llm_provider: LLM provider name
        llm_model: LLM model identifier
        timeout: Timeout in seconds

    Returns:
        Dict with valid agent configuration
    """
    return {
        'category': category.value,
        'llm_provider': llm_provider,
        'llm_model': llm_model,
        'system_prompt': f"You are a {category.value.lower().replace('_', ' ')} agent.",
        'timeout_seconds': timeout,
        'tools': [],
        'resources': {},
        'enabled': True
    }


def create_test_request(
    query: str = "Test query",
    user_id: str = "test_user",
    session_id: str = "550e8400-e29b-41d4-a716-446655440000"
) -> AgentRequest:
    """
    Create a valid test request for agent testing

    Args:
        query: Query text
        user_id: User identifier
        session_id: Session UUID

    Returns:
        AgentRequest with test data
    """
    return AgentRequest(
        query=query,
        user_id=user_id,
        session_id=session_id,
        context={
            'message_history': [],
            'routing_history': []
        },
        metadata={
            'timestamp': datetime.utcnow().isoformat(),
            'request_id': '123e4567-e89b-12d3-a456-426614174000'
        }
    )


# Contract Validation (for pytest contract tests)

def validate_agent_contract(agent_class: type, config: Dict[str, Any]) -> List[str]:
    """
    Validate that an agent class implements the BaseAgent contract correctly

    Args:
        agent_class: Agent class to validate (not instance)
        config: Configuration to use for instantiation

    Returns:
        List of validation errors (empty if valid)

    Example:
        ```python
        def test_information_retrieval_agent_contract():
            config = create_test_config(Category.INFORMATION_RETRIEVAL)
            errors = validate_agent_contract(InformationRetrievalAgent, config)
            assert len(errors) == 0, f"Contract violations: {errors}"
        ```
    """
    errors = []

    # Check inheritance
    if not issubclass(agent_class, BaseAgent):
        errors.append(f"{agent_class.__name__} does not inherit from BaseAgent")
        return errors  # Cannot continue validation

    # Try instantiation
    try:
        agent = agent_class(config)
    except Exception as e:
        errors.append(f"Failed to instantiate {agent_class.__name__}: {e}")
        return errors

    # Check required methods
    if not hasattr(agent, 'process'):
        errors.append("Missing process() method")
    elif not asyncio.iscoroutinefunction(agent.process):
        errors.append("process() method must be async")

    if not hasattr(agent, 'get_category'):
        errors.append("Missing get_category() method")
    else:
        try:
            category = agent.get_category()
            if not isinstance(category, Category):
                errors.append(f"get_category() must return Category enum, got {type(category)}")
        except Exception as e:
            errors.append(f"get_category() raised exception: {e}")

    # Check configuration validation
    try:
        invalid_config = {}
        agent_class(invalid_config)
        errors.append("Agent does not validate required config fields (should raise ValueError)")
    except ValueError:
        pass  # Expected
    except Exception as e:
        errors.append(f"Unexpected exception during config validation: {e}")

    return errors


# Export contract components
__all__ = [
    'BaseAgent',
    'AgentRequest',
    'AgentResponse',
    'Category',
    'AgentRegistry',
    'MockAgent',
    'create_test_config',
    'create_test_request',
    'validate_agent_contract'
]
