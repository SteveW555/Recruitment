"""
Classifier - Query classification using sentence-transformers.

Uses semantic similarity with pre-encoded example queries to classify
user inputs into one of six categories with confidence scoring.
"""

import json
import os
import time
from typing import List, Dict, Tuple, Optional
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer, util

from .models.category import Category
from .models.routing_decision import RoutingDecision


class Classifier:
    """
    Semantic similarity-based query classifier.

    Uses sentence-transformers (all-MiniLM-L6-v2) to encode queries and
    compare them against example queries for each category.

    Achieves <100ms inference latency for classification.
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        config_path: str = "config/agents.json",
        confidence_threshold: float = 0.7,
    ):
        """
        Initialize classifier with sentence-transformers model.

        Args:
            model_name: Sentence-transformers model name (default: all-MiniLM-L6-v2)
            config_path: Path to agents.json configuration
            confidence_threshold: Minimum confidence for routing (default: 0.7)
        """
        self.model_name = model_name
        self.config_path = config_path
        self.confidence_threshold = confidence_threshold

        # Load sentence-transformers model
        print(f"Loading sentence-transformers model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"[OK] Model loaded successfully")

        # Load example queries from config
        self.examples_by_category: Dict[Category, List[str]] = {}
        self.encoded_examples: Dict[Category, np.ndarray] = {}
        self._load_examples()

    def _load_examples(self):
        """Load example queries from config/agents.json and encode them."""
        print(f"Loading example queries from {self.config_path}...")

        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}. "
                f"Please create it with example queries for each category."
            )

        with open(self.config_path, "r") as f:
            config = json.load(f)

        # Extract example queries for each category
        for category_str, agent_config in config.items():
            try:
                category = Category.from_string(category_str)
                example_queries = agent_config.get("example_queries", [])

                if not example_queries:
                    print(f"[WARNING] No example queries for {category.value}")
                    continue

                self.examples_by_category[category] = example_queries

                # Encode example queries
                print(f"  Encoding {len(example_queries)} examples for {category.value}...")
                encoded = self.model.encode(example_queries, convert_to_tensor=True)
                self.encoded_examples[category] = encoded

            except ValueError as e:
                print(f"[WARNING] Invalid category {category_str}: {e}")
                continue

        print(f"[OK] Loaded and encoded examples for {len(self.examples_by_category)} categories")

    def classify(self, query_text: str, query_id: str) -> RoutingDecision:
        """
        Classify a query into a category with confidence scoring.

        Uses cosine similarity between query embedding and example embeddings
        to determine the best matching category.

        Args:
            query_text: User query text
            query_id: Query ID for the routing decision

        Returns:
            RoutingDecision with primary/secondary categories and confidence scores
        """
        start_time = time.time()

        # Encode query
        query_embedding = self.model.encode(query_text, convert_to_tensor=True)

        # Calculate similarity with all example queries
        category_scores: Dict[Category, float] = {}

        for category, example_embeddings in self.encoded_examples.items():
            # Compute cosine similarity with all examples for this category
            similarities = util.cos_sim(query_embedding, example_embeddings)[0]

            # Use max similarity as category score
            # Clamp to [0, 1] to handle floating point precision issues
            max_similarity = float(torch.max(similarities)) if len(similarities) > 0 else 0.0
            max_similarity = max(0.0, min(1.0, max_similarity))
            category_scores[category] = max_similarity

        # Sort categories by score (descending)
        sorted_categories = sorted(
            category_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Get primary and secondary categories
        primary_category, primary_confidence = sorted_categories[0]
        secondary_category, secondary_confidence = sorted_categories[1] if len(sorted_categories) > 1 else (None, None)

        # Only include secondary if confidence is above 50% threshold
        if secondary_confidence and secondary_confidence < 0.5:
            secondary_category = None
            secondary_confidence = None

        # Calculate classification latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Check if fallback should be triggered (confidence < threshold)
        fallback_triggered = primary_confidence < self.confidence_threshold

        # Generate reasoning
        reasoning = self._generate_reasoning(
            query_text,
            primary_category,
            primary_confidence,
            secondary_category,
            secondary_confidence
        )

        # Create routing decision
        decision = RoutingDecision(
            query_id=query_id,
            primary_category=primary_category,
            primary_confidence=primary_confidence,
            secondary_category=secondary_category,
            secondary_confidence=secondary_confidence,
            reasoning=reasoning,
            classification_latency_ms=latency_ms,
            fallback_triggered=fallback_triggered,
            user_override=False,
        )

        return decision

    def _generate_reasoning(
        self,
        query_text: str,
        primary_category: Category,
        primary_confidence: float,
        secondary_category: Optional[Category],
        secondary_confidence: Optional[float]
    ) -> str:
        """
        Generate human-readable reasoning for classification decision.

        Args:
            query_text: Original query
            primary_category: Primary classified category
            primary_confidence: Primary confidence score
            secondary_category: Secondary category (if any)
            secondary_confidence: Secondary confidence score (if any)

        Returns:
            Reasoning string
        """
        # Truncate query for reasoning (max 50 chars)
        query_preview = query_text[:50] + "..." if len(query_text) > 50 else query_text

        reasoning = (
            f"Query '{query_preview}' classified as {primary_category.value} "
            f"with {primary_confidence:.2%} confidence. "
        )

        if secondary_category and secondary_confidence:
            reasoning += (
                f"Secondary match: {secondary_category.value} ({secondary_confidence:.2%})."
            )

        if primary_confidence < self.confidence_threshold:
            reasoning += f" Below confidence threshold ({self.confidence_threshold:.0%}), requesting clarification."

        return reasoning[:500]  # Trim to 500 chars max

    def get_all_similarities(self, query_text: str) -> Dict[Category, float]:
        """
        Get similarity scores for all categories (for debugging/analysis).

        Args:
            query_text: Query text

        Returns:
            Dictionary mapping categories to similarity scores
        """
        query_embedding = self.model.encode(query_text, convert_to_tensor=True)

        category_scores = {}
        for category, example_embeddings in self.encoded_examples.items():
            similarities = util.cos_sim(query_embedding, example_embeddings)[0]
            max_similarity = float(torch.max(similarities)) if len(similarities) > 0 else 0.0
            category_scores[category] = max_similarity

        return category_scores

    def get_example_count(self, category: Category) -> int:
        """
        Get number of example queries for a category.

        Args:
            category: Category to check

        Returns:
            Number of examples
        """
        return len(self.examples_by_category.get(category, []))

    def reload_examples(self):
        """Reload example queries from config (useful after config changes)."""
        self._load_examples()

    def __repr__(self) -> str:
        """String representation."""
        categories_loaded = len(self.examples_by_category)
        return (
            f"Classifier(model={self.model_name}, "
            f"categories={categories_loaded}, "
            f"threshold={self.confidence_threshold})"
        )


# Fix import issue for torch (sentence-transformers internally uses torch)
try:
    import torch
except ImportError:
    print("[WARNING] PyTorch not found. Install with: pip install torch")
    torch = None
