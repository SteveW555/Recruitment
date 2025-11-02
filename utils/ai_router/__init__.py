"""
AI Router Module

Intelligent query routing system that classifies user queries into categories
and routes them to specialized agent handlers.

Categories:
- Information Retrieval: Simple multi-source data lookup
- Problem Solving: Complex analysis and recommendations
- Report Generation: Visualization and presentation creation
- Automation: Workflow pipeline design
- Industry Knowledge: UK recruitment domain expertise
- General Chat: Casual conversation

Usage:
    from utils.ai_router import AIRouter

    router = AIRouter()
    response = await router.route_query(query_text, user_id, session_id)
"""

__version__ = "0.1.0"
__all__ = ["GroqClassifier", "AIRouter", "AgentRegistry"]

# Import main classes
from .groq_classifier import GroqClassifier
from .router import AIRouter
from .agent_registry import AgentRegistry
