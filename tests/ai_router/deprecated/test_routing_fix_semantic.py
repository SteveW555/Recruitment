"""
Quick test script to verify agent routing is working correctly.
Tests that queries are classified to appropriate agents, not just general chat.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from utils.ai_router.classifier import Classifier
from utils.ai_router.models.category import Category

def test_classifier():
    """Test that classifier properly routes queries to correct agents."""

    print("=" * 60)
    print("AI Router Classification Test")
    print("=" * 60)
    print()

    # Initialize classifier
    print("[1/2] Loading classifier...")
    try:
        classifier = Classifier(
            model_name="all-MiniLM-L6-v2",
            config_path="config/agents.json",
            confidence_threshold=0.65
        )
        print("[OK] Classifier loaded successfully\n")
    except Exception as e:
        print(f"[ERROR] Failed to load classifier: {e}")
        return False

    # Test queries for each category
    test_cases = [
        # Information Retrieval
        ("Show me all active jobs in London", Category.INFORMATION_RETRIEVAL),
        ("Find candidates with 5+ years sales experience", Category.INFORMATION_RETRIEVAL),

        # Data Operations
        ("Create an invoice for placement 12345", Category.DATA_OPERATIONS),
        ("Schedule an interview with Jane Doe", Category.DATA_OPERATIONS),

        # Problem Solving
        ("Why is our placement rate 15% lower than average?", Category.PROBLEM_SOLVING),
        ("How can we reduce candidate dropout?", Category.PROBLEM_SOLVING),

        # Report Generation
        ("Generate a quarterly performance report", Category.REPORT_GENERATION),
        ("Create a dashboard for top 10 clients", Category.REPORT_GENERATION),

        # Automation
        ("Automate the candidate welcome email process", Category.AUTOMATION),
        ("Create a workflow for interview reminders", Category.AUTOMATION),

        # Industry Knowledge
        ("What are the GDPR requirements for storing CVs?", Category.INDUSTRY_KNOWLEDGE),
        ("What are IR35 compliance regulations?", Category.INDUSTRY_KNOWLEDGE),

        # General Chat
        ("Hello", Category.GENERAL_CHAT),
        ("How are you?", Category.GENERAL_CHAT),
    ]

    print("[2/2] Testing classifications...")
    print()

    passed = 0
    failed = 0

    for query, expected_category in test_cases:
        decision = classifier.classify(query, "test-query-id")

        # Check if classification matches expected
        is_correct = decision.primary_category == expected_category

        # Display result
        status = "[PASS]" if is_correct else "[FAIL]"
        confidence_str = f"{decision.primary_confidence:.1%}"

        print(f"{status} Query: {query[:50]:<50}")
        print(f"  Expected: {expected_category.value:<25} Got: {decision.primary_category.value:<25} ({confidence_str})")

        if is_correct:
            passed += 1
        else:
            failed += 1
            print(f"  [WARNING] MISMATCH!")

        print()

    # Summary
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 60)

    if failed == 0:
        print("[SUCCESS] All tests passed! Agent routing is working correctly.")
        return True
    else:
        print(f"[FAIL] {failed} tests failed. Review classifier examples in config/agents.json")
        return False


if __name__ == "__main__":
    success = test_classifier()
    sys.exit(0 if success else 1)
