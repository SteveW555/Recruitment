"""
ScoringEngine - Multi-component CV Scoring Algorithm
=====================================================

Implements the 100-point scoring system with 4 components:
1. Keyword Matching (30 points)
2. Tool & Technology Match (25 points)
3. Experience & Qualification Match (20 points)
4. Customization/Tailoring Detection (25 points)
"""

import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Implements the comprehensive CV scoring algorithm"""

    # Weight multipliers for different keyword types
    KEYWORD_WEIGHTS = {
        "required_tool": 2.0,
        "required_metric": 2.0,
        "industry_term": 1.5,
        "soft_skill": 1.0,
    }

    def __init__(
        self,
        semantic_threshold: float = 0.70,
        enable_disqualification: bool = True,
    ):
        """
        Initialize scoring engine.

        Args:
            semantic_threshold: Similarity threshold for semantic matches (0-1)
            enable_disqualification: Whether to apply auto-reject filters
        """
        self.semantic_threshold = semantic_threshold
        self.enable_disqualification = enable_disqualification

        logger.info(
            "ScoringEngine initialized - semantic_threshold=%.2f, disqualification=%s",
            semantic_threshold,
            enable_disqualification,
        )

    def calculate_score(
        self,
        job_description: str,
        cv_text: str,
        job_entities: Dict[str, Any],
        cv_entities: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive score across all components.

        Returns:
            Dictionary with overall_score, breakdown, and confidence
        """
        logger.info("Calculating CV score")

        # Component 1: Keyword Matching (30 points)
        keyword_score = self._score_keyword_matching(
            job_description, cv_text, job_entities, cv_entities
        )

        # Component 2: Tool & Technology Match (25 points)
        tool_score = self._score_tool_matching(job_entities, cv_entities)

        # Component 3: Experience & Qualification Match (20 points)
        experience_score = self._score_experience_matching(job_entities, cv_entities)

        # Component 4: Customization/Tailoring Detection (25 points)
        customization_score = self._score_customization(
            job_description, cv_text, job_entities, cv_entities
        )

        # Calculate overall score
        overall_score = (
            keyword_score["score"]
            + tool_score["score"]
            + experience_score["score"]
            + customization_score["score"]
        )

        # Calculate confidence
        confidence = self._calculate_confidence(
            cv_text, keyword_score, tool_score, experience_score, customization_score
        )

        result = {
            "overall_score": round(overall_score, 1),
            "confidence": round(confidence, 2),
            "breakdown": {
                "keyword_matching": keyword_score,
                "tool_matching": tool_score,
                "experience_matching": experience_score,
                "customization_score": customization_score,
            },
        }

        logger.info("Score calculated: %.1f (confidence: %.2f)", overall_score, confidence)
        return result

    def _score_keyword_matching(
        self,
        job_description: str,
        cv_text: str,
        job_entities: Dict[str, Any],
        cv_entities: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Score keyword matching (30 points max).

        Detects exact and semantic matches for:
        - Required tools (2x weight)
        - Required metrics (2x weight)
        - Industry terminology (1.5x weight)
        - Soft skills (1x weight)
        """
        matches = []
        total_score = 0.0

        # Extract keywords from job description
        job_keywords = self._extract_keywords(job_description, job_entities)

        # Normalize texts for matching
        job_lower = job_description.lower()
        cv_lower = cv_text.lower()

        for keyword, keyword_type in job_keywords:
            weight = self.KEYWORD_WEIGHTS.get(keyword_type, 1.0)
            points = 0

            # Check for exact match
            if keyword.lower() in cv_lower:
                points = 3.0 * weight
                match_type = "exact"
            # Check for semantic/partial match
            elif self._check_semantic_match(keyword, cv_text):
                points = 1.5 * weight
                match_type = "semantic"
            else:
                points = 0
                match_type = "no_match"

            if points > 0:
                matches.append(
                    {
                        "term": keyword,
                        "type": match_type,
                        "weight": weight,
                        "points": round(points, 1),
                    }
                )
                total_score += points

        # Cap at 30 points
        capped_score = min(total_score, 30)

        return {
            "score": round(capped_score, 1),
            "max": 30,
            "matches": matches,
            "total_keywords": len(job_keywords),
            "matched_keywords": len([m for m in matches if m["type"] != "no_match"]),
        }

    def _score_tool_matching(
        self, job_entities: Dict[str, Any], cv_entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score tool & technology matching (25 points max).

        Calculates overlap between required and candidate tools.
        """
        required_tools = set(job_entities.get("required_tools", []))
        nice_to_have_tools = set(job_entities.get("nice_to_have_tools", []))
        candidate_tools = set(cv_entities.get("tools", []))

        # Calculate matches
        required_matches = required_tools & candidate_tools
        nice_matches = nice_to_have_tools & candidate_tools
        missing_required = required_tools - candidate_tools

        # Calculate score
        score = 0.0
        score += len(required_matches) * 5.0  # 5 points per required tool
        score += len(nice_matches) * 2.0  # 2 points per nice-to-have
        score -= len(missing_required) * 3.0  # -3 penalty for missing required

        # Calculate overlap percentage
        if required_tools:
            overlap_pct = (len(required_matches) / len(required_tools)) * 100
        else:
            overlap_pct = 100 if not missing_required else 0

        # Cap at 25 points
        capped_score = min(max(score, 0), 25)

        return {
            "score": round(capped_score, 1),
            "max": 25,
            "required_tools": list(required_tools),
            "candidate_tools": list(candidate_tools),
            "matched_required": list(required_matches),
            "matched_nice_to_have": list(nice_matches),
            "missing": list(missing_required),
            "overlap": round(overlap_pct, 1),
        }

    def _score_experience_matching(
        self, job_entities: Dict[str, Any], cv_entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Score experience & qualification matching (20 points max).

        Components:
        - Years of experience (5 + 3 bonus)
        - Industry match (5 points)
        - Role relevance (5 points)
        - Qualification alignment (5-7 points)
        """
        score = 0.0

        # Years of experience
        years_required = job_entities.get("years_experience_min", 0)
        years_candidate = cv_entities.get("years_experience", 0)

        if years_candidate >= years_required:
            score += 5.0
            # Bonus for exceeding by 50%+
            if years_candidate >= years_required * 1.5:
                score += 3.0
        else:
            # Proportional reduction
            if years_required > 0:
                score += (years_candidate / years_required) * 5.0

        # Industry match
        job_industry = job_entities.get("industry", "").lower()
        cv_industries = [i.lower() for i in cv_entities.get("industries", [])]

        if job_industry in cv_industries:
            score += 5.0  # Exact match
        elif any(self._check_related_industry(job_industry, cv_ind) for cv_ind in cv_industries):
            score += 2.0  # Related industry
        else:
            score += 0.0

        # Role relevance
        job_role = job_entities.get("role_type", "").lower()
        cv_roles = [r.lower() for r in cv_entities.get("roles", [])]

        if job_role in cv_roles:
            score += 5.0  # Same role
        elif any(self._check_related_role(job_role, cv_role) for cv_role in cv_roles):
            score += 2.0  # Transferable role
        else:
            score += 0.0  # Unrelated

        # Qualification alignment (simplified for now)
        # This would be expanded with actual qualification parsing
        score += 5.0  # Assume meets requirements for now

        return {
            "score": round(score, 1),
            "max": 20,
            "years_required": years_required,
            "years_candidate": years_candidate,
            "industry_match": "exact" if job_industry in cv_industries else "related" if cv_industries else "none",
            "role_match": "same" if job_role in cv_roles else "transferable" if cv_roles else "unrelated",
        }

    def _score_customization(
        self,
        job_description: str,
        cv_text: str,
        job_entities: Dict[str, Any],
        cv_entities: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Score CV customization/tailoring (25 points max).

        This is the MOST IMPORTANT component - detects if candidate
        actually read and tailored their CV to the job.

        Components:
        A. Exact phrase matching (15 points max)
        B. Quantified metric alignment (5 points)
        C. Responsibility mirroring (6 points max)
        D. Tool prominence (3 points)
        E. Industry context awareness (2 points)
        """
        score = 0.0
        signals = []
        red_flags = []

        # A. Exact phrase matching
        job_phrases = self._extract_key_phrases(job_description)
        cv_lower = cv_text.lower()
        phrase_matches = 0

        for phrase in job_phrases[:10]:  # Check top 10 phrases
            if phrase.lower() in cv_lower:
                phrase_matches += 1
                if phrase_matches <= 5:  # Max 5 counted
                    score += 3.0

        if phrase_matches > 0:
            signals.append(f"exact_phrase_matching: {phrase_matches} phrases")

        # B. Quantified metric alignment
        job_metrics = job_entities.get("metrics", [])
        cv_metrics = cv_entities.get("metrics", [])

        if job_metrics and cv_metrics:
            # Check if CV provides matching/exceeding metrics
            for job_metric in job_metrics:
                if any(self._metrics_align(job_metric, cv_metric) for cv_metric in cv_metrics):
                    score += 5.0
                    signals.append(f"quantified_metrics: {job_metric}")
                    break  # Only count once

        # C. Responsibility mirroring
        job_responsibilities = job_entities.get("responsibilities", [])
        cv_experience = cv_entities.get("experience_descriptions", [])

        responsibility_mirrors = 0
        for resp in job_responsibilities[:5]:  # Check top 5
            if any(self._check_semantic_match(resp, exp) for exp in cv_experience):
                responsibility_mirrors += 1

        score += min(responsibility_mirrors * 2.0, 6.0)
        if responsibility_mirrors > 0:
            signals.append(f"responsibility_mirroring: {responsibility_mirrors} matches")

        # D. Tool prominence
        required_tools = job_entities.get("required_tools", [])
        cv_summary = cv_entities.get("summary", "")

        tools_in_summary = sum(1 for tool in required_tools if tool.lower() in cv_summary.lower())
        if tools_in_summary > 0:
            score += 3.0
            signals.append(f"tool_prominence: {tools_in_summary} tools in summary")
        elif required_tools and any(tool.lower() in cv_lower for tool in required_tools):
            score += 1.0

        # E. Industry context awareness
        job_company_type = job_entities.get("company_type", "")
        if job_company_type and job_company_type.lower() in cv_lower:
            score += 2.0
            signals.append("industry_context_awareness")

        # Red flags (deductions)
        if self._has_generic_objective(cv_entities.get("summary", "")):
            score -= 3.0
            red_flags.append("generic_objective_statement")

        if phrase_matches == 0 and len(job_phrases) > 5:
            score -= 5.0
            red_flags.append("no_job_specific_keywords")

        # Cap at 25 points, minimum 0
        capped_score = min(max(score, 0), 25)

        return {
            "score": round(capped_score, 1),
            "max": 25,
            "signals": signals,
            "red_flags": red_flags,
            "tailoring_detected": capped_score >= 15,
        }

    def check_disqualifiers(
        self, job_entities: Dict[str, Any], cv_entities: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Check for automatic disqualification criteria.

        Returns:
            (is_disqualified, list_of_reasons)
        """
        if not self.enable_disqualification:
            return False, []

        disqualifiers = []

        # 1. Insufficient experience (>1 year short)
        years_required = job_entities.get("years_experience_min", 0)
        years_candidate = cv_entities.get("years_experience", 0)
        if years_required > 0 and (years_required - years_candidate) > 1:
            disqualifiers.append(
                f"insufficient_experience: {years_candidate} years vs {years_required} required"
            )

        # 2. Wrong career field
        job_role = job_entities.get("role_type", "").lower()
        cv_roles = [r.lower() for r in cv_entities.get("roles", [])]
        if job_role and cv_roles:
            if not any(self._check_related_role(job_role, cv_role) for cv_role in cv_roles):
                disqualifiers.append("wrong_career_field")

        # 3. Zero required tools
        required_tools = set(job_entities.get("required_tools", []))
        candidate_tools = set(cv_entities.get("tools", []))
        if required_tools and not (required_tools & candidate_tools):
            disqualifiers.append("no_required_tools")

        # 4. Explicit exclusions
        exclusions = job_entities.get("exclusions", [])
        cv_text_lower = cv_entities.get("full_text", "").lower()
        for exclusion in exclusions:
            if exclusion.lower() in cv_text_lower:
                disqualifiers.append(f"explicit_exclusion: {exclusion}")

        is_disqualified = len(disqualifiers) > 0
        return is_disqualified, disqualifiers

    def _calculate_confidence(
        self,
        cv_text: str,
        keyword_score: Dict,
        tool_score: Dict,
        experience_score: Dict,
        customization_score: Dict,
    ) -> float:
        """
        Calculate confidence in the match score (0-1).

        Higher confidence when:
        - CV is well-structured and detailed
        - Multiple scoring signals present
        - High customization score
        """
        confidence = 0.0

        # CV length/detail (0.2 max)
        word_count = len(cv_text.split())
        if word_count > 300:
            confidence += 0.2
        else:
            confidence += (word_count / 300) * 0.2

        # Keyword matches (0.3 max)
        if keyword_score.get("matched_keywords", 0) > 5:
            confidence += 0.3
        else:
            confidence += (keyword_score.get("matched_keywords", 0) / 5) * 0.3

        # Tool matches (0.2 max)
        tool_overlap = tool_score.get("overlap", 0)
        confidence += (tool_overlap / 100) * 0.2

        # Customization detection (0.3 max)
        if customization_score.get("tailoring_detected", False):
            confidence += 0.3
        else:
            confidence += (customization_score["score"] / 25) * 0.3

        return min(confidence, 1.0)

    # Helper methods

    def _extract_keywords(
        self, job_description: str, job_entities: Dict[str, Any]
    ) -> List[Tuple[str, str]]:
        """Extract keywords from job description with their types"""
        keywords = []

        # Required tools
        for tool in job_entities.get("required_tools", []):
            keywords.append((tool, "required_tool"))

        # Metrics
        for metric in job_entities.get("metrics", []):
            keywords.append((metric, "required_metric"))

        # Industry terms
        industry_terms = [
            "SaaS",
            "B2B",
            "B2C",
            "customer-facing",
            "technical support",
            "help desk",
        ]
        for term in industry_terms:
            if term.lower() in job_description.lower():
                keywords.append((term, "industry_term"))

        # Soft skills
        soft_skills = [
            "communication",
            "empathy",
            "de-escalation",
            "patient",
            "problem-solving",
        ]
        for skill in soft_skills:
            if skill.lower() in job_description.lower():
                keywords.append((skill, "soft_skill"))

        return keywords

    def _extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text (2-4 word ngrams that appear in job)"""
        # Simplified implementation - would use NLP in production
        phrases = []

        # Common recruitment phrases
        common_phrases = [
            "knowledge base articles",
            "high volume support",
            "customer satisfaction",
            "ticketing system",
            "live chat",
            "technical troubleshooting",
            "product knowledge",
            "first-call resolution",
            "service level",
        ]

        text_lower = text.lower()
        for phrase in common_phrases:
            if phrase in text_lower:
                phrases.append(phrase)

        return phrases[:max_phrases]

    def _check_semantic_match(self, term1: str, term2: str) -> bool:
        """Check if two terms are semantically similar"""
        # Simplified - would use sentence-transformers in production
        # For now, check for substring matches
        term1_lower = term1.lower()
        term2_lower = term2.lower()

        if term1_lower in term2_lower or term2_lower in term1_lower:
            return True

        # Check for common synonyms
        synonyms = {
            "troubleshoot": ["diagnose", "debug", "resolve", "fix"],
            "customer": ["client", "user"],
            "support": ["help", "assistance", "service"],
        }

        for key, values in synonyms.items():
            if key in term1_lower and any(v in term2_lower for v in values):
                return True

        return False

    def _metrics_align(self, job_metric: str, cv_metric: str) -> bool:
        """Check if CV metric aligns with job requirement"""
        # Extract numbers from metrics
        job_numbers = re.findall(r"\d+", job_metric)
        cv_numbers = re.findall(r"\d+", cv_metric)

        if not job_numbers or not cv_numbers:
            return False

        # Check if metric types are similar (CSAT, tickets, etc.)
        job_type = re.sub(r"\d+", "", job_metric).lower()
        cv_type = re.sub(r"\d+", "", cv_metric).lower()

        if job_type in cv_type or cv_type in job_type:
            # Check if CV number meets or exceeds job number
            return int(cv_numbers[0]) >= int(job_numbers[0])

        return False

    def _check_related_industry(self, industry1: str, industry2: str) -> bool:
        """Check if industries are related"""
        # Simplified - would use taxonomy in production
        related_groups = [
            {"saas", "software", "technology", "it"},
            {"finance", "fintech", "banking"},
            {"retail", "e-commerce"},
        ]

        ind1_lower = industry1.lower()
        ind2_lower = industry2.lower()

        for group in related_groups:
            if any(term in ind1_lower for term in group) and any(
                term in ind2_lower for term in group
            ):
                return True

        return False

    def _check_related_role(self, role1: str, role2: str) -> bool:
        """Check if roles are related"""
        # Simplified - would use role taxonomy in production
        related_roles = [
            {
                "customer support",
                "technical support",
                "customer service",
                "help desk",
                "support specialist",
            },
            {"developer", "engineer", "programmer"},
            {"analyst", "data analyst", "business analyst"},
        ]

        role1_lower = role1.lower()
        role2_lower = role2.lower()

        for group in related_roles:
            if any(term in role1_lower for term in group) and any(
                term in role2_lower for term in group
            ):
                return True

        return False

    def _has_generic_objective(self, summary: str) -> bool:
        """Check if summary contains generic objective language"""
        generic_phrases = [
            "seeking opportunities",
            "looking for a role",
            "dynamic environment",
            "challenging position",
            "career growth",
        ]

        summary_lower = summary.lower()
        return any(phrase in summary_lower for phrase in generic_phrases)
