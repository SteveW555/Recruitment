"""
CV Matching Engine
==================

Automated CV evaluation system for ProActive People recruitment platform.

Main Components:
- CVMatcher: Core matching engine
- TextExtractor: PDF/DOCX text extraction
- ScoringEngine: Multi-component scoring algorithm
- EntityExtractor: NER for tools, skills, metrics

Usage:
    from cv_matcher import CVMatcher

    matcher = CVMatcher()
    result = matcher.match_cv_to_job(job_description, cv_path)
    print(f"Score: {result.overall_score}, Classification: {result.classification}")
"""

from .cv_matcher import CVMatcher
from .scoring_engine import ScoringEngine
from .text_extractor import TextExtractor
from .entity_extractor import EntityExtractor

__version__ = "1.0.0"
__all__ = ["CVMatcher", "ScoringEngine", "TextExtractor", "EntityExtractor"]
