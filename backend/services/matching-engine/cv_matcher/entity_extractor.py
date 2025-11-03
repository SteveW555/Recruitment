"""
EntityExtractor - Named Entity Recognition for CVs and Job Descriptions
========================================================================

Extracts structured information:
- Tools & technologies
- Skills
- Years of experience
- Industries
- Roles
- Metrics (CSAT, ticket volumes, etc.)
- Responsibilities
"""

import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extract structured entities from unstructured text"""

    # Common tools/systems in recruitment
    COMMON_TOOLS = {
        "zendesk",
        "salesforce",
        "jira",
        "confluence",
        "intercom",
        "freshdesk",
        "helpscout",
        "servicenow",
        "ms dynamics",
        "dynamics 365",
        "hubspot",
        "slack",
        "teams",
        "zoom",
    }

    # Industry keywords
    INDUSTRIES = {
        "saas": ["saas", "software as a service"],
        "fintech": ["fintech", "financial technology"],
        "ecommerce": ["ecommerce", "e-commerce", "online retail"],
        "technology": ["technology", "tech", "it"],
        "healthcare": ["healthcare", "health", "medical"],
    }

    # Role types
    ROLE_TYPES = {
        "customer support": [
            "customer support",
            "technical support",
            "customer service",
            "help desk",
            "support specialist",
            "support engineer",
        ],
        "sales": ["sales", "account executive", "business development"],
        "engineering": ["engineer", "developer", "programmer"],
    }

    def __init__(self, use_nlp: bool = True, nlp_model: str = "en_core_web_sm"):
        """
        Initialize entity extractor.

        Args:
            use_nlp: Whether to use spaCy NLP (optional, improves accuracy)
            nlp_model: spaCy model to load
        """
        self.use_nlp = use_nlp
        self.nlp = None

        if use_nlp:
            try:
                import spacy

                self.nlp = spacy.load(nlp_model)
                logger.info("Loaded spaCy model: %s", nlp_model)
            except ImportError:
                logger.warning("spaCy not installed, using regex-based extraction")
                self.use_nlp = False
            except OSError:
                logger.warning("spaCy model not found, using regex-based extraction")
                self.use_nlp = False

    def extract_from_job(self, job_description: str) -> Dict[str, Any]:
        """
        Extract entities from job description.

        Returns:
            Dictionary with:
            - required_tools: List of mandatory tools
            - nice_to_have_tools: List of optional tools
            - years_experience_min: Minimum years required
            - industry: Industry/sector
            - role_type: Type of role
            - metrics: Performance metrics mentioned
            - responsibilities: Key responsibilities
            - company_type: Company type (e.g., SaaS, startup)
            - exclusions: Disqualifying statements
        """
        logger.info("Extracting entities from job description")

        entities = {
            "required_tools": self._extract_tools(job_description, required=True),
            "nice_to_have_tools": self._extract_tools(job_description, required=False),
            "years_experience_min": self._extract_years_experience(job_description),
            "industry": self._extract_industry(job_description),
            "role_type": self._extract_role_type(job_description),
            "metrics": self._extract_metrics(job_description),
            "responsibilities": self._extract_responsibilities(job_description),
            "company_type": self._extract_company_type(job_description),
            "exclusions": [],  # Can be configured per job
        }

        logger.debug("Extracted job entities: %s", entities.keys())
        return entities

    def extract_from_cv(self, cv_text: str) -> Dict[str, Any]:
        """
        Extract entities from CV text.

        Returns:
            Dictionary with:
            - name: Candidate name
            - tools: List of tools/technologies mentioned
            - years_experience: Years of experience
            - industries: Industries worked in
            - roles: Roles held
            - metrics: Performance metrics mentioned
            - experience_descriptions: Experience bullet points
            - summary: Professional summary/objective
            - full_text: Original CV text (for reference)
        """
        logger.info("Extracting entities from CV")

        entities = {
            "name": self._extract_name(cv_text),
            "tools": self._extract_tools(cv_text),
            "years_experience": self._extract_years_experience(cv_text, is_cv=True),
            "industries": self._extract_industries_cv(cv_text),
            "roles": self._extract_roles(cv_text),
            "metrics": self._extract_metrics(cv_text),
            "experience_descriptions": self._extract_experience_bullets(cv_text),
            "summary": self._extract_summary(cv_text),
            "full_text": cv_text,
        }

        logger.debug("Extracted CV entities: %s", entities.keys())
        return entities

    def _extract_tools(self, text: str, required: bool = None) -> List[str]:
        """Extract tools and technologies from text"""
        tools_found = set()
        text_lower = text.lower()

        # Check for common tools
        for tool in self.COMMON_TOOLS:
            if tool in text_lower:
                # Preserve original casing
                # Find the original tool name in text
                pattern = re.compile(re.escape(tool), re.IGNORECASE)
                match = pattern.search(text)
                if match:
                    tools_found.add(match.group())
                else:
                    tools_found.add(tool.title())

        # Extract tools from "Requirements" or "Skills" sections
        requirements_section = self._extract_section(text, ["requirements", "required", "must have"])
        if requirements_section and required is True:
            # Additional tools from requirements
            pass

        return sorted(list(tools_found))

    def _extract_years_experience(self, text: str, is_cv: bool = False) -> int:
        """Extract years of experience from text"""
        # Patterns for years of experience
        patterns = [
            r"(\d+)\+?\s*years?\s*(?:of)?\s*experience",
            r"minimum\s*(\d+)\s*years?",
            r"at least\s*(\d+)\s*years?",
            r"(\d+)\s*years?\s*in",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                years = int(match.group(1))
                if 0 <= years <= 50:  # Sanity check
                    return years

        # For CV, try to calculate from date ranges
        if is_cv:
            years = self._calculate_experience_from_dates(text)
            if years > 0:
                return years

        return 0

    def _calculate_experience_from_dates(self, text: str) -> int:
        """Calculate total experience from date ranges in CV"""
        # Pattern for date ranges: Jan 2020 - Present, 2018-2020, etc.
        date_patterns = [
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4}\s*[-–]\s*(?:Present|Current|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s*\d{4})",
            r"\d{4}\s*[-–]\s*(?:Present|Current|\d{4})",
        ]

        years_total = 0
        current_year = 2025  # Would use datetime.now().year in production

        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_range = match.group()

                # Extract start and end years
                year_matches = re.findall(r"\d{4}", date_range)
                if year_matches:
                    start_year = int(year_matches[0])
                    if "present" in date_range.lower() or "current" in date_range.lower():
                        end_year = current_year
                    elif len(year_matches) > 1:
                        end_year = int(year_matches[1])
                    else:
                        continue

                    years_total += max(end_year - start_year, 0)

        return years_total

    def _extract_industry(self, text: str) -> str:
        """Extract primary industry from job description"""
        text_lower = text.lower()

        for industry, keywords in self.INDUSTRIES.items():
            if any(keyword in text_lower for keyword in keywords):
                return industry

        return ""

    def _extract_industries_cv(self, text: str) -> List[str]:
        """Extract industries from CV"""
        text_lower = text.lower()
        industries = []

        for industry, keywords in self.INDUSTRIES.items():
            if any(keyword in text_lower for keyword in keywords):
                industries.append(industry)

        return industries

    def _extract_role_type(self, text: str) -> str:
        """Extract role type from job description"""
        text_lower = text.lower()

        for role_type, keywords in self.ROLE_TYPES.items():
            if any(keyword in text_lower for keyword in keywords):
                return role_type

        return ""

    def _extract_roles(self, text: str) -> List[str]:
        """Extract roles from CV"""
        text_lower = text.lower()
        roles = []

        for role_type, keywords in self.ROLE_TYPES.items():
            if any(keyword in text_lower for keyword in keywords):
                roles.append(role_type)

        return roles

    def _extract_metrics(self, text: str) -> List[str]:
        """Extract performance metrics (CSAT, ticket volumes, etc.)"""
        metrics = []

        # Pattern for metrics: "90% CSAT", "60 tickets per day", etc.
        patterns = [
            r"\d+%\s*(?:CSAT|satisfaction|uptime|accuracy|resolution)",
            r"\d+\s*(?:tickets?|calls?|queries?|requests?)\s*per\s*(?:day|week|hour)",
            r"(?:response|resolution)\s*time[:\s]*\d+\s*(?:min|hour|day)",
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                metrics.append(match.group().strip())

        return metrics

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities from job description"""
        # Find bullets in responsibilities section
        resp_section = self._extract_section(text, ["responsibilities", "duties", "you will"])

        if not resp_section:
            return []

        # Extract bullet points
        bullets = re.findall(r"[•\-\*]\s*(.+)", resp_section)
        return [bullet.strip() for bullet in bullets[:10]]  # Top 10

    def _extract_experience_bullets(self, text: str) -> List[str]:
        """Extract experience bullet points from CV"""
        # Find bullets in experience section
        exp_section = self._extract_section(text, ["experience", "work history", "employment"])

        if not exp_section:
            return []

        bullets = re.findall(r"[•\-\*]\s*(.+)", exp_section)
        return [bullet.strip() for bullet in bullets[:20]]  # Top 20

    def _extract_company_type(self, text: str) -> str:
        """Extract company type (SaaS, startup, etc.)"""
        text_lower = text.lower()

        company_types = ["saas", "startup", "enterprise", "scale-up", "fintech", "unicorn"]

        for company_type in company_types:
            if company_type in text_lower:
                return company_type

        return ""

    def _extract_name(self, text: str) -> str:
        """Extract candidate name from CV"""
        if self.use_nlp and self.nlp:
            # Use spaCy NER
            doc = self.nlp(text[:500])  # Check first 500 chars
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text

        # Fallback: assume name is in first line
        first_line = text.split("\n")[0].strip()
        if len(first_line) < 50 and len(first_line.split()) <= 4:
            return first_line

        return "Unknown Candidate"

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary from CV"""
        # Look for summary/objective section
        summary_section = self._extract_section(
            text, ["summary", "objective", "profile", "about"]
        )

        if summary_section:
            # Return first 500 chars
            return summary_section[:500].strip()

        # Fallback: return first paragraph after name
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if i > 0 and len(line) > 50:  # Skip name/contact
                return line.strip()[:500]

        return ""

    def _extract_section(self, text: str, section_names: List[str]) -> str:
        """Extract content from a specific section"""
        text_lower = text.lower()

        for section_name in section_names:
            # Find section header
            pattern = rf"(?:^|\n)(?:\s*{section_name}\s*)(?:\n|:)"
            match = re.search(pattern, text_lower)

            if match:
                start = match.end()
                # Find next section or end of text
                next_section = re.search(r"\n\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*\n", text[start:])

                if next_section:
                    end = start + next_section.start()
                else:
                    end = len(text)

                return text[start:end].strip()

        return ""
