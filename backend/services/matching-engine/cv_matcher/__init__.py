"""
CV Matching Engine
==================

Automated CV evaluation system for ProActive People recruitment platform.

Main Components:
- CVMatcher: Core matching engine
- TextExtractor: PDF/DOCX text extraction
- ScoringEngine: Multi-component scoring algorithm
- EntityExtractor: NER for tools, skills, metrics

Quick Usage (Simple):
    from cv_matcher import quick_match

    result = quick_match(job_description, "cv.pdf", "Candidate Name")
    print(result)
    # Output:
    # Elena Rossi (72.8/100): ✅ Suitable
    # • Strong candidate with 4+ years experience
    # • Industry match confirmed
    # → Review for interview

Advanced Usage:
    from cv_matcher import CVMatcher

    matcher = CVMatcher()
    result = matcher.match_cv_to_job(job_description, cv_path)
    print(f"Score: {result.overall_score}, Classification: {result.classification}")
"""

from .cv_matcher import CVMatcher
from .scoring_engine import ScoringEngine
from .text_extractor import TextExtractor
from .entity_extractor import EntityExtractor
from .quick_match import quick_match, quick_score, quick_batch, quick_match_multi

__version__ = "1.0.0"
__all__ = [
    "CVMatcher",
    "ScoringEngine",
    "TextExtractor",
    "EntityExtractor",
    "quick_match",
    "quick_score",
    "quick_batch",
    "quick_match_multi",
]
