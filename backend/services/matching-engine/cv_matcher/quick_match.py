"""
Quick Match - Convenience Function
===================================

Simple one-line function for quick CV evaluation.
"""

from typing import Union
from .cv_matcher import CVMatcher


def quick_match(job_description: str, cv_path_or_text: str, candidate_name: str = None) -> str:
    """
    Quick CV matching with formatted output.

    Args:
        job_description: Full job description text
        cv_path_or_text: Path to CV file (PDF/DOCX) or CV text
        candidate_name: Optional candidate name

    Returns:
        Formatted string with score and key highlights

    Example:
        >>> result = quick_match(job_text, "elena_cv.pdf", "Elena Rossi")
        >>> print(result)
        Elena Rossi (72.8/100): ✅ Suitable
        • Strong candidate with 4+ years experience
        • SaaS industry match
        • Keyword matching: 24.8/30 (strong)
    """
    matcher = CVMatcher(config={
        "use_nlp": False,  # Fast mode
        "enable_disqualification": True,
    })

    result = matcher.match_cv_to_job(job_description, cv_path_or_text, candidate_name)

    # Format output
    emoji = _get_emoji(result.classification)

    output = []
    output.append(f"{result.candidate_name} ({result.overall_score:.1f}/100): {emoji} {result.classification}")

    # Add key highlights
    breakdown = result.breakdown

    # Experience
    exp = breakdown['experience_matching']
    if exp.get('years_candidate', 0) > 0:
        years = exp['years_candidate']
        required = exp.get('years_required', 0)
        if years >= required:
            if years > required * 1.5:
                output.append(f"• Strong candidate with {years}+ years experience (exceeds requirement)")
            else:
                output.append(f"• {years} years experience (meets requirement)")
        else:
            output.append(f"⚠ Only {years} years experience ({required} required)")

    # Industry match
    if exp.get('industry_match') == 'exact':
        industry = breakdown['experience_matching'].get('industry', 'target')
        output.append(f"• Industry match confirmed")

    # Keywords
    kw_score = breakdown['keyword_matching']['score']
    if kw_score >= 20:
        output.append(f"• Keyword matching: {kw_score:.1f}/30 (strong)")
    elif kw_score >= 15:
        output.append(f"• Keyword matching: {kw_score:.1f}/30 (good)")
    else:
        output.append(f"⚠ Keyword matching: {kw_score:.1f}/30 (weak)")

    # Tool match
    tools = breakdown['tool_matching']
    if tools['overlap'] == 100:
        output.append(f"• Perfect tool match (all required tools present)")
    elif tools['overlap'] >= 75:
        output.append(f"• Strong tool match ({tools['overlap']:.0f}% overlap)")
    elif tools.get('missing'):
        missing = ", ".join(tools['missing'][:3])
        output.append(f"⚠ Missing tools: {missing}")

    # Customization
    custom_score = breakdown['customization_score']['score']
    if custom_score >= 20:
        output.append(f"• Strong CV customization detected (score: {custom_score:.1f}/25)")
    elif custom_score < 10:
        output.append(f"⚠ Generic CV - little evidence of tailoring")

    # Concerns
    if result.concerns:
        for concern in result.concerns[:2]:  # Top 2 concerns
            output.append(f"⚠ {concern}")

    # Recommendation
    output.append(f"\n→ {result.recommendation}")

    return "\n".join(output)


def quick_score(job_description: str, cv_path_or_text: str) -> float:
    """
    Get just the score (no formatting).

    Returns:
        Float score 0-100
    """
    matcher = CVMatcher(config={"use_nlp": False, "enable_disqualification": True})
    result = matcher.match_cv_to_job(job_description, cv_path_or_text)
    return result.overall_score


def quick_batch(job_description: str, cv_paths: list) -> str:
    """
    Quick batch matching with formatted ranking.

    Args:
        job_description: Full job description text
        cv_paths: List of CV file paths

    Returns:
        Formatted ranking table

    Example:
        >>> result = quick_batch(job_text, ["cv1.pdf", "cv2.pdf", "cv3.pdf"])
        >>> print(result)
        CANDIDATE RANKING (3 candidates):
        1. ✅ Elena Rossi (92.0) - Highly Suitable
        2. ✅ Rhea Patel (75.0) - Suitable
        3. ❌ Ben Carter (5.0) - Unsuitable
    """
    matcher = CVMatcher(config={"use_nlp": False, "enable_disqualification": True})
    results = matcher.match_multiple_cvs(job_description, cv_paths)

    output = [f"CANDIDATE RANKING ({len(results)} candidates):\n"]

    for rank, result in enumerate(results, 1):
        emoji = _get_emoji(result.classification)
        output.append(
            f"{rank}. {emoji} {result.candidate_name} ({result.overall_score:.1f}) - {result.classification}"
        )

    return "\n".join(output)


def quick_match_multi(
    job_description: str,
    cv_paths_or_texts: list,
    candidate_names: list = None
) -> str:
    """
    Match multiple CVs with detailed results, sorted by score (high to low).

    Args:
        job_description: Full job description text
        cv_paths_or_texts: List of CV file paths or CV text strings
        candidate_names: Optional list of candidate names (same length as CVs)

    Returns:
        Formatted string with detailed results for each candidate, sorted by score

    Example:
        >>> cvs = ["elena.pdf", "john.pdf", "mary.pdf"]
        >>> names = ["Elena Rossi", "John Smith", "Mary Jones"]
        >>> results = quick_match_multi(job_text, cvs, names)
        >>> print(results)

        DETAILED CANDIDATE RANKING (3 candidates):

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🥇 #1: Elena Rossi (92.0/100): 🌟 Highly Suitable
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        • Strong candidate with 4+ years experience (exceeds requirement)
        • Industry match confirmed
        • Keyword matching: 28.0/30 (strong)
        • Perfect tool match (all required tools present)
        • Strong CV customization detected (score: 24.0/25)

        → Fast-track to interview

        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        🥈 #2: John Smith (75.0/100): ✅ Suitable
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ...
    """
    matcher = CVMatcher(config={
        "use_nlp": False,
        "enable_disqualification": True,
    })

    # Process all CVs
    results = []
    for i, cv_path_or_text in enumerate(cv_paths_or_texts):
        candidate_name = None
        if candidate_names and i < len(candidate_names):
            candidate_name = candidate_names[i]

        try:
            result = matcher.match_cv_to_job(job_description, cv_path_or_text, candidate_name)
            results.append(result)
        except Exception as e:
            # Skip failed CVs but log them
            error_name = candidate_name or f"Candidate {i+1}"
            results.append(type('obj', (), {
                'candidate_name': error_name,
                'overall_score': 0.0,
                'classification': 'Error',
                'breakdown': {},
                'concerns': [f"Failed to process: {str(e)}"],
            })())

    # Sort by score (highest first)
    results.sort(key=lambda r: r.overall_score, reverse=True)

    # Format output
    output = []
    output.append(f"DETAILED CANDIDATE RANKING ({len(results)} candidates):\n")

    for rank, result in enumerate(results, 1):
        # Rank emoji
        if rank == 1:
            rank_emoji = "🥇"
        elif rank == 2:
            rank_emoji = "🥈"
        elif rank == 3:
            rank_emoji = "🥉"
        else:
            rank_emoji = f"{rank}."

        # Classification emoji
        class_emoji = _get_emoji(result.classification)

        # Separator
        output.append("━" * 80)
        output.append(
            f"{rank_emoji} #{rank}: {result.candidate_name} ({result.overall_score:.1f}/100): "
            f"{class_emoji} {result.classification}"
        )
        output.append("━" * 80)

        # Add details (only if not an error)
        if result.classification != 'Error':
            breakdown = result.breakdown

            # Experience
            exp = breakdown.get('experience_matching', {})
            if exp.get('years_candidate', 0) > 0:
                years = exp['years_candidate']
                required = exp.get('years_required', 0)
                if years >= required:
                    if years > required * 1.5:
                        output.append(f"• Strong candidate with {years}+ years experience (exceeds requirement)")
                    else:
                        output.append(f"• {years} years experience (meets requirement)")
                else:
                    output.append(f"⚠ Only {years} years experience ({required} required)")

            # Industry match
            if exp.get('industry_match') == 'exact':
                output.append("• Industry match confirmed")

            # Keywords
            kw_score = breakdown.get('keyword_matching', {}).get('score', 0)
            if kw_score >= 20:
                output.append(f"• Keyword matching: {kw_score:.1f}/30 (strong)")
            elif kw_score >= 15:
                output.append(f"• Keyword matching: {kw_score:.1f}/30 (good)")
            elif kw_score > 0:
                output.append(f"⚠ Keyword matching: {kw_score:.1f}/30 (weak)")

            # Tool match
            tools = breakdown.get('tool_matching', {})
            if tools.get('overlap') == 100:
                output.append("• Perfect tool match (all required tools present)")
            elif tools.get('overlap', 0) >= 75:
                output.append(f"• Strong tool match ({tools['overlap']:.0f}% overlap)")
            elif tools.get('missing'):
                missing = ", ".join(tools['missing'][:3])
                output.append(f"⚠ Missing tools: {missing}")

            # Customization
            custom_score = breakdown.get('customization_score', {}).get('score', 0)
            if custom_score >= 20:
                output.append(f"• Strong CV customization detected (score: {custom_score:.1f}/25)")
            elif custom_score < 10 and custom_score > 0:
                output.append("⚠ Generic CV - little evidence of tailoring")

            # Concerns
            if hasattr(result, 'concerns') and result.concerns:
                for concern in result.concerns[:2]:  # Top 2 concerns
                    output.append(f"⚠ {concern}")

            # Recommendation
            if hasattr(result, 'recommendation'):
                output.append(f"\n→ {result.recommendation}")
        else:
            # Error case
            if hasattr(result, 'concerns') and result.concerns:
                for concern in result.concerns:
                    output.append(f"❌ {concern}")

        output.append("")  # Blank line between candidates

    return "\n".join(output)


def _get_emoji(classification: str) -> str:
    """Get emoji based on classification"""
    emoji_map = {
        "Highly Suitable": "🌟",
        "Suitable": "✅",
        "Potentially Suitable": "⚠️",
        "Weak Match": "❌",
        "Unsuitable": "❌",
        "Error": "❌",
    }
    return emoji_map.get(classification, "➖")
