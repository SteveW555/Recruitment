#!/usr/bin/env python3
"""
Test AI Router query classification without running the full router server.

Usage:
    # Single query test
    python test_routing.py "What are current salaries for developers?"

    # With previous agent context
    python test_routing.py "Tell me more" --previous-agent INFORMATION_RETRIEVAL

    # With staff role context
    python test_routing.py "What are GDPR requirements?" --staff-role person_4_compliance_wellbeing

    # Batch test from file
    python test_routing.py --file queries.txt

    # Custom configuration
    python test_routing.py "query" --threshold 0.7 --model llama-3-70b-8192
"""

import argparse
import os
import sys
import time
from typing import List, Optional

# Add parent directories to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..", "..", ".."))
sys.path.insert(0, project_root)

from utils.ai_router.groq_classifier import GroqClassifier
from utils.ai_router.models.category import Category


def print_separator():
    """Print a visual separator line."""
    print("\n" + "=" * 80 + "\n")


def print_decision(query_text: str, decision, staff_role: Optional[str] = None):
    """
    Print routing decision in formatted output.

    Args:
        query_text: The original query
        decision: RoutingDecision object
        staff_role: Optional staff role context
    """
    print(f"Query: {query_text}")
    if staff_role:
        print(f"Staff Role: {staff_role}")
    print(f"\nCategory: {decision.primary_category.value}")
    print(f"Confidence: {decision.primary_confidence:.3f}")
    print(f"Fallback Triggered: {decision.fallback_triggered}")
    print(f"Classification Latency: {decision.classification_latency_ms}ms")
    print(f"\nReasoning:\n{decision.reasoning}")
    print_separator()


def test_single_query(
    classifier: GroqClassifier,
    query_text: str,
    previous_agent: Optional[str] = None,
    staff_role: Optional[str] = None,
):
    """
    Test a single query and print results.

    Args:
        classifier: GroqClassifier instance
        query_text: Query to test
        previous_agent: Optional previous agent for context
        staff_role: Optional staff role context
    """
    print_separator()
    print("TESTING SINGLE QUERY")
    print_separator()

    query_id = f"test_{int(time.time() * 1000)}"

    try:
        decision = classifier.classify(
            query_text=query_text,
            query_id=query_id,
            previous_agent=previous_agent,
        )
        print_decision(query_text, decision, staff_role)

    except Exception as e:
        print(f"ERROR: Classification failed: {e}")
        import traceback
        traceback.print_exc()


def test_batch_queries(
    classifier: GroqClassifier,
    file_path: str,
    staff_role: Optional[str] = None,
):
    """
    Test multiple queries from a file.

    Args:
        classifier: GroqClassifier instance
        file_path: Path to file containing queries (one per line)
        staff_role: Optional staff role context
    """
    print_separator()
    print(f"TESTING BATCH QUERIES FROM: {file_path}")
    print_separator()

    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        queries = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not queries:
        print("ERROR: No queries found in file")
        return

    print(f"Found {len(queries)} queries to test\n")

    results = []
    total_latency = 0

    for i, query_text in enumerate(queries, 1):
        query_id = f"batch_test_{i}"

        try:
            decision = classifier.classify(
                query_text=query_text,
                query_id=query_id,
            )

            results.append({
                "query": query_text,
                "category": decision.primary_category,
                "confidence": decision.primary_confidence,
                "fallback": decision.fallback_triggered,
                "latency": decision.classification_latency_ms,
            })

            total_latency += decision.classification_latency_ms

            print_decision(query_text, decision, staff_role)

        except Exception as e:
            print(f"ERROR: Query {i} failed: {e}")
            continue

    # Summary
    print_separator()
    print("BATCH TEST SUMMARY")
    print_separator()

    print(f"Total queries: {len(results)}")
    print(f"Successful: {len(results)}")
    print(f"Average latency: {total_latency / len(results):.0f}ms")
    print(f"Total latency: {total_latency}ms")

    # Category distribution
    category_counts = {}
    for result in results:
        cat = result["category"].value
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print("\nCategory Distribution:")
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        percentage = (count / len(results)) * 100
        print(f"  {category}: {count} ({percentage:.1f}%)")

    # Confidence statistics
    confidences = [r["confidence"] for r in results]
    avg_confidence = sum(confidences) / len(confidences)
    min_confidence = min(confidences)
    max_confidence = max(confidences)

    print(f"\nConfidence Statistics:")
    print(f"  Average: {avg_confidence:.3f}")
    print(f"  Min: {min_confidence:.3f}")
    print(f"  Max: {max_confidence:.3f}")

    # Fallback rate
    fallback_count = sum(1 for r in results if r["fallback"])
    fallback_rate = (fallback_count / len(results)) * 100
    print(f"\nFallback Rate: {fallback_count}/{len(results)} ({fallback_rate:.1f}%)")

    print_separator()


def validate_staff_role(staff_role: str) -> bool:
    """
    Validate that staff role is one of the 5 defined roles.

    Args:
        staff_role: Staff role to validate

    Returns:
        True if valid, False otherwise
    """
    valid_roles = [
        "person_1_managing_director",
        "person_2_temp_consultant",
        "person_3_resourcer_admin_tech",
        "person_4_compliance_wellbeing",
        "person_5_finance_training",
    ]

    if staff_role not in valid_roles:
        print(f"ERROR: Invalid staff role: {staff_role}")
        print(f"Valid roles: {', '.join(valid_roles)}")
        return False

    return True


def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(
        description="Test AI Router query classification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single query
  python test_routing.py "What are current salaries for developers?"

  # With previous agent context
  python test_routing.py "Tell me more" --previous-agent INFORMATION_RETRIEVAL

  # With staff role
  python test_routing.py "GDPR requirements?" --staff-role person_4_compliance_wellbeing

  # Batch test
  python test_routing.py --file queries.txt

  # Custom configuration
  python test_routing.py "query" --threshold 0.7 --model llama-3-70b-8192 --temperature 0.2
        """,
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query text to classify (for single query test)",
    )

    parser.add_argument(
        "--file",
        "-f",
        help="File containing queries (one per line) for batch testing",
    )

    parser.add_argument(
        "--previous-agent",
        help="Previous agent for context-aware routing",
    )

    parser.add_argument(
        "--staff-role",
        help="Staff role context (person_1_managing_director, person_2_temp_consultant, etc.)",
    )

    parser.add_argument(
        "--config",
        default="config/agents.json",
        help="Path to agents.json configuration (default: config/agents.json)",
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=0.65,
        help="Confidence threshold for routing (default: 0.65)",
    )

    parser.add_argument(
        "--model",
        default="llama-3.3-70b-versatile",
        help="Groq model for classification (default: llama-3.3-70b-versatile)",
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.3,
        help="Temperature for routing decisions (default: 0.3)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.query and not args.file:
        parser.print_help()
        print("\nERROR: Either provide a query or use --file for batch testing")
        sys.exit(1)

    if args.query and args.file:
        print("ERROR: Cannot specify both query and --file")
        sys.exit(1)

    if args.staff_role and not validate_staff_role(args.staff_role):
        sys.exit(1)

    # Initialize classifier
    print("Initializing GroqClassifier...")
    print(f"  Config: {args.config}")
    print(f"  Threshold: {args.threshold}")
    print(f"  Model: {args.model}")
    print(f"  Temperature: {args.temperature}")

    try:
        classifier = GroqClassifier(
            config_path=args.config,
            confidence_threshold=args.threshold,
            routing_model=args.model,
            temperature=args.temperature,
        )
        print("Classifier initialized successfully\n")

    except Exception as e:
        print(f"ERROR: Failed to initialize classifier: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Run test
    if args.query:
        test_single_query(
            classifier=classifier,
            query_text=args.query,
            previous_agent=args.previous_agent,
            staff_role=args.staff_role,
        )
    else:
        test_batch_queries(
            classifier=classifier,
            file_path=args.file,
            staff_role=args.staff_role,
        )


if __name__ == "__main__":
    main()
