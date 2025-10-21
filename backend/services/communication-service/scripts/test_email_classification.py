#!/usr/bin/env python3
"""
Test Email Classification Script
ProActive People - Recruitment Automation System

Tests the email classification service with various sample emails
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from classify_email import classify_email

# ============================================================================
# TEST EMAIL SAMPLES
# ============================================================================

TEST_EMAILS = [
    {
        "name": "Candidate CV Submission",
        "from_email": "john.candidate@gmail.com",
        "subject": "Application for Senior Sales Executive - Bristol",
        "body": """Dear ProActive People,

I am writing to apply for the Senior Sales Executive position advertised on Indeed.
I have over 5 years of B2B sales experience in the tech sector, consistently exceeding
targets by 30%+.

Please find my CV attached. I am immediately available and would welcome the opportunity
to discuss how my skills align with your client's requirements.

Key achievements:
- Grew territory revenue from £800k to £2.1M in 3 years
- Built and managed a team of 8 account executives
- Proficient in Salesforce, HubSpot, and LinkedIn Sales Navigator

Looking forward to hearing from you.

Best regards,
John Candidate
Mobile: 07700 900123""",
        "to_emails": ["recruitment@proactivepeople.com"],
        "attachments": ["John_Candidate_CV.pdf"]
    },
    {
        "name": "Client Job Brief",
        "from_email": "hiring.manager@techcorp.co.uk",
        "subject": "URGENT: Need 3 Software Engineers - Start ASAP",
        "body": """Hi ProActive Team,

We have an urgent requirement for 3 mid-level Software Engineers to start within 2 weeks.

Requirements:
- 3-5 years Python/FastAPI experience
- PostgreSQL and Redis
- Docker/Kubernetes knowledge
- AWS experience preferred

Location: Bristol (hybrid - 2 days office)
Salary: £50k-£65k DOE
Contract: Permanent

Can you send CVs by end of week? Our CTO is available for interviews next Monday.

Thanks,
Sarah Thompson
Head of Engineering
TechCorp Ltd""",
        "to_emails": ["bristol@proactivepeople.com"],
        "attachments": []
    },
    {
        "name": "Candidate Interview Feedback",
        "from_email": "alice.recruiter@client.com",
        "subject": "Re: Interview Feedback - Michael Brown - Accountant Role",
        "body": """Hi,

Thanks for sending Michael for the Senior Accountant position.

Unfortunately, we won't be moving forward. While his technical skills were strong,
we had concerns about:
- Limited experience with our specific industry regulations
- Cultural fit seemed off - very formal compared to our casual environment
- Salary expectations £10k above our budget

We'd like to see candidates with 5+ years in fintech specifically.

Can you send 2-3 more CVs this week?

Best,
Alice""",
        "to_emails": ["accountancy@proactivepeople.com"],
        "attachments": []
    },
    {
        "name": "Broadbean Notification",
        "from_email": "notifications@broadbean.com",
        "subject": "Job Posted Successfully: Customer Service Advisor - Bristol",
        "body": """Your job has been posted to the following job boards:

✓ Indeed UK
✓ Totaljobs
✓ CV-Library
✓ Reed
✓ Monster UK

Job Reference: PP-CS-2024-089
Posted: 21/10/2025 10:23 GMT
Expires: 20/11/2025

Campaign Performance (24 hours):
- Views: 127
- Applications: 0
- Clicks: 34

View detailed analytics: https://broadbean.com/campaigns/PP-CS-2024-089

This is an automated message from Broadbean.""",
        "to_emails": ["integrations@proactivepeople.com"],
        "attachments": []
    },
    {
        "name": "Candidate Availability Update",
        "from_email": "emma.jobseeker@outlook.com",
        "subject": "Update on my availability",
        "body": """Hi team,

Just wanted to let you know that I've handed in my notice at my current employer
and will be available from 1st December.

I'm still very interested in the Marketing Manager roles we discussed. Have there
been any developments on those opportunities?

Also happy to consider contract work if anything comes up in the meantime.

Thanks,
Emma Davis""",
        "to_emails": ["marketing@proactivepeople.com"],
        "attachments": []
    },
    {
        "name": "Complaint Email (Urgent)",
        "from_email": "angry.candidate@mail.com",
        "subject": "Complaint about consultant behavior",
        "body": """To whom it may concern,

I am extremely disappointed with the service I received from your consultant Mark Johnson.

He called me at 8:30 AM on Saturday morning about a role, which is completely unprofessional.
When I explained I was unavailable, he became rude and suggested I wasn't serious about
finding work.

This is unacceptable behavior. I've been in recruitment for 15 years and would never
treat a candidate this way.

I expect a formal response and apology within 48 hours, or I will be posting reviews
on Glassdoor and Trustpilot.

Regards,
David Mitchell""",
        "to_emails": ["complaints@proactivepeople.com", "info@proactivepeople.com"],
        "attachments": []
    },
    {
        "name": "Spam/Marketing",
        "from_email": "sales@marketing-platform.com",
        "subject": "🚀 Boost Your Recruitment Business with AI-Powered Tools!",
        "body": """Hi there!

Are you tired of manual CV screening? Our revolutionary AI platform can:

✨ Parse 1000s of CVs in seconds
✨ Match candidates 10x faster
✨ Integrate with any ATS
✨ Increase placements by 300%

SPECIAL OFFER: 50% off for the first 100 recruiters!

Click here to start your free trial: [link removed]

Don't miss out!

The MarketingPlatform Team

P.S. This offer expires in 48 hours!

Unsubscribe | Privacy Policy""",
        "to_emails": ["info@proactivepeople.com"],
        "attachments": []
    },
    {
        "name": "Reference Check Request",
        "from_email": "hr@previousemployer.co.uk",
        "subject": "Reference Request: Sophie Williams",
        "body": """Dear ProActive People,

We have received a reference request for Sophie Williams who has listed your agency
as a previous employer/contact.

Could you please confirm:
- Dates of engagement with your agency
- Roles she was placed in
- Performance and reliability
- Reason for leaving placements
- Would you rehire/work with her again?

This is for a permanent position at our company.

Please respond within 5 working days.

Thanks,
Jane Robertson
HR Manager
Previous Employer Ltd""",
        "to_emails": ["references@proactivepeople.com"],
        "attachments": []
    }
]


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_classification_tests():
    """
    Run classification tests on all sample emails
    """
    print("=" * 80)
    print("EMAIL CLASSIFICATION TEST SUITE")
    print("ProActive People - GROQ AI Integration")
    print("=" * 80)
    print()

    results = []

    for i, email in enumerate(TEST_EMAILS, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}/{len(TEST_EMAILS)}: {email['name']}")
        print(f"{'=' * 80}")
        print(f"From: {email['from_email']}")
        print(f"Subject: {email['subject']}")
        print(f"Attachments: {', '.join(email['attachments']) if email['attachments'] else 'None'}")
        print()

        try:
            # Classify the email
            classification = classify_email(
                from_email=email['from_email'],
                subject=email['subject'],
                body=email['body'],
                to_emails=email['to_emails'],
                attachments=email['attachments']
            )

            # Display results
            print(f"✓ CLASSIFICATION SUCCESSFUL")
            print(f"  Category: {classification['category']} > {classification['subcategory']}")
            print(f"  Confidence: {classification['confidence']:.2%}")
            print(f"  Priority: {classification['priority']}")
            print(f"  Sentiment: {classification['sentiment']}")
            print(f"  Requires Action: {'Yes' if classification['requires_action'] else 'No'}")

            if classification.get('keywords'):
                print(f"  Keywords: {', '.join(classification['keywords'][:5])}")

            if classification.get('entities'):
                entities = classification['entities']
                if entities.get('names'):
                    print(f"  People: {', '.join(entities['names'])}")
                if entities.get('companies'):
                    print(f"  Companies: {', '.join(entities['companies'])}")
                if entities.get('job_titles'):
                    print(f"  Job Titles: {', '.join(entities['job_titles'])}")

            if classification.get('suggested_actions'):
                print(f"  Suggested Actions:")
                for action in classification['suggested_actions'][:3]:
                    print(f"    - {action}")

            if classification.get('reasoning'):
                print(f"  Reasoning: {classification['reasoning'][:100]}...")

            # Track success
            results.append({
                'name': email['name'],
                'success': True,
                'category': classification['category'],
                'confidence': classification['confidence']
            })

        except Exception as e:
            print(f"✗ CLASSIFICATION FAILED")
            print(f"  Error: {str(e)}")
            results.append({
                'name': email['name'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print(f"\n\n{'=' * 80}")
    print("TEST SUMMARY")
    print(f"{'=' * 80}")

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"Total Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {successful/total:.1%}")
    print()

    # Category breakdown
    if successful > 0:
        print("Classification Breakdown:")
        categories = {}
        for r in results:
            if r['success']:
                cat = r['category']
                categories[cat] = categories.get(cat, 0) + 1

        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")

    print()
    print(f"{'=' * 80}")
    print("All tests completed!")
    print(f"{'=' * 80}")


if __name__ == '__main__':
    run_classification_tests()
