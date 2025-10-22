#!/usr/bin/env python3
"""
AI Router Classifier Test CLI

Interactive command-line tool for testing the query classification system.
Tests the sentence-transformers model and provides detailed similarity scores.

Usage:
    python test_classifier.py
    python test_classifier.py --query "What are GDPR requirements?"
    python test_classifier.py --batch test_queries.txt
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.ai_router.classifier import Classifier
from utils.ai_router.models.category import Category


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text: str):
    """Print formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_classification_result(query: str, classifier: Classifier, verbose: bool = False):
    """
    Print classification result with confidence scores.

    Args:
        query: Query text to classify
        classifier: Classifier instance
        verbose: Show all category scores
    """
    # Classify query
    result = classifier.classify(query, query_id="cli_test")

    # Print query
    print(f"{Colors.BOLD}Query:{Colors.END} {query}")
    print()

    # Print primary classification
    confidence_color = (
        Colors.GREEN if result.primary_confidence >= 0.8 else
        Colors.YELLOW if result.primary_confidence >= 0.6 else
        Colors.RED
    )

    print(f"{Colors.BOLD}Primary Classification:{Colors.END}")
    print(f"  Category:   {Colors.CYAN}{result.primary_category.value}{Colors.END}")
    print(f"  Confidence: {confidence_color}{result.primary_confidence:.2%}{Colors.END}")
    print(f"  Latency:    {result.classification_latency_ms}ms")

    # Print secondary classification if exists
    if result.secondary_category:
        print(f"\n{Colors.BOLD}Secondary Match:{Colors.END}")
        print(f"  Category:   {result.secondary_category.value}")
        print(f"  Confidence: {result.secondary_confidence:.2%}")

    # Print fallback warning
    if result.fallback_triggered:
        print(f"\n{Colors.RED}{Colors.BOLD}[!] FALLBACK TRIGGERED{Colors.END}")
        print(f"  Confidence below threshold ({classifier.confidence_threshold:.0%})")

    # Print reasoning
    print(f"\n{Colors.BOLD}Reasoning:{Colors.END}")
    print(f"  {result.reasoning}")

    # Verbose mode: show all category scores
    if verbose:
        print(f"\n{Colors.BOLD}All Category Scores:{Colors.END}")
        all_scores = classifier.get_all_similarities(query)
        sorted_scores = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)

        for i, (category, score) in enumerate(sorted_scores, 1):
            bar_length = int(score * 40)
            bar = '#' * bar_length + '-' * (40 - bar_length)

            # Highlight primary category
            if category == result.primary_category:
                print(f"  {Colors.GREEN}> {category.value:25} {score:.2%} {bar}{Colors.END}")
            else:
                print(f"    {category.value:25} {score:.2%} {bar}")

    print(f"\n{Colors.BLUE}{'-' * 70}{Colors.END}")


def run_interactive_mode(classifier: Classifier, verbose: bool = False):
    """
    Run interactive CLI mode.

    Args:
        classifier: Classifier instance
        verbose: Show all category scores
    """
    print_header("AI Router Classifier - Interactive Mode")

    print(f"{Colors.BOLD}Model:{Colors.END} {classifier.model_name}")
    print(f"{Colors.BOLD}Categories Loaded:{Colors.END} {len(classifier.examples_by_category)}")
    print(f"{Colors.BOLD}Confidence Threshold:{Colors.END} {classifier.confidence_threshold:.0%}")
    print()

    # Show example counts
    print(f"{Colors.BOLD}Example Queries Per Category:{Colors.END}")
    for category in Category.all_categories():
        count = classifier.get_example_count(category)
        status = f"{Colors.GREEN}[OK]{Colors.END}" if count > 0 else f"{Colors.RED}[X]{Colors.END}"
        print(f"  {status} {category.value:25} {count} examples")

    print(f"\n{Colors.CYAN}Enter queries to classify (or 'quit' to exit){Colors.END}")
    print(f"{Colors.CYAN}Commands: 'verbose on/off', 'help', 'examples', 'quit'{Colors.END}\n")

    while True:
        try:
            # Get user input
            query = input(f"{Colors.BOLD}Query>{Colors.END} ").strip()

            if not query:
                continue

            # Handle commands
            if query.lower() in ['quit', 'exit', 'q']:
                print(f"\n{Colors.GREEN}Goodbye!{Colors.END}")
                break

            elif query.lower() == 'help':
                print(f"\n{Colors.BOLD}Available Commands:{Colors.END}")
                print("  verbose on/off - Toggle detailed category scores")
                print("  examples       - Show example queries for each category")
                print("  help           - Show this help message")
                print("  quit           - Exit the program\n")
                continue

            elif query.lower() == 'verbose on':
                verbose = True
                print(f"{Colors.GREEN}[OK] Verbose mode enabled{Colors.END}\n")
                continue

            elif query.lower() == 'verbose off':
                verbose = False
                print(f"{Colors.GREEN}[OK] Verbose mode disabled{Colors.END}\n")
                continue

            elif query.lower() == 'examples':
                print(f"\n{Colors.BOLD}Example Queries by Category:{Colors.END}\n")
                for category in Category.all_categories():
                    examples = classifier.examples_by_category.get(category, [])
                    print(f"{Colors.CYAN}{category.value}:{Colors.END}")
                    for i, example in enumerate(examples[:3], 1):
                        print(f"  {i}. {example}")
                    if len(examples) > 3:
                        print(f"  ... and {len(examples) - 3} more")
                    print()
                continue

            # Classify query
            print()
            print_classification_result(query, classifier, verbose)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.GREEN}Goodbye!{Colors.END}")
            break
        except Exception as e:
            print(f"\n{Colors.RED}Error: {e}{Colors.END}\n")


def run_single_query(query: str, classifier: Classifier, verbose: bool = False):
    """
    Classify a single query.

    Args:
        query: Query text
        classifier: Classifier instance
        verbose: Show all category scores
    """
    print_header("AI Router Classifier - Single Query")
    print_classification_result(query, classifier, verbose)


def run_batch_mode(file_path: str, classifier: Classifier, verbose: bool = False):
    """
    Classify queries from a file (one per line).

    Args:
        file_path: Path to file with queries
        classifier: Classifier instance
        verbose: Show all category scores
    """
    print_header("AI Router Classifier - Batch Mode")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            queries = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

        print(f"{Colors.BOLD}Processing {len(queries)} queries from {file_path}{Colors.END}\n")

        # Track statistics
        category_counts = {cat: 0 for cat in Category.all_categories()}
        low_confidence_count = 0
        total_latency = 0

        for i, query in enumerate(queries, 1):
            print(f"\n{Colors.BOLD}[{i}/{len(queries)}]{Colors.END}")
            result = classifier.classify(query, query_id=f"batch_{i}")
            print_classification_result(query, classifier, verbose)

            # Update stats
            category_counts[result.primary_category] += 1
            if result.fallback_triggered:
                low_confidence_count += 1
            total_latency += result.classification_latency_ms

        # Print summary
        print_header("Batch Summary")
        print(f"{Colors.BOLD}Total Queries:{Colors.END} {len(queries)}")
        print(f"{Colors.BOLD}Average Latency:{Colors.END} {total_latency / len(queries):.1f}ms")
        print(f"{Colors.BOLD}Low Confidence:{Colors.END} {low_confidence_count} ({low_confidence_count/len(queries):.1%})")
        print(f"\n{Colors.BOLD}Category Distribution:{Colors.END}")

        for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                percentage = count / len(queries)
                bar_length = int(percentage * 40)
                bar = '#' * bar_length
                print(f"  {category.value:25} {count:3} ({percentage:.1%}) {bar}")

    except FileNotFoundError:
        print(f"{Colors.RED}Error: File not found: {file_path}{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Router Classifier Test CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python test_classifier.py

  # Single query
  python test_classifier.py --query "What are GDPR requirements?"

  # Batch mode
  python test_classifier.py --batch test_queries.txt

  # Verbose mode (show all category scores)
  python test_classifier.py --query "Hello" --verbose
        """
    )

    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Single query to classify'
    )

    parser.add_argument(
        '--batch', '-b',
        type=str,
        help='Path to file with queries (one per line)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show all category similarity scores'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config/agents.json',
        help='Path to agents.json config file (default: config/agents.json)'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        default=0.7,
        help='Confidence threshold for fallback (default: 0.7)'
    )

    args = parser.parse_args()

    # Initialize classifier
    print(f"{Colors.BOLD}Initializing AI Router Classifier...{Colors.END}")
    try:
        classifier = Classifier(
            config_path=args.config,
            confidence_threshold=args.threshold
        )
    except Exception as e:
        print(f"{Colors.RED}Error initializing classifier: {e}{Colors.END}")
        sys.exit(1)

    # Run appropriate mode
    if args.query:
        run_single_query(args.query, classifier, args.verbose)
    elif args.batch:
        run_batch_mode(args.batch, classifier, args.verbose)
    else:
        run_interactive_mode(classifier, args.verbose)


if __name__ == '__main__':
    main()
