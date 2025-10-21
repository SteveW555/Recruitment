#!/usr/bin/env python3
"""
Email Classification Example - System + User Prompt Pattern
ProActive People - Recruitment Automation System

Demonstrates how to use separate system and user prompts with GROQ
for email classification tasks.
"""

import json
from groq_client import GroqClient, CompletionConfig, Temperature

# ============================================================================
# SYSTEM PROMPT
# ============================================================================
# The system prompt defines the AI's role, expertise, and output format

SYSTEM_PROMPT = """You are an expert email classification AI for a UK recruitment agency.

Your role: Analyze incoming emails and classify them into categories for automated routing.

Categories:
- CANDIDATE: Job applications, CV submissions, interview responses
- CLIENT: Job briefs, feedback, hiring requests
- SUPPLIER: Service provider emails (ATS systems, job boards)
- STAFF: Internal team communications
- OTHER: Spam, automated messages, unclassified

Output Format: Return ONLY valid JSON with this structure:
{
  "category": "CANDIDATE|CLIENT|SUPPLIER|STAFF|OTHER",
  "subcategory": "specific subcategory",
  "confidence": 0.0-1.0,
  "priority": "URGENT|HIGH|NORMAL|LOW",
  "sentiment": "positive|negative|neutral|mixed",
  "keywords": ["extracted", "keywords"],
  "requires_action": true|false,
  "reasoning": "brief explanation"
}

Be accurate and consistent. Use lower confidence scores when uncertain."""


# ============================================================================
# USER PROMPT BUILDER
# ============================================================================
# The user prompt contains the specific data to analyze

def build_user_prompt(from_email: str, subject: str, body: str) -> str:
    """Build user prompt with email details"""
    return f"""Classify this email:

FROM: {from_email}
SUBJECT: {subject}

BODY:
{body}

Analyze and return the classification JSON."""


# ============================================================================
# CLASSIFICATION FUNCTION
# ============================================================================

def classify_email_with_prompts(from_email: str, subject: str, body: str):
    """
    Classify email using system + user prompt pattern

    This demonstrates the recommended approach:
    1. System prompt = Role, rules, and output format (stays constant)
    2. User prompt = Specific data to analyze (changes per request)
    """

    # Initialize GROQ client
    client = GroqClient()

    # Build user prompt with email data
    user_prompt = build_user_prompt(from_email, subject, body)

    # Configure for classification (low temperature for consistency)
    config = CompletionConfig(
        model="llama-3.3-70b-versatile",
        temperature=Temperature.CONSERVATIVE.value,  # 0.3 for consistent results
        max_tokens=1500
    )

    # Call GROQ with BOTH system and user prompts
    response = client.complete(
        prompt=user_prompt,           # The specific email to classify
        system_prompt=SYSTEM_PROMPT,  # The AI's role and instructions
        config=config
    )

    # Parse JSON response (handle markdown-wrapped JSON)
    try:
        content = response.content

        # Extract JSON from markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        classification = json.loads(content)
        return classification
    except json.JSONDecodeError as e:
        # Fallback if JSON parsing fails
        return {
            "category": "OTHER",
            "subcategory": "unclassified",
            "confidence": 0.1,
            "error": f"Failed to parse response: {str(e)}",
            "raw_response": response.content
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("EMAIL CLASSIFICATION - System + User Prompt Pattern")
    print("=" * 80)
    print()

    # Example 1: Candidate CV submission
    print("EXAMPLE 1: Candidate CV Submission")
    print("-" * 80)

    result1 = classify_email_with_prompts(
        from_email="john.smith@gmail.com",
        subject="Application for Senior Sales Executive - Bristol",
        body="""Dear ProActive People,

I am writing to apply for the Senior Sales Executive position advertised on Indeed.
I have 5+ years of B2B sales experience and consistently exceed targets.

Please find my CV attached. I am immediately available.

Best regards,
John Smith
Mobile: 07700 900123"""
    )

    print("Classification Result:")
    print(json.dumps(result1, indent=2))
    print()

    # Example 2: Client job brief (urgent)
    print("\nEXAMPLE 2: Urgent Client Job Brief")
    print("-" * 80)

    result2 = classify_email_with_prompts(
        from_email="hiring@techcorp.co.uk",
        subject="URGENT: Need 3 Software Engineers - Start ASAP",
        body="""Hi ProActive Team,

We have an urgent requirement for 3 mid-level Software Engineers to start within 2 weeks.

Requirements:
- 3-5 years Python experience
- PostgreSQL and Redis
- AWS experience preferred

Can you send CVs by end of week?

Thanks,
Sarah Thompson
Head of Engineering"""
    )

    print("Classification Result:")
    print(json.dumps(result2, indent=2))
    print()

    # Example 3: Spam/marketing email
    print("\nEXAMPLE 3: Spam/Marketing Email")
    print("-" * 80)

    result3 = classify_email_with_prompts(
        from_email="sales@marketing-platform.com",
        subject="🚀 Boost Your Recruitment Business with AI!",
        body="""Hi there!

Are you tired of manual CV screening? Our revolutionary AI platform can:

* Parse 1000s of CVs in seconds
* Match candidates 10x faster
* Increase placements by 300%

SPECIAL OFFER: 50% off for the first 100 recruiters!

Click here to start your free trial!"""
    )

    print("Classification Result:")
    print(json.dumps(result3, indent=2))
    print()

    print("=" * 80)
    print("KEY INSIGHTS:")
    print("=" * 80)
    print("""
[OK] System Prompt: Defines the AI's role and classification rules (constant)
[OK] User Prompt: Contains the specific email data to analyze (variable)
[OK] Separation: Keeps instructions separate from data for clarity
[OK] Consistency: Low temperature (0.3) ensures reliable classification
[OK] Structure: JSON output makes integration with TypeScript easy

This pattern is ideal for production systems where you need:
- Consistent behavior across thousands of emails
- Clear separation between rules and data
- Easy testing and validation
- Reliable automated routing
    """)
