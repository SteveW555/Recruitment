#!/usr/bin/env python3
"""
Recruitment Source Finder Script

Parses sources.md and returns relevant sources based on query matching.
Uses keyword matching, category analysis, and relevance scoring.
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


# Domain-specific synonym mappings for better matching
SYNONYM_GROUPS = {
    'gdpr': ['gdpr', 'data protection', 'privacy', 'data privacy', 'compliance'],
    'ats': ['ats', 'applicant tracking', 'recruitment software', 'crm', 'recruitment crm', 'staffing software'],
    'cv': ['cv', 'resume', 'curriculum vitae', 'candidate profile'],
    'business_development': ['business development', 'bd', 'client acquisition', 'sales', 'new business'],
    'sourcing': ['sourcing', 'candidate sourcing', 'talent acquisition', 'candidate search'],
    'recruitment_models': ['retained', 'contingency', 'recruitment models', 'fee structure'],
    'legal': ['legal', 'compliance', 'regulations', 'conduct regulations', 'employment law'],
    'marketing': ['marketing', 'digital marketing', 'content marketing', 'seo'],
    'finance': ['finance', 'accounting', 'profit', 'margins', 'fees', 'funding'],
    'roles': ['recruiter', 'consultant', '360', 'resourcer', 'bd manager', 'managing director'],
}


def expand_query_with_synonyms(query: str) -> List[str]:
    """Expand query terms with domain synonyms for better matching."""
    query_lower = query.lower()
    expanded_terms = set(query_lower.split())

    # Add synonyms for each term
    for group_terms in SYNONYM_GROUPS.values():
        for term in group_terms:
            if term in query_lower:
                expanded_terms.update(group_terms)
                break

    return list(expanded_terms)


def parse_sources_md(file_path: Path) -> List[Dict]:
    """Parse sources.md and extract all sources with their categories."""
    if not file_path.exists():
        raise FileNotFoundError(f"sources.md not found at {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sources = []
    current_category = "Uncategorized"
    current_subcategory = None

    # Split into lines and process
    lines = content.split('\n')

    for line in lines:
        line = line.strip()

        # Main category (📌 **N. Category Name**)
        if line.startswith('📌 **'):
            match = re.search(r'📌 \*\*(?:\d+\.\s*)?(.+?)\*\*', line)
            if match:
                current_category = match.group(1).strip()
                current_subcategory = None

        # Subcategory (✅ **Subcategory Name**)
        elif line.startswith('✅ **'):
            match = re.search(r'✅ \*\*(.+?)\*\*', line)
            if match:
                current_subcategory = match.group(1).strip()

        # Source entry (Title – Description OR Title)
        elif line and not line.startswith('[') and not line.startswith('#'):
            # Check if next line might be a URL
            # Format: "Title – Description" on one line, "[URL](URL)" on next
            # Or: "Title" on one line, "[URL](URL)" on next

            # Look for pattern: text (not starting with bracket)
            if ' – ' in line or (line and not line.startswith('[')):
                title_parts = line.split(' – ', 1)
                title = title_parts[0].strip()
                description = title_parts[1].strip() if len(title_parts) > 1 else ""

                # This is a source title, URL should be on next line or inline
                # We'll handle URL extraction in next iteration or look for inline URLs
                # For now, store source with placeholder
                if title and not title.startswith('http'):
                    sources.append({
                        'title': title,
                        'description': description,
                        'category': current_category,
                        'subcategory': current_subcategory,
                        'url': None  # Will be filled when URL line is found
                    })

        # URL line ([https://example.com](https://example.com))
        elif line.startswith('['):
            url_match = re.search(r'\[([^\]]+)\]\(([^\)]+)\)', line)
            if url_match and sources:
                # Assign URL to the most recent source
                if sources[-1]['url'] is None:
                    sources[-1]['url'] = url_match.group(2)

    # Filter out sources without URLs (incomplete entries)
    sources = [s for s in sources if s['url']]

    return sources


def calculate_relevance_score(source: Dict, query_terms: List[str]) -> Tuple[int, List[str]]:
    """
    Calculate relevance score for a source based on query terms.
    Returns (score, match_reasons).
    """
    score = 0
    match_reasons = []

    # Prepare searchable text
    title = source['title'].lower()
    description = source['description'].lower()
    category = source['category'].lower()
    subcategory = (source['subcategory'] or '').lower()

    # Match in different fields with different weights
    for term in query_terms:
        term = term.lower()

        # Title matches (highest weight)
        if term in title:
            score += 30
            if f"matched '{term}' in title" not in match_reasons:
                match_reasons.append(f"matched '{term}' in title")

        # Category matches (high weight)
        if term in category:
            score += 25
            if f"matched '{term}' in category" not in match_reasons:
                match_reasons.append(f"matched '{term}' in category")

        # Subcategory matches (high weight)
        if term in subcategory:
            score += 20
            if f"matched '{term}' in subcategory" not in match_reasons:
                match_reasons.append(f"matched '{term}' in subcategory")

        # Description matches (medium weight)
        if term in description:
            score += 15
            if f"matched '{term}' in description" not in match_reasons:
                match_reasons.append(f"matched '{term}' in description")

    # Bonus for multiple term matches
    if len(match_reasons) > 2:
        score += 10

    return score, match_reasons


def find_relevant_sources(
    sources: List[Dict],
    query: str,
    limit: int = 20,
    min_score: int = 30
) -> List[Dict]:
    """Find and rank sources relevant to the query."""

    # Expand query with synonyms
    query_terms = expand_query_with_synonyms(query)

    # Score all sources
    scored_sources = []
    for source in sources:
        score, reasons = calculate_relevance_score(source, query_terms)

        if score >= min_score:
            scored_sources.append({
                **source,
                'score': score,
                'match_reasons': reasons
            })

    # Sort by score (descending)
    scored_sources.sort(key=lambda x: x['score'], reverse=True)

    # Return top N
    return scored_sources[:limit]


def format_output_json(sources: List[Dict]) -> str:
    """Format sources as JSON for easy parsing."""
    output = []
    for source in sources:
        output.append({
            'title': source['title'],
            'url': source['url'],
            'category': source['category'],
            'subcategory': source.get('subcategory'),
            'score': source['score'],
            'match_reasons': source['match_reasons']
        })
    return json.dumps(output, indent=2, ensure_ascii=False)


def format_output_readable(sources: List[Dict]) -> str:
    """Format sources in human-readable format grouped by category."""
    if not sources:
        return "No relevant sources found."

    # Group by category
    by_category = {}
    for source in sources:
        cat = source['category']
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(source)

    output_lines = [f"Found {len(sources)} relevant sources:\n"]

    for category, cat_sources in by_category.items():
        output_lines.append(f"\n## {category}")
        if cat_sources[0].get('subcategory'):
            # Group by subcategory within category
            by_subcat = {}
            for src in cat_sources:
                subcat = src.get('subcategory') or 'General'
                if subcat not in by_subcat:
                    by_subcat[subcat] = []
                by_subcat[subcat].append(src)

            for subcat, sub_sources in by_subcat.items():
                if subcat != 'General':
                    output_lines.append(f"\n### {subcat}")
                for src in sub_sources:
                    output_lines.append(f"- **{src['title']}** (score: {src['score']})")
                    output_lines.append(f"  {src['url']}")
        else:
            for src in cat_sources:
                output_lines.append(f"- **{src['title']}** (score: {src['score']})")
                output_lines.append(f"  {src['url']}")

    return '\n'.join(output_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Find relevant sources from sources.md based on query'
    )
    parser.add_argument('query', help='Search query or topic')
    parser.add_argument('--limit', type=int, default=20, help='Maximum sources to return')
    parser.add_argument('--min-score', type=int, default=30, help='Minimum relevance score (0-100)')
    parser.add_argument('--format', choices=['json', 'readable'], default='json',
                       help='Output format')
    parser.add_argument('--sources-file', type=str, default='d:/Recruitment/sources.md',
                       help='Path to sources.md file')

    args = parser.parse_args()

    try:
        # Parse sources.md
        sources_path = Path(args.sources_file)
        all_sources = parse_sources_md(sources_path)

        # Find relevant sources
        relevant = find_relevant_sources(
            all_sources,
            args.query,
            limit=args.limit,
            min_score=args.min_score
        )

        # Output results
        if args.format == 'json':
            print(format_output_json(relevant))
        else:
            print(format_output_readable(relevant))

        # Exit code indicates if results were found
        sys.exit(0 if relevant else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == '__main__':
    main()
