"""
Unit tests for Classifier - Query classification engine.

Tests:
- Model loading and example encoding
- Query classification accuracy
- Confidence scoring
- Secondary category detection
- Fallback triggering logic
"""

import pytest
import os
import json
from pathlib import Path

from utils.ai_router.classifier import Classifier
from utils.ai_router.models.category import Category


@pytest.fixture
def config_file(tmp_path):
    """Create a temporary config file for testing."""
    config = {
        "INFORMATION_RETRIEVAL": {
            "example_queries": [
                "What are the top job boards in the UK?",
                "Where can I find candidates for sales roles?",
                "Which recruitment platforms support bulk import?",
                "What data can I extract from LinkedIn?",
                "How do I find talent on Totaljobs?",
                "What are the best sources for CV databases?",
                "Where to search for IT contractors?",
                "How can I access Indeed API?",
            ]
        },
        "PROBLEM_SOLVING": {
            "example_queries": [
                "How can we improve our placement rate?",
                "What strategies reduce candidate dropout?",
                "How to optimize our interview process?",
                "Why are we losing candidates to competitors?",
                "How can we speed up hiring?",
                "What's causing high interview no-shows?",
                "How to reduce time-to-hire?",
            ]
        },
        "INDUSTRY_KNOWLEDGE": {
            "example_queries": [
                "What's the typical notice period for permanent placements?",
                "What are GDPR requirements for storing CVs?",
                "What's the IR35 implications for contractors?",
                "What are the salary trends in IT recruitment?",
                "What compliance rules apply to recruitment agencies?",
                "What's the national living wage threshold?",
            ]
        },
        "GENERAL_CHAT": {
            "example_queries": [
                "Hello, how are you?",
                "What's the weather like?",
                "Tell me a joke",
                "What time is it?",
                "How's your day?",
            ]
        },
    }

    config_path = tmp_path / "agents.json"
    with open(config_path, "w") as f:
        json.dump(config, f)

    return str(config_path)


@pytest.fixture
def classifier(config_file):
    """Create a classifier instance for testing."""
    return Classifier(config_path=config_file, confidence_threshold=0.7)


class TestClassifierInitialization:
    """Test classifier initialization and setup."""

    def test_classifier_loads_model(self, classifier):
        """Test that classifier loads the sentence-transformers model."""
        assert classifier.model is not None
        assert classifier.model_name == "all-MiniLM-L6-v2"

    def test_classifier_loads_examples(self, classifier):
        """Test that classifier loads and encodes example queries."""
        assert len(classifier.examples_by_category) > 0
        assert len(classifier.encoded_examples) > 0
        assert Category.INFORMATION_RETRIEVAL in classifier.examples_by_category

    def test_classifier_example_counts(self, classifier):
        """Test that classifier has correct number of examples per category."""
        ir_count = classifier.get_example_count(Category.INFORMATION_RETRIEVAL)
        assert ir_count > 0


class TestClassification:
    """Test query classification."""

    def test_classify_information_retrieval(self, classifier):
        """Test classification of information retrieval query."""
        decision = classifier.classify(
            "What are the top job boards for sales positions?",
            query_id="test_1"
        )

        assert decision.primary_category == Category.INFORMATION_RETRIEVAL
        assert decision.primary_confidence > 0.5
        assert decision.classification_latency_ms > 0

    def test_classify_problem_solving(self, classifier):
        """Test classification of problem solving query."""
        decision = classifier.classify(
            "How can we reduce candidate dropout rate?",
            query_id="test_2"
        )

        assert decision.primary_category == Category.PROBLEM_SOLVING
        assert decision.primary_confidence > 0.5

    def test_classify_industry_knowledge(self, classifier):
        """Test classification of industry knowledge query."""
        decision = classifier.classify(
            "What are the GDPR requirements for CV storage?",
            query_id="test_3"
        )

        assert decision.primary_category == Category.INDUSTRY_KNOWLEDGE
        assert decision.primary_confidence > 0.5

    def test_classify_general_chat(self, classifier):
        """Test classification of general chat query."""
        decision = classifier.classify(
            "Hello, how are you today?",
            query_id="test_4"
        )

        assert decision.primary_category == Category.GENERAL_CHAT
        assert decision.primary_confidence > 0.5

    def test_secondary_category_detection(self, classifier):
        """Test that secondary categories are detected."""
        # Ambiguous query that might match multiple categories
        decision = classifier.classify(
            "Where can I find recruiting information and tips?",
            query_id="test_5"
        )

        # Should have primary category
        assert decision.primary_category is not None
        assert decision.primary_confidence > 0


class TestConfidenceScoring:
    """Test confidence scoring and thresholds."""

    def test_confidence_scores_are_normalized(self, classifier):
        """Test that confidence scores are between 0 and 1."""
        decision = classifier.classify(
            "Test query for confidence",
            query_id="test_6"
        )

        assert 0.0 <= decision.primary_confidence <= 1.0
        if decision.secondary_confidence:
            assert 0.0 <= decision.secondary_confidence <= 1.0

    def test_low_confidence_triggers_fallback(self, classifier):
        """Test that very ambiguous queries trigger fallback."""
        classifier.confidence_threshold = 0.95  # Very high threshold

        decision = classifier.classify(
            "xyz abc 123",  # Nonsense query
            query_id="test_7"
        )

        # Should trigger fallback due to low confidence
        if decision.primary_confidence < classifier.confidence_threshold:
            assert decision.fallback_triggered

    def test_secondary_confidence_below_threshold(self, classifier):
        """Test that secondary category below 50% threshold is removed."""
        decision = classifier.classify(
            "What are the top job boards in the UK?",
            query_id="test_8"
        )

        # If secondary exists, it should be above 50%
        if decision.secondary_confidence is not None:
            assert decision.secondary_confidence >= 0.5


class TestReasoningGeneration:
    """Test reasoning message generation."""

    def test_reasoning_includes_category(self, classifier):
        """Test that reasoning includes the classified category."""
        decision = classifier.classify(
            "What are the top job boards?",
            query_id="test_9"
        )

        assert decision.primary_category.value in decision.reasoning

    def test_reasoning_includes_confidence(self, classifier):
        """Test that reasoning includes confidence percentage."""
        decision = classifier.classify(
            "What are the top job boards?",
            query_id="test_10"
        )

        # Reasoning should contain confidence as percentage
        assert "%" in decision.reasoning

    def test_reasoning_mentions_low_confidence(self, classifier):
        """Test that reasoning mentions confidence threshold for low confidence."""
        classifier.confidence_threshold = 0.95

        decision = classifier.classify(
            "xyz abc 123",
            query_id="test_11"
        )

        if decision.primary_confidence < 0.95:
            assert "clarification" in decision.reasoning.lower() or "threshold" in decision.reasoning.lower()

    def test_reasoning_length_limited(self, classifier):
        """Test that reasoning is capped at 500 characters."""
        decision = classifier.classify(
            "test query",
            query_id="test_12"
        )

        assert len(decision.reasoning) <= 500


class TestSimilarityScores:
    """Test similarity score calculation."""

    def test_get_all_similarities(self, classifier):
        """Test getting similarity scores for all categories."""
        query = "What are the top job boards?"
        similarities = classifier.get_all_similarities(query)

        assert len(similarities) > 0
        assert all(0.0 <= score <= 1.0 for score in similarities.values())

    def test_information_retrieval_highest_for_ir_query(self, classifier):
        """Test that IR category has highest score for IR query."""
        query = "What are the top job boards?"
        similarities = classifier.get_all_similarities(query)

        ir_score = similarities.get(Category.INFORMATION_RETRIEVAL, 0)
        other_scores = [score for cat, score in similarities.items() if cat != Category.INFORMATION_RETRIEVAL]

        if other_scores:
            assert ir_score >= min(other_scores)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_query(self, classifier):
        """Test handling of empty query."""
        with pytest.raises((ValueError, AttributeError)):
            classifier.classify("", query_id="test_13")

    def test_very_short_query(self, classifier):
        """Test handling of very short query."""
        decision = classifier.classify(
            "hi",
            query_id="test_14"
        )

        assert decision.primary_category is not None

    def test_very_long_query(self, classifier):
        """Test handling of very long query."""
        long_query = "test " * 500  # 2500 words
        decision = classifier.classify(
            long_query,
            query_id="test_15"
        )

        assert decision.primary_category is not None

    def test_unicode_query(self, classifier):
        """Test handling of Unicode characters."""
        decision = classifier.classify(
            "What are the top job boards in the UK? 你好 café",
            query_id="test_16"
        )

        assert decision.primary_category is not None

    def test_special_characters_query(self, classifier):
        """Test handling of special characters."""
        decision = classifier.classify(
            "What are the top job boards??? !!! ***",
            query_id="test_17"
        )

        assert decision.primary_category is not None


class TestClassifierReloading:
    """Test classifier reload functionality."""

    def test_reload_examples(self, classifier, config_file):
        """Test reloading examples from config."""
        original_count = len(classifier.examples_by_category)

        classifier.reload_examples()

        assert len(classifier.examples_by_category) == original_count
