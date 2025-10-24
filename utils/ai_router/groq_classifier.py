"""
GroqClassifier - Query classification using Groq LLM.

Uses Groq LLM (llama-3.3-70b-versatile) to intelligently classify
user queries by analyzing intent and context, providing more accurate
routing than semantic similarity alone.
"""

import json
import os
import sys
from typing import List, Dict, Optional

from .models.category import Category
from .models.routing_decision import RoutingDecision
from utils.groq.groq_client import GroqClient


class GroqClassifier:
    """
    LLM-based query classifier using Groq.

    Uses Groq's llama-3.3-70b-versatile model to analyze queries and
    route them to the most appropriate agent based on intent analysis.

    Achieves <500ms inference latency for classification.
    """

    def __init__(
        self,
        config_path: str = "config/agents.json",
        confidence_threshold: float = 0.65,
        routing_model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.3,
    ):
        """
        Initialize Groq-based classifier.

        Args:
            config_path: Path to agents.json configuration
            confidence_threshold: Minimum confidence for routing (default: 0.65)
            routing_model: Groq model for routing (default: llama-3.3-70b-versatile)
            temperature: Temperature for routing decisions (default: 0.3)
        """
        self.config_path = config_path
        self.confidence_threshold = confidence_threshold
        self.routing_model = routing_model
        self.temperature = temperature

        # Initialize Groq client
        print(f"[*] Initializing Groq classifier with model: {routing_model}...", file=sys.stderr)
        self.groq_client = GroqClient()
        print(f"[OK] Groq classifier ready", file=sys.stderr)

        # Load agent definitions from config
        self.available_agents: List[Dict[str, any]] = []
        self._load_agent_definitions()

    def _load_agent_definitions(self):
        """Load agent definitions from config/agents.json."""
        print(f"[*] Loading agent definitions from {self.config_path}...", file=sys.stderr)

        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}"
            )

        with open(self.config_path, "r") as f:
            config = json.load(f)

        # Convert config to agent definitions for Groq routing
        for category_str, agent_config in config.items():
            try:
                category = Category.from_string(category_str)

                self.available_agents.append({
                    "name": category.value,
                    "description": agent_config.get("description", ""),
                    "examples": agent_config.get("example_queries", []),
                })

            except ValueError as e:
                print(f"[WARNING] Invalid category {category_str}: {e}", file=sys.stderr)
                continue

        print(f"[OK] Loaded {len(self.available_agents)} agent definitions", file=sys.stderr)

    def classify(
        self,
        query_text: str,
        query_id: str,
        previous_agent: Optional[str] = None
    ) -> RoutingDecision:
        """
        Classify a query using Groq LLM.

        Args:
            query_text: User query to classify
            query_id: Unique query identifier
            previous_agent: Previous agent for context-aware routing

        Returns:
            RoutingDecision with category, confidence, and reasoning
        """
        # Build conversation history for context
        conversation_history = []
        if previous_agent:
            # Add context that this is a follow-up query
            conversation_history.append({
                "role": "system",
                "content": f"Previous query was handled by {previous_agent} agent. "
                          f"Consider if this is a follow-up query."
            })

        # Use Groq to route the query
        try:
            routing_result = self.groq_client.route_query_to_agent(
                query=query_text,
                available_agents=self.available_agents,
                conversation_history=conversation_history if conversation_history else None,
                routing_model=self.routing_model,
                temperature=self.temperature
            )

            # Extract results
            agent_name = routing_result.get("agent", "GENERAL_CHAT")
            confidence = routing_result.get("confidence", 0.5)
            reasoning = routing_result.get("reasoning", "")
            is_followup = routing_result.get("is_followup", False)

            # Convert agent name to Category
            try:
                primary_category = Category.from_string(agent_name)
            except ValueError:
                print(f"[WARNING] Invalid category from Groq: {agent_name}, using GENERAL_CHAT", file=sys.stderr)
                primary_category = Category.GENERAL_CHAT
                confidence = 0.5

            # Create routing decision
            decision = RoutingDecision(
                query_id=query_id,
                query_text=query_text,
                primary_category=primary_category,
                primary_confidence=confidence,
                fallback_category=Category.GENERAL_CHAT,
                fallback_confidence=1.0,
                all_scores={primary_category: confidence},
                reasoning=reasoning,
                context_boost=is_followup,
            )

            return decision

        except Exception as e:
            # Fallback to general chat on error
            print(f"[ERROR] Groq classification failed: {e}", file=sys.stderr)

            return RoutingDecision(
                query_id=query_id,
                query_text=query_text,
                primary_category=Category.GENERAL_CHAT,
                primary_confidence=0.5,
                fallback_category=Category.GENERAL_CHAT,
                fallback_confidence=1.0,
                all_scores={Category.GENERAL_CHAT: 0.5},
                reasoning=f"Groq error: {str(e)}",
                context_boost=False,
            )

    def get_category_examples(self, category: Category) -> List[str]:
        """
        Get example queries for a category.

        Args:
            category: Category to get examples for

        Returns:
            List of example queries
        """
        for agent in self.available_agents:
            if agent["name"] == category.value:
                return agent.get("examples", [])
        return []

    def __repr__(self) -> str:
        """String representation."""
        return f"GroqClassifier(model={self.routing_model}, agents={len(self.available_agents)})"
