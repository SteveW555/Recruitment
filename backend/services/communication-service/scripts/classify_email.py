#!/usr/bin/env python3
"""
Email Classification Service using GROQ AI
ProActive People - Recruitment Automation System

This script classifies incoming emails using GROQ's LLM API with structured
system and user prompts for accurate categorization and routing.
"""

import sys
import json
import argparse
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add parent directory to path to import groq_client
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from groq_client import GroqClient, CompletionConfig, Temperature

# ============================================================================
# EMAIL CLASSIFICATION CONFIGURATION
# ============================================================================

SYSTEM_PROMPT = """You are an expert email classification AI for ProActive People, a leading UK recruitment agency specializing in Sales, Technical, Contact Centre, Accountancy, and Commercial roles.

Your role is to analyze incoming emails and classify them accurately for automated routing to the appropriate department and handler.

## Classification Categories:

### CANDIDATE
Emails from job seekers, applicants, or potential candidates
Subcategories:
- application: Job applications
- cv_submission: CV/resume submissions
- interview_response: Responses to interview invitations
- availability_update: Availability or status updates
- reference_check: Reference information
- general_enquiry: General candidate questions

### CLIENT
Emails from companies seeking recruitment services
Subcategories:
- job_brief: New job vacancy briefs
- feedback: Candidate feedback after interviews
- interview_request: Interview scheduling requests
- placement_update: Updates on placed candidates
- contract_query: Contract or terms questions
- general_enquiry: General client questions

### SUPPLIER
Emails from service providers and partners
Subcategories:
- bullhorn_sync: Bullhorn ATS system notifications
- broadbean_notification: Broadbean job posting updates
- invoice: Invoices and billing
- service_update: Service updates or changes
- integration_issue: Technical integration problems

### STAFF
Internal emails from ProActive People team members
Subcategories:
- hr_matter: HR-related communications
- team_update: Team announcements or updates
- internal_query: Internal questions or requests

### OTHER
Emails that don't fit above categories
Subcategories:
- spam: Promotional or spam emails
- automated_notification: System notifications
- out_of_office: Auto-responder messages
- unclassified: Unable to determine category

## Priority Levels:
- URGENT: Requires immediate attention (complaints, time-sensitive opportunities)
- HIGH: Important but not urgent (new job briefs, interview feedback)
- NORMAL: Standard business communications
- LOW: Informational only, no action required

## Sentiment Analysis:
- positive: Positive or enthusiastic tone
- neutral: Professional, matter-of-fact tone
- negative: Complaints, frustrations, or concerns
- mixed: Contains both positive and negative elements

## Your Task:
Analyze each email and provide a structured JSON response with:
1. Primary category and subcategory
2. Confidence score (0.0 to 1.0)
3. Priority level
4. Sentiment analysis
5. Key extracted entities (names, companies, job titles, dates, etc.)
6. Important keywords
7. Whether action is required
8. Suggested actions if applicable

Be accurate, consistent, and thorough in your analysis. When uncertain, use lower confidence scores."""


def build_user_prompt(
    from_email: str,
    subject: str,
    body: str,
    to_emails: List[str],
    attachments: List[str]
) -> str:
    """
    Build the user prompt for email classification

    Args:
        from_email: Sender email address
        subject: Email subject line
        body: Email body text
        to_emails: List of recipient email addresses
        attachments: List of attachment filenames

    Returns:
        Formatted user prompt string
    """

    # Check for CV attachments
    cv_keywords = ['cv', 'resume', 'curriculum', 'vitae']
    has_cv = any(
        any(keyword in att.lower() for keyword in cv_keywords)
        for att in attachments
    )

    prompt = f"""Classify this email:

FROM: {from_email}
TO: {', '.join(to_emails)}
SUBJECT: {subject}

BODY:
{body[:2000]}  # Limit body to 2000 chars for token efficiency
{'...[truncated]' if len(body) > 2000 else ''}

ATTACHMENTS: {', '.join(attachments) if attachments else 'None'}
{'⚠️ CV/Resume detected in attachments' if has_cv else ''}

Analyze this email and return ONLY valid JSON with this exact structure:
{{
  "category": "CANDIDATE|CLIENT|SUPPLIER|STAFF|OTHER",
  "subcategory": "string (from predefined subcategories)",
  "confidence": 0.0-1.0,
  "priority": "URGENT|HIGH|NORMAL|LOW",
  "sentiment": "positive|negative|neutral|mixed",
  "keywords": ["array", "of", "important", "keywords"],
  "entities": {{
    "names": ["person names"],
    "companies": ["company names"],
    "job_titles": ["job titles mentioned"],
    "locations": ["locations mentioned"],
    "dates": ["date references"],
    "phone_numbers": ["phone numbers"],
    "skills": ["skills mentioned"]
  }},
  "requires_action": true|false,
  "suggested_actions": ["array of suggested next steps"],
  "reasoning": "brief explanation of classification decision",
  "red_flags": ["any concerning elements detected"]
}}

Focus on accuracy and provide detailed entity extraction."""

    return prompt


def parse_classification_response(response_text: str) -> Dict[str, Any]:
    """
    Parse and validate the classification response

    Args:
        response_text: Raw response from GROQ

    Returns:
        Validated classification dictionary
    """
    try:
        # Extract JSON from response (in case it's wrapped in markdown)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        classification = json.loads(response_text)

        # Validate required fields
        required_fields = [
            'category', 'subcategory', 'confidence', 'priority',
            'sentiment', 'keywords', 'entities', 'requires_action'
        ]

        for field in required_fields:
            if field not in classification:
                raise ValueError(f"Missing required field: {field}")

        # Validate category values
        valid_categories = ['CANDIDATE', 'CLIENT', 'SUPPLIER', 'STAFF', 'OTHER']
        if classification['category'] not in valid_categories:
            raise ValueError(f"Invalid category: {classification['category']}")

        valid_priorities = ['URGENT', 'HIGH', 'NORMAL', 'LOW']
        if classification['priority'] not in valid_priorities:
            raise ValueError(f"Invalid priority: {classification['priority']}")

        valid_sentiments = ['positive', 'negative', 'neutral', 'mixed']
        if classification['sentiment'] not in valid_sentiments:
            raise ValueError(f"Invalid sentiment: {classification['sentiment']}")

        # Validate confidence is between 0 and 1
        if not 0.0 <= classification['confidence'] <= 1.0:
            raise ValueError(f"Invalid confidence: {classification['confidence']}")

        return classification

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise ValueError(f"Classification validation failed: {str(e)}")


def classify_email(
    from_email: str,
    subject: str,
    body: str,
    to_emails: List[str],
    attachments: List[str],
    groq_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Classify an email using GROQ AI

    Args:
        from_email: Sender email address
        subject: Email subject line
        body: Email body text
        to_emails: List of recipient email addresses
        attachments: List of attachment filenames
        groq_api_key: Optional GROQ API key (defaults to env var)

    Returns:
        Classification results as dictionary
    """
    try:
        # Initialize GROQ client
        client = GroqClient(api_key=groq_api_key)

        # Build user prompt
        user_prompt = build_user_prompt(
            from_email=from_email,
            subject=subject,
            body=body,
            to_emails=to_emails,
            attachments=attachments
        )

        # Configure completion settings
        config = CompletionConfig(
            model="llama-3.3-70b-versatile",  # Best model for classification
            temperature=Temperature.CONSERVATIVE.value,  # Low temperature for consistency
            max_tokens=2000,  # Enough for detailed classification
            top_p=0.9
        )

        # Get classification from GROQ
        response = client.complete(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT,
            config=config
        )

        # Parse and validate response
        classification = parse_classification_response(response.content)

        # Add metadata
        classification['classified_at'] = datetime.utcnow().isoformat()
        classification['classified_by'] = 'ai'
        classification['model_used'] = response.model
        classification['tokens_used'] = response.usage

        return classification

    except Exception as e:
        # Return error classification
        return {
            'category': 'OTHER',
            'subcategory': 'unclassified',
            'confidence': 0.1,
            'priority': 'NORMAL',
            'sentiment': 'neutral',
            'keywords': [],
            'entities': {},
            'requires_action': False,
            'suggested_actions': [],
            'error': str(e),
            'classified_at': datetime.utcnow().isoformat(),
            'classified_by': 'rule-based-fallback'
        }


def main():
    """
    Main entry point for command-line usage
    """
    parser = argparse.ArgumentParser(
        description='Classify recruitment emails using GROQ AI'
    )
    parser.add_argument('--from', dest='from_email', required=True,
                       help='Sender email address')
    parser.add_argument('--subject', required=True,
                       help='Email subject line')
    parser.add_argument('--body', required=True,
                       help='Email body text')
    parser.add_argument('--to', required=True,
                       help='JSON array of recipient emails')
    parser.add_argument('--attachments', required=True,
                       help='JSON array of attachment filenames')
    parser.add_argument('--api-key', dest='api_key',
                       help='GROQ API key (optional, uses GROQ_API_KEY env var)')

    args = parser.parse_args()

    # Parse JSON arguments
    try:
        to_emails = json.loads(args.to)
        attachments = json.loads(args.attachments)
    except json.JSONDecodeError as e:
        print(json.dumps({
            'error': f'Invalid JSON in arguments: {str(e)}'
        }))
        sys.exit(1)

    # Classify email
    classification = classify_email(
        from_email=args.from_email,
        subject=args.subject,
        body=args.body,
        to_emails=to_emails,
        attachments=attachments,
        groq_api_key=args.api_key
    )

    # Output JSON result
    print(json.dumps(classification, indent=2))


if __name__ == '__main__':
    main()
