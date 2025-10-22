"""
AgentConfiguration Model - Definition of agent capabilities and LLM settings.

Stores configuration for tools, resources, and processing strategies per agent category.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from .category import Category


@dataclass
class AgentConfiguration:
    """
    Definition of agent capabilities including tools, knowledge sources, and processing strategies.

    Attributes:
        category: Category this config is for
        agent_class: Python class name (e.g., "InformationRetrievalAgent")
        llm_provider: "groq" or "anthropic"
        llm_model: Model identifier (e.g., "llama-3-70b-8192")
        timeout_seconds: Max execution time (default 2)
        retry_count: Number of retries on failure (default 1)
        retry_delay_ms: Delay between retries (default 500)
        tools: Available tools (e.g., ["web_search", "sources_md"])
        resources: Resource paths (e.g., {"sources_file": "./sources.md"})
        system_prompt: Agent's system prompt/instructions
        enabled: Whether agent is active (default True)
    """

    category: Category
    agent_class: str
    llm_provider: str
    llm_model: str
    system_prompt: str
    timeout_seconds: int = 2
    retry_count: int = 1
    retry_delay_ms: int = 500
    tools: List[str] = field(default_factory=list)
    resources: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True

    def __post_init__(self):
        """Validate agent configuration."""
        # Validate timeout
        if self.timeout_seconds <= 0 or self.timeout_seconds > 10:
            raise ValueError(
                f"timeout_seconds must be between 1 and 10, got: {self.timeout_seconds}"
            )

        if self.timeout_seconds > 2:
            # Warning: exceeds recommendation for 3s total latency
            pass

        # Validate provider
        valid_providers = ["groq", "anthropic"]
        if self.llm_provider not in valid_providers:
            raise ValueError(
                f"llm_provider must be one of {valid_providers}, got: {self.llm_provider}"
            )

        # Validate retry settings
        if self.retry_count < 0:
            raise ValueError(f"retry_count must be >= 0, got: {self.retry_count}")

        if self.retry_delay_ms < 0:
            raise ValueError(f"retry_delay_ms must be >= 0, got: {self.retry_delay_ms}")

        # Validate agent class name
        if not self.agent_class or not self.agent_class.endswith("Agent"):
            raise ValueError(
                f"agent_class must end with 'Agent', got: {self.agent_class}"
            )

        # Validate system prompt
        if not self.system_prompt or not self.system_prompt.strip():
            raise ValueError("system_prompt is required and cannot be empty")

        # Validate Industry Knowledge agent has sources_file
        if self.category == Category.INDUSTRY_KNOWLEDGE:
            if "sources_file" not in self.resources:
                raise ValueError(
                    "Industry Knowledge agent must have 'sources_file' in resources"
                )

    def to_dict(self) -> Dict:
        """
        Convert agent configuration to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "category": self.category.value,
            "agent_class": self.agent_class,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "retry_delay_ms": self.retry_delay_ms,
            "tools": self.tools,
            "resources": self.resources,
            "system_prompt": self.system_prompt,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AgentConfiguration":
        """
        Create AgentConfiguration from dictionary.

        Args:
            data: Dictionary with configuration data

        Returns:
            AgentConfiguration instance
        """
        category = Category.from_string(data["category"])

        return cls(
            category=category,
            agent_class=data["agent_class"],
            llm_provider=data["llm_provider"],
            llm_model=data["llm_model"],
            system_prompt=data["system_prompt"],
            timeout_seconds=data.get("timeout_seconds", 2),
            retry_count=data.get("retry_count", 1),
            retry_delay_ms=data.get("retry_delay_ms", 500),
            tools=data.get("tools", []),
            resources=data.get("resources", {}),
            enabled=data.get("enabled", True),
        )

    def get_total_timeout_ms(self) -> int:
        """
        Get total timeout including retries.

        Returns:
            Total milliseconds including all retry attempts
        """
        # Initial attempt + retries
        total_attempts = 1 + self.retry_count
        # Timeout per attempt + delay between retries
        total_ms = (self.timeout_seconds * 1000 * total_attempts) + (self.retry_delay_ms * self.retry_count)
        return total_ms

    def supports_tool(self, tool_name: str) -> bool:
        """
        Check if agent supports a specific tool.

        Args:
            tool_name: Tool name to check

        Returns:
            True if tool is in agent's tools list
        """
        return tool_name in self.tools

    def get_resource(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a resource path by key.

        Args:
            key: Resource key
            default: Default value if key not found

        Returns:
            Resource value or default
        """
        return self.resources.get(key, default)

    def is_anthropic(self) -> bool:
        """Check if using Anthropic provider."""
        return self.llm_provider == "anthropic"

    def is_groq(self) -> bool:
        """Check if using Groq provider."""
        return self.llm_provider == "groq"

    def __str__(self) -> str:
        """String representation of agent configuration."""
        return (
            f"AgentConfig(category={self.category.value}, "
            f"provider={self.llm_provider}, model={self.llm_model})"
        )

    def __repr__(self) -> str:
        """Detailed representation of agent configuration."""
        return (
            f"AgentConfiguration(category={self.category.value}, "
            f"agent_class={self.agent_class}, "
            f"llm_provider={self.llm_provider}, "
            f"llm_model={self.llm_model}, "
            f"timeout={self.timeout_seconds}s, "
            f"enabled={self.enabled})"
        )
