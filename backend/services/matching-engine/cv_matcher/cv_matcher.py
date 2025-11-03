"""
CVMatcher - Main CV Matching Engine
====================================

Orchestrates the entire CV evaluation pipeline.
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .text_extractor import TextExtractor
from .entity_extractor import EntityExtractor
from .scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Container for CV matching results"""

    candidate_name: str
    overall_score: float
    classification: str
    confidence: float
    recommendation: str
    breakdown: Dict[str, Any]
    strengths: List[str]
    concerns: List[str]
    next_steps: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "candidate_name": self.candidate_name,
            "overall_score": self.overall_score,
            "classification": self.classification,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "breakdown": self.breakdown,
            "strengths": self.strengths,
            "concerns": self.concerns,
            "next_steps": self.next_steps,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


class CVMatcher:
    """
    Main CV matching engine that coordinates text extraction,
    entity recognition, and scoring.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize CV matcher with optional configuration.

        Args:
            config: Optional configuration dictionary with keys:
                - use_nlp: Enable NLP-based semantic matching (default: True)
                - nlp_model: spaCy model to use (default: 'en_core_web_sm')
                - semantic_threshold: Similarity threshold for matches (default: 0.70)
                - enable_disqualification: Apply auto-reject filters (default: True)
        """
        self.config = config or {}
        self.text_extractor = TextExtractor()
        self.entity_extractor = EntityExtractor(
            use_nlp=self.config.get("use_nlp", True),
            nlp_model=self.config.get("nlp_model", "en_core_web_sm"),
        )
        self.scoring_engine = ScoringEngine(
            semantic_threshold=self.config.get("semantic_threshold", 0.70),
            enable_disqualification=self.config.get("enable_disqualification", True),
        )

        logger.info("CVMatcher initialized with config: %s", self.config)

    def match_cv_to_job(
        self,
        job_description: str,
        cv_path_or_text: str,
        candidate_name: Optional[str] = None,
    ) -> MatchResult:
        """
        Match a CV against a job description and return detailed results.

        Args:
            job_description: Full job description text
            cv_path_or_text: File path to CV (PDF/DOCX) or CV text content
            candidate_name: Optional candidate name (extracted if not provided)

        Returns:
            MatchResult object with comprehensive matching analysis
        """
        logger.info("Starting CV matching process")

        try:
            # Step 1: Extract text from CV
            cv_text = self._extract_cv_text(cv_path_or_text)
            logger.debug("CV text extracted (%d chars)", len(cv_text))

            # Step 2: Extract entities from job and CV
            job_entities = self.entity_extractor.extract_from_job(job_description)
            cv_entities = self.entity_extractor.extract_from_cv(cv_text)
            logger.debug("Entities extracted - Job: %s, CV: %s", job_entities.keys(), cv_entities.keys())

            # Step 3: Extract candidate name if not provided
            if not candidate_name:
                candidate_name = cv_entities.get("name", "Unknown Candidate")

            # Step 4: Check disqualification filters
            is_disqualified, disqualifiers = self.scoring_engine.check_disqualifiers(
                job_entities, cv_entities
            )

            if is_disqualified:
                logger.warning("Candidate disqualified: %s", disqualifiers)
                return self._create_disqualified_result(candidate_name, disqualifiers)

            # Step 5: Calculate component scores
            scoring_result = self.scoring_engine.calculate_score(
                job_description=job_description,
                cv_text=cv_text,
                job_entities=job_entities,
                cv_entities=cv_entities,
            )

            # Step 6: Build match result
            match_result = self._build_match_result(
                candidate_name=candidate_name,
                scoring_result=scoring_result,
                job_entities=job_entities,
                cv_entities=cv_entities,
            )

            logger.info(
                "Matching complete - Score: %.1f, Classification: %s",
                match_result.overall_score,
                match_result.classification,
            )

            return match_result

        except Exception as e:
            logger.error("Error during CV matching: %s", str(e), exc_info=True)
            raise CVMatchingError(f"Failed to match CV: {str(e)}") from e

    def match_multiple_cvs(
        self, job_description: str, cv_paths: List[str]
    ) -> List[MatchResult]:
        """
        Match multiple CVs against a single job description.

        Args:
            job_description: Full job description text
            cv_paths: List of file paths to CVs

        Returns:
            List of MatchResult objects, sorted by score (highest first)
        """
        logger.info("Matching %d CVs against job", len(cv_paths))

        results = []
        for cv_path in cv_paths:
            try:
                result = self.match_cv_to_job(job_description, cv_path)
                results.append(result)
            except Exception as e:
                logger.error("Failed to match CV %s: %s", cv_path, str(e))
                # Continue with other CVs

        # Sort by score descending
        results.sort(key=lambda r: r.overall_score, reverse=True)

        logger.info("Batch matching complete - %d results", len(results))
        return results

    def _extract_cv_text(self, cv_path_or_text: str) -> str:
        """Extract text from CV file or return text if already extracted"""
        if cv_path_or_text.endswith((".pdf", ".docx", ".doc")):
            return self.text_extractor.extract(cv_path_or_text)
        return cv_path_or_text

    def _create_disqualified_result(
        self, candidate_name: str, disqualifiers: List[str]
    ) -> MatchResult:
        """Create result object for disqualified candidate"""
        return MatchResult(
            candidate_name=candidate_name,
            overall_score=0,
            classification="Unsuitable",
            confidence=1.0,
            recommendation="Auto-reject",
            breakdown={
                "disqualification_reasons": disqualifiers,
                "keyword_matching": {"score": 0, "max": 30},
                "tool_matching": {"score": 0, "max": 25},
                "experience_matching": {"score": 0, "max": 20},
                "customization_score": {"score": 0, "max": 25},
            },
            strengths=[],
            concerns=[f"Disqualified: {reason}" for reason in disqualifiers],
            next_steps="Candidate automatically rejected based on disqualification criteria",
        )

    def _build_match_result(
        self,
        candidate_name: str,
        scoring_result: Dict[str, Any],
        job_entities: Dict[str, Any],
        cv_entities: Dict[str, Any],
    ) -> MatchResult:
        """Build comprehensive match result from scoring output"""

        overall_score = scoring_result["overall_score"]
        classification = self._classify_score(overall_score)
        recommendation = self._get_recommendation(classification, overall_score)
        confidence = scoring_result.get("confidence", 0.85)

        strengths = self._identify_strengths(scoring_result, job_entities, cv_entities)
        concerns = self._identify_concerns(scoring_result, job_entities, cv_entities)

        return MatchResult(
            candidate_name=candidate_name,
            overall_score=overall_score,
            classification=classification,
            confidence=confidence,
            recommendation=recommendation,
            breakdown=scoring_result["breakdown"],
            strengths=strengths,
            concerns=concerns,
            next_steps=self._get_next_steps(classification),
            metadata={
                "job_required_tools": job_entities.get("required_tools", []),
                "cv_tools": cv_entities.get("tools", []),
                "years_experience": cv_entities.get("years_experience"),
            },
        )

    def _classify_score(self, score: float) -> str:
        """Classify overall score into category"""
        if score >= 80:
            return "Highly Suitable"
        elif score >= 60:
            return "Suitable"
        elif score >= 40:
            return "Potentially Suitable"
        elif score >= 20:
            return "Weak Match"
        else:
            return "Unsuitable"

    def _get_recommendation(self, classification: str, score: float) -> str:
        """Get recommendation based on classification"""
        recommendations = {
            "Highly Suitable": "Fast-track to interview",
            "Suitable": "Review for interview",
            "Potentially Suitable": "Manual review needed",
            "Weak Match": "Likely reject",
            "Unsuitable": "Auto-reject",
        }
        return recommendations.get(classification, "Manual review")

    def _get_next_steps(self, classification: str) -> str:
        """Get next steps based on classification"""
        next_steps = {
            "Highly Suitable": "Schedule phone screen within 48 hours",
            "Suitable": "Add to interview shortlist for review",
            "Potentially Suitable": "Recruiter to manually review CV and make decision",
            "Weak Match": "Hold for 7 days, then reject if no better candidates",
            "Unsuitable": "Send automated rejection email",
        }
        return next_steps.get(classification, "Awaiting manual review")

    def _identify_strengths(
        self,
        scoring_result: Dict[str, Any],
        job_entities: Dict[str, Any],
        cv_entities: Dict[str, Any],
    ) -> List[str]:
        """Identify candidate strengths based on scoring"""
        strengths = []

        # Experience strengths
        exp_breakdown = scoring_result["breakdown"]["experience_matching"]
        if exp_breakdown.get("years_candidate", 0) > exp_breakdown.get("years_required", 0):
            years_over = exp_breakdown["years_candidate"] - exp_breakdown["years_required"]
            strengths.append(
                f"Exceeds experience requirements ({exp_breakdown['years_candidate']} years vs {exp_breakdown['years_required']} required)"
            )

        # Tool strengths
        tool_breakdown = scoring_result["breakdown"]["tool_matching"]
        if tool_breakdown.get("overlap", 0) == 100:
            strengths.append("Perfect tool/system match - all required tools present")
        elif tool_breakdown.get("overlap", 0) >= 80:
            strengths.append("Strong tool match - most required tools present")

        # Customization strengths
        custom_breakdown = scoring_result["breakdown"]["customization_score"]
        if custom_breakdown["score"] >= 20:
            strengths.append("Strong evidence of CV tailoring to job description")

        # Metric strengths
        if "quantified_metrics" in str(custom_breakdown.get("signals", [])):
            strengths.append("Provides quantified performance metrics")

        # Industry match
        if exp_breakdown.get("industry_match") == "exact":
            strengths.append(f"Exact industry match ({job_entities.get('industry', 'target sector')})")

        return strengths

    def _identify_concerns(
        self,
        scoring_result: Dict[str, Any],
        job_entities: Dict[str, Any],
        cv_entities: Dict[str, Any],
    ) -> List[str]:
        """Identify potential concerns based on scoring"""
        concerns = []

        # Tool gaps
        tool_breakdown = scoring_result["breakdown"]["tool_matching"]
        missing_tools = tool_breakdown.get("missing", [])
        if missing_tools:
            concerns.append(f"Missing required tools: {', '.join(missing_tools)}")

        # Experience concerns
        exp_breakdown = scoring_result["breakdown"]["experience_matching"]
        if exp_breakdown.get("years_candidate", 0) < exp_breakdown.get("years_required", 0):
            concerns.append("Below minimum experience requirement")

        # Customization concerns
        custom_breakdown = scoring_result["breakdown"]["customization_score"]
        red_flags = custom_breakdown.get("red_flags", [])
        if red_flags:
            concerns.extend([f"Red flag: {flag}" for flag in red_flags])

        # Low component scores
        if scoring_result["breakdown"]["keyword_matching"]["score"] < 15:
            concerns.append("Low keyword match - may not have read job description carefully")

        return concerns


class CVMatchingError(Exception):
    """Custom exception for CV matching errors"""

    pass
