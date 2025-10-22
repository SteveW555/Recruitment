"""
Category Enum - Seven predefined classification types for query routing.

This module defines the Category enum used throughout the AI Router system
to classify and route queries to specialized agents.
"""

from enum import Enum
from typing import Dict, List


class Category(str, Enum):
    """
    Seven predefined query categories for AI routing.

    Each category routes to a specialized agent with appropriate tools,
    resources, and LLM configuration.
    """

    INFORMATION_RETRIEVAL = "INFORMATION_RETRIEVAL"
    DATA_OPERATIONS = "DATA_OPERATIONS"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    REPORT_GENERATION = "REPORT_GENERATION"
    AUTOMATION = "AUTOMATION"
    INDUSTRY_KNOWLEDGE = "INDUSTRY_KNOWLEDGE"
    GENERAL_CHAT = "GENERAL_CHAT"

    @classmethod
    def get_priority(cls, category: "Category") -> int:
        """
        Get priority level for a category (1=highest, 3=lowest).

        Args:
            category: The category to get priority for

        Returns:
            Priority level: 1 (P1), 2 (P2), or 3 (P3)
        """
        priority_map = {
            cls.INFORMATION_RETRIEVAL: 1,  # P1 - Most common, MVP
            cls.DATA_OPERATIONS: 1,         # P1 - Core system operations, MVP
            cls.INDUSTRY_KNOWLEDGE: 1,      # P1 - Critical for recruitment, MVP
            cls.PROBLEM_SOLVING: 2,         # P2 - High value, complex
            cls.AUTOMATION: 2,              # P2 - High operational impact
            cls.REPORT_GENERATION: 3,       # P3 - Valuable but less frequent
            cls.GENERAL_CHAT: 3,            # P3 - UX important, lowest business value
        }
        return priority_map.get(category, 3)

    @classmethod
    def get_description(cls, category: "Category") -> str:
        """
        Get human-readable description for a category.

        Args:
            category: The category to describe

        Returns:
            Description string
        """
        descriptions = {
            cls.INFORMATION_RETRIEVAL: "External information retrieval from multiple sources",
            cls.DATA_OPERATIONS: "Internal system operations and data management",
            cls.PROBLEM_SOLVING: "Complex analysis and recommendations",
            cls.REPORT_GENERATION: "Visualization and presentation creation",
            cls.AUTOMATION: "Workflow pipeline design",
            cls.INDUSTRY_KNOWLEDGE: "UK recruitment domain expertise",
            cls.GENERAL_CHAT: "Casual conversation",
        }
        return descriptions.get(category, "Unknown category")

    @classmethod
    def from_string(cls, value: str) -> "Category":
        """
        Convert string to Category enum.

        Args:
            value: String representation of category

        Returns:
            Category enum value

        Raises:
            ValueError: If value is not a valid category
        """
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(
                f"Invalid category: {value}. Must be one of: "
                f"{', '.join([c.value for c in cls])}"
            )

    @classmethod
    def all_categories(cls) -> List["Category"]:
        """Get list of all categories."""
        return list(cls)

    @classmethod
    def get_agent_class_name(cls, category: "Category") -> str:
        """
        Get the agent class name for a category.

        Args:
            category: The category

        Returns:
            Agent class name (e.g., "InformationRetrievalAgent")
        """
        agent_map = {
            cls.INFORMATION_RETRIEVAL: "InformationRetrievalAgent",
            cls.DATA_OPERATIONS: "DataOperationsAgent",
            cls.PROBLEM_SOLVING: "ProblemSolvingAgent",
            cls.REPORT_GENERATION: "ReportGenerationAgent",
            cls.AUTOMATION: "AutomationAgent",
            cls.INDUSTRY_KNOWLEDGE: "IndustryKnowledgeAgent",
            cls.GENERAL_CHAT: "GeneralChatAgent",
        }
        return agent_map.get(category, "BaseAgent")
