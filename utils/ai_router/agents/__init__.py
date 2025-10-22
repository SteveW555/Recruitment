"""
Agent implementations for handling different query categories.

Each agent is specialized for a specific category and implements
the BaseAgent interface for consistent routing behavior.
"""

from .base_agent import BaseAgent, AgentRequest, AgentResponse
from .information_retrieval_agent import InformationRetrievalAgent
from .problem_solving_agent import ProblemSolvingAgent
from .report_generation_agent import ReportGenerationAgent
from .automation_agent import AutomationAgent
from .industry_knowledge_agent import IndustryKnowledgeAgent
from .general_chat_agent import GeneralChatAgent

__all__ = [
    "BaseAgent",
    "AgentRequest",
    "AgentResponse",
    "InformationRetrievalAgent",
    "ProblemSolvingAgent",
    "ReportGenerationAgent",
    "AutomationAgent",
    "IndustryKnowledgeAgent",
    "GeneralChatAgent",
]
