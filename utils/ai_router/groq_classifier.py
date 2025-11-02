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
        prompt_path: str = "prompts/ai_router_classification.json"
    ):
        """
        Initialize Groq-based classifier.

        Args:
            config_path: Path to agents.json configuration
            confidence_threshold: Minimum confidence for routing (default: 0.65)
            routing_model: Groq model for routing (default: llama-3.3-70b-versatile)
            temperature: Temperature for routing decisions (default: 0.3)
            prompt_path: Path to classification prompt JSON file
        """
        self.config_path = config_path
        self.confidence_threshold = confidence_threshold
        self.routing_model = routing_model
        self.temperature = temperature
        self.prompt_path = prompt_path

        # Initialize Groq client
        print(f"[*] Initializing Groq classifier with model: {routing_model}...", file=sys.stderr)
        self.groq_client = GroqClient()
        print(f"[OK] Groq classifier ready", file=sys.stderr)

        # Load agent definitions from config
        self.available_agents: List[Dict[str, any]] = []
        self._load_agent_definitions()

        # Load classification prompt template
        self.prompt_template: str = ""
        self._load_prompt_template()

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

    def _load_prompt_template(self):
        """Load classification prompt template from JSON file."""
        print(f"[*] Loading classification prompt from {self.prompt_path}...", file=sys.stderr)

        if not os.path.exists(self.prompt_path):
            print(f"[WARNING] Prompt file not found: {self.prompt_path}, using fallback", file=sys.stderr)
            # Fallback to hardcoded prompt if file not found
            self.prompt_template = """You are a query classification system for a recruitment agency AI assistant.

Your task is to analyze user queries and classify them into ONE of the following categories:

{categories_text}

**Instructions:**
1. Analyze the user's query intent and context
2. Select the MOST APPROPRIATE category
3. Provide a confidence score (0.0 to 1.0)
4. Explain your reasoning briefly

**CRITICAL: Return ONLY valid JSON (no markdown, no explanation, no extra text):**
{{
    "category": "CATEGORY_NAME",
    "confidence": 0.85,
    "reasoning": "Brief explanation of why this category was chosen"
}}

**Guidelines:**
- If unclear or casual greeting/chat, use GENERAL_CHAT
- For queries about finding information (salaries, job boards, candidates), use INFORMATION_RETRIEVAL
- For complex problem analysis with recommendations, use PROBLEM_SOLVING
- For workflow/automation design requests, use AUTOMATION
- For UK recruitment regulations/compliance/best practices, use INDUSTRY_KNOWLEDGE
- For generating reports/charts/dashboards, use REPORT_GENERATION
- For system operations (CRUD on database), use DATA_OPERATIONS"""
            return

        with open(self.prompt_path, "r") as f:
            prompt_config = json.load(f)

        self.prompt_template = prompt_config.get("system_prompt", "")
        print(f"[OK] Loaded prompt template (version {prompt_config.get('version', 'unknown')})", file=sys.stderr)

    def _build_classification_prompt(self) -> str:
        """
        Build system prompt for Groq classification.

        Returns:
            System prompt describing categories and classification task
        """
        category_descriptions = []
        for agent in self.available_agents:
            # Get category enum to access description
            try:
                category = Category.from_string(agent["name"])
                description = Category.get_description(category)
                examples = agent.get("examples", [])[:3]  # Include up to 3 examples

                category_info = f"- **{agent['name']}**: {description}"
                if examples:
                    category_info += f"\n  Examples: {', '.join([f'"{ex}"' for ex in examples])}"
                category_descriptions.append(category_info)
            except ValueError:
                continue

        categories_text = "\n".join(category_descriptions)

        # Use loaded prompt template and replace variable placeholder
        return self.prompt_template.format(categories_text=categories_text)

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
        import time

        # Start latency tracking
        start_time = time.time()

        # Build classification system prompt
        system_prompt = self._build_classification_prompt()

        # Add context about previous agent if available
        user_message = query_text
        if previous_agent:
            user_message = f"[Previous agent: {previous_agent}]\n\nQuery: {query_text}"

        try:
            # Call Groq for classification using complete() method
            from utils.groq.groq_client import CompletionConfig

            config = CompletionConfig(
                model=self.routing_model,
                temperature=self.temperature,
                max_tokens=200
            )

            response = self.groq_client.complete(
                prompt=user_message,
                system_prompt=system_prompt,
                config=config
            )

            # Parse JSON response from GroqResponse.content
            result = self.groq_client.validate_json_response(response.content)
            if result is None:
                raise ValueError("Failed to parse JSON response from Groq")

            # Extract classification results
            category_name = result.get("category", "GENERAL_CHAT")
            confidence = float(result.get("confidence", 0.5))
            reasoning = result.get("reasoning", "No reasoning provided")

            # Convert to Category enum
            try:
                primary_category = Category.from_string(category_name)
            except ValueError:
                print(f"[WARNING] Invalid category from Groq: {category_name}, using GENERAL_CHAT", file=sys.stderr)
                primary_category = Category.GENERAL_CHAT
                confidence = 0.5
                reasoning = f"Invalid category '{category_name}', defaulted to GENERAL_CHAT"

            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)

            # Determine if fallback should be triggered
            fallback_triggered = confidence < self.confidence_threshold

            # Create routing decision with ONLY valid parameters
            decision = RoutingDecision(
                query_id=query_id,
                primary_category=primary_category,
                primary_confidence=confidence,
                reasoning=reasoning,
                classification_latency_ms=latency_ms,
                fallback_triggered=fallback_triggered,
            )

            # Attach system prompt for debugging/logging (not part of RoutingDecision model)
            decision.system_prompt = system_prompt  # Add as attribute for transparency
            print(f"[DEBUG GroqClassifier] Attached system_prompt to decision (length: {len(system_prompt)} chars)", file=sys.stderr)

            return decision

        except Exception as e:
            # Calculate latency even for errors
            latency_ms = int((time.time() - start_time) * 1000)

            # Fallback to general chat on error
            print(f"[ERROR] Groq classification failed: {e}", file=sys.stderr)

            decision = RoutingDecision(
                query_id=query_id,
                primary_category=Category.GENERAL_CHAT,
                primary_confidence=0.5,
                reasoning=f"Classification error: {str(e)}",
                classification_latency_ms=latency_ms,
                fallback_triggered=True,
            )

            # Attach system prompt even for errors (for debugging)
            decision.system_prompt = system_prompt if 'system_prompt' in locals() else "Error: System prompt not built"

            return decision

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
