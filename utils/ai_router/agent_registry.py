"""
Agent Registry - Dynamic agent instantiation and management.

Loads agent configurations from JSON, instantiates agent classes,
and provides runtime access to agents by category.
"""

import json
import os
import importlib
from typing import Dict, Optional, List, Any
from pathlib import Path

from .models.category import Category
from .agents.base_agent import BaseAgent


class AgentRegistry:
    """
    Registry for managing agent instances and configurations.

    Responsibilities:
    1. Load agent configurations from config/agents.json
    2. Dynamically import and instantiate agent classes
    3. Provide get_agent() method for router to retrieve agents by category
    4. Check agent availability and enable/disable agents
    5. Handle agent initialization errors gracefully
    """

    def __init__(self, config_path: str = "config/agents.json"):
        """
        Initialize agent registry by loading configuration.

        Args:
            config_path: Path to agents.json configuration file

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        self.config_path = config_path
        self._agents: Dict[Category, BaseAgent] = {}
        self._configs: Dict[Category, Dict[str, Any]] = {}
        self._load_config()

    def _load_config(self):
        """Load agent configurations from JSON file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}. "
                f"Create it with agent configurations for each category."
            )

        with open(self.config_path, "r") as f:
            self.config = json.load(f)

        print(f"Loaded agent configuration from {self.config_path}")

    def instantiate_agents(self) -> Dict[str, str]:
        """
        Instantiate all configured agents.

        Returns:
            Dictionary mapping category names to initialization status
            (e.g., {"INFORMATION_RETRIEVAL": "OK", "GENERAL_CHAT": "FAILED: ..."})

        This method should be called after initialization to load all agents.
        If an agent fails to instantiate, it's marked as unavailable but registry
        continues loading other agents.
        """
        status = {}

        for category_str, agent_config in self.config.items():
            try:
                category = Category.from_string(category_str)
                agent_class_path = agent_config.get("agent_class")

                if not agent_class_path:
                    status[category_str] = "SKIPPED: No agent_class specified"
                    continue

                # Try to instantiate the agent
                agent = self._load_agent_class(agent_class_path, agent_config)
                self._agents[category] = agent
                self._configs[category] = agent_config
                status[category_str] = "OK"
                print(f"✓ Loaded agent for {category.value}")

            except Exception as e:
                status[category_str] = f"FAILED: {str(e)}"
                print(f"✗ Failed to load {category_str}: {e}")
                continue

        return status

    def _load_agent_class(self, class_path: str, config: Dict[str, Any]) -> BaseAgent:
        """
        Dynamically load and instantiate an agent class.

        Args:
            class_path: Module path to agent class (e.g., "utils.ai_router.agents.information_retrieval_agent:InformationRetrievalAgent")
            config: Agent configuration dictionary

        Returns:
            Instantiated agent

        Raises:
            ImportError: If module or class cannot be imported
            TypeError: If agent_class doesn't inherit from BaseAgent
        """
        # Parse class path (format: "module.path:ClassName")
        if ":" not in class_path:
            raise ValueError(f"Invalid class path format: {class_path}. Use 'module.path:ClassName'")

        module_path, class_name = class_path.split(":", 1)

        # Dynamically import module
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Cannot import module {module_path}: {e}")

        # Get agent class from module
        if not hasattr(module, class_name):
            raise ImportError(f"Module {module_path} has no class {class_name}")

        agent_class = getattr(module, class_name)

        # Verify it's a BaseAgent subclass
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{class_name} must inherit from BaseAgent")

        # Instantiate the agent
        return agent_class(config)

    def get_agent(self, category: Category) -> Optional[BaseAgent]:
        """
        Get agent for specified category.

        Args:
            category: Category enum value

        Returns:
            Agent instance if registered and enabled, None otherwise
        """
        agent = self._agents.get(category)
        if agent and agent.enabled:
            return agent
        return None

    def is_agent_available(self, category: Category) -> bool:
        """
        Check if agent is registered and enabled.

        Args:
            category: Category to check

        Returns:
            True if agent is available, False otherwise
        """
        agent = self._agents.get(category)
        return agent is not None and agent.enabled

    def list_available_agents(self) -> List[Category]:
        """
        List all registered and enabled agents.

        Returns:
            List of Category enums for available agents
        """
        return [
            category for category, agent in self._agents.items()
            if agent.enabled
        ]

    def get_agent_config(self, category: Category) -> Optional[Dict[str, Any]]:
        """
        Get configuration for an agent.

        Args:
            category: Category to get config for

        Returns:
            Configuration dictionary or None if not found
        """
        return self._configs.get(category)

    def enable_agent(self, category: Category) -> bool:
        """
        Enable an agent.

        Args:
            category: Category to enable

        Returns:
            True if agent was enabled, False if not found
        """
        agent = self._agents.get(category)
        if agent:
            agent.enabled = True
            return True
        return False

    def disable_agent(self, category: Category) -> bool:
        """
        Disable an agent.

        Args:
            category: Category to disable

        Returns:
            True if agent was disabled, False if not found
        """
        agent = self._agents.get(category)
        if agent:
            agent.enabled = False
            return True
        return False

    def get_all_agents(self) -> Dict[Category, BaseAgent]:
        """Get all registered agents (including disabled ones)."""
        return self._agents.copy()

    def __repr__(self) -> str:
        """String representation."""
        available_count = len(self.list_available_agents())
        total_count = len(self._agents)
        return f"AgentRegistry(available={available_count}/{total_count})"
