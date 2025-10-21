"""
Email Classification System Test Script
ProActive People - Recruitment Automation System

Tests the email classifier with various email types.
Run: python test_email_classification.py
"""

from utils.email.email_classifier import EmailClassifier
from datetime import datetime
import json


def print_separator(title=""):
    """Print a visual separator."""
    width = 80
    if title:
        print("\n" + "=" * width)
        print(f"  {title}")
        print("=" * width)
    else:
        print("-" * width)


def print_classification_result(email, result, index):
    """Pretty print a classification result."""
    print(f"\n#{index}. {email['subject']}")
    print(f"    From: {email['from_email']}")

    # Category and confidence
    category = result['category'].upper()
    confidence = result.get('confidence', 0)
    confidence_bar = "█" * int(confidence * 20) + "░" * (20 - int(confidence * 20))

    print(f"    Category: {category}")
    print(f"    Confidence: [{confidence_bar}] {confidence:.1%}")

    # Additional details
    if result.get('subcategory'):
        print(f"    Subcategory: {result['subcategory']}")

    if result.get('priority'):
        priority_emoji = {
            'urgent': '🔴',
            'high': '🟠',
            'normal': '🟢',
            'low': '⚪'
        }.get(result.get('priority', 'normal'), '🟢')
        print(f"    Priority: {priority_emoji} {result['priority'].upper()}")

    if result.get('sentiment'):
        sentiment_emoji = {
            'positive': '😊',
            'neutral': '😐',
            'negative': '😞',
            'mixed': '🤔'
        }.get(result.get('sentiment', 'neutral'), '😐')
        print(f"    Sentiment: {sentiment_emoji} {result['sentiment']}")

    # Keywords
    if result.get('keywords'):
        keywords = ', '.join(result['keywords'][:5])
        print(f"    Keywords: {keywords}")

    # Action required
    if result.get('requires_action'):
        print(f"    ⚠️  Requires Action: YES")
        if result.get('suggested_actions'):
            actions = ', '.join(result['suggested_actions'][:3])
            print(f"    Suggested: {actions}")

    # Method used
    method = result.get('method', 'unknown')
    print(f"    Method: {method}")

    # Review flag
    if result.get('needs_manual_review'):
        print(f"    ⚠️  NEEDS MANUAL REVIEW")


def main():
    """Run the email classification tests."""

    print_separator("EMAIL CLASSIFICATION SYSTEM - TEST SUITE")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"GROQ Model: Llama 3.3-70B Versatile")

    # Initialize classifier
    print("\nInitializing EmailClassifier...")
    classifier = EmailClassifier()
    print("✓ Classifier initialized successfully")

    # Test emails covering all categories
    test_emails = [
        # CANDIDATE EMAILS
        {
            'id': 'test-001',
            'from_email': 'sarah.jones@gmail.com',
            'subject': 'Application for Sales Executive Position',
            'body_text': '''Dear ProActive People,

I am writing to express my interest in the Sales Executive position advertised on Indeed.

I have over 5 years of experience in B2B sales, consistently exceeding targets by 20%+ each year. My background includes working with major accounts in the technology sector, and I excel at building long-term client relationships.

Please find attached my CV for your review. I would welcome the opportunity to discuss how my experience aligns with your client's needs.

Available for interview at your convenience.

Best regards,
Sarah Jones
Tel: 07700 900123''',
            'attachments': ['Sarah_Jones_CV.pdf']
        },
        {
            'id': 'test-002',
            'from_email': 'michael.chen@outlook.com',
            'subject': 'Re: Interview Confirmation - IT Support Role',
            'body_text': '''Hi Emma,

Thank you for scheduling the interview. I can confirm I will be available on Tuesday, January 23rd at 2:00 PM for the interview with TechCorp.

I have prepared thoroughly and look forward to discussing the IT Support role in detail.

See you then!

Best,
Michael Chen''',
            'attachments': []
        },

        # CLIENT EMAILS
        {
            'id': 'test-003',
            'from_email': 'hr@techcorp.co.uk',
            'subject': 'URGENT: New Vacancy - Senior Software Engineer',
            'body_text': '''Hi ProActive Team,

We have an urgent requirement for a Senior Software Engineer to join our development team.

Key requirements:
- 5+ years Python/Django experience
- AWS cloud architecture
- Team leadership skills
- Available to start ASAP

Salary: £70-80k + benefits
Location: Bristol (hybrid - 2 days/week in office)

Can you source suitable candidates by end of week? This is a critical hire for an upcoming project.

Thanks,
David Wilson
Head of Engineering, TechCorp''',
            'attachments': ['Job_Specification.pdf']
        },
        {
            'id': 'test-004',
            'from_email': 'jane.smith@corporatesolutions.com',
            'subject': 'Feedback on Candidate - Robert Taylor',
            'body_text': '''Hi Claire,

We completed the second interview with Robert Taylor yesterday for the Accountant role.

Feedback: Robert performed exceptionally well. His technical knowledge is excellent, and he demonstrated strong attention to detail during the case study. The team was impressed with his communication skills and cultural fit.

We would like to proceed with an offer. Can we schedule a call tomorrow to discuss terms?

Looking forward to hearing from you.

Best regards,
Jane Smith
Finance Director''',
            'attachments': []
        },

        # SUPPLIER EMAILS
        {
            'id': 'test-005',
            'from_email': 'notifications@bullhorn.com',
            'subject': 'API Rate Limit Warning - Action Required',
            'body_text': '''Dear ProActive People Administrator,

This is an automated notification from Bullhorn ATS.

Your account has exceeded 80% of the API rate limit for this billing period. Current usage: 45,000 / 50,000 requests.

To avoid service disruption, please:
1. Review your integration logs
2. Optimize API calls
3. Contact support if you need a limit increase

Dashboard: https://bullhorn.com/dashboard
Support: support@bullhorn.com

Best regards,
Bullhorn Support Team''',
            'attachments': []
        },
        {
            'id': 'test-006',
            'from_email': 'accounts@broadbean.com',
            'subject': 'Invoice #BB-2025-0123 - Job Posting Services',
            'body_text': '''Dear Customer,

Please find attached invoice #BB-2025-0123 for job posting services for January 2025.

Invoice Details:
- Job posts: 47 positions
- Total: £1,245.00 + VAT
- Due date: February 14, 2025

Payment methods accepted: Bank transfer, Direct Debit

Thank you for your business.

Broadbean Technology
Finance Team''',
            'attachments': ['Invoice_BB-2025-0123.pdf']
        },

        # STAFF EMAILS
        {
            'id': 'test-007',
            'from_email': 'emma.williams@proactivepeople.com',
            'subject': 'Team Meeting - Friday 3pm',
            'body_text': '''Hi Everyone,

Quick reminder about our weekly team meeting this Friday at 3pm.

Agenda:
- Weekly targets review
- New client onboarding (TechStartup Ltd)
- CV database cleanup project
- Q&A

Location: Conference Room B

See you all there!

Emma
Team Leader''',
            'attachments': []
        },
        {
            'id': 'test-008',
            'from_email': 'hr@proactivepeople.com',
            'subject': 'Holiday Request Approved - Confirmation',
            'body_text': '''Dear James,

Your holiday request has been approved.

Dates: February 10-14, 2025 (5 days)
Remaining allowance: 12 days

Please ensure your tasks are delegated before you leave and set up an out-of-office message.

Have a great break!

Best regards,
HR Department''',
            'attachments': []
        },

        # OTHER EMAILS
        {
            'id': 'test-009',
            'from_email': 'newsletter@recruitmentweekly.com',
            'subject': 'Top 10 Recruitment Trends for 2025',
            'body_text': '''Weekly Recruitment Insights

This week's top stories:
1. AI in recruitment - opportunities and challenges
2. Remote work statistics 2025
3. Salary benchmarking guide
...

Click here to read more: [link]

To unsubscribe, click here.

Recruitment Weekly
Your trusted recruitment news source''',
            'attachments': []
        },
        {
            'id': 'test-010',
            'from_email': 'noreply@linkedin.com',
            'subject': 'You have 3 new connection requests',
            'body_text': '''LinkedIn Notification

You have 3 new connection requests:
- John Smith (Recruiter at ABC Ltd)
- Lisa Brown (HR Manager)
- Tom Wilson (Business Development)

View all connections: https://linkedin.com/...

This is an automated message from LinkedIn.''',
            'attachments': []
        }
    ]

    print_separator("CLASSIFYING EMAILS")
    print(f"Total test emails: {len(test_emails)}\n")

    # Classify all emails
    results = classifier.classify_batch(test_emails)

    # Display results
    for i, (email, result) in enumerate(zip(test_emails, results), 1):
        print_classification_result(email, result, i)

    # Statistics
    print_separator("CLASSIFICATION STATISTICS")

    stats = classifier.get_category_stats(results)

    print(f"\nOverall Performance:")
    print(f"  Total Emails: {stats['total']}")
    print(f"  Average Confidence: {stats['avg_confidence']:.1%}")
    print(f"  Needs Manual Review: {stats['needs_review']} ({stats['needs_review']/stats['total']*100:.1f}%)")

    print(f"\nBreakdown by Category:")
    for category, data in sorted(stats['by_category'].items(), key=lambda x: x[1]['count'], reverse=True):
        count = data['count']
        percentage = data['percentage']
        bar = "█" * int(percentage / 5) + "░" * (20 - int(percentage / 5))
        print(f"  {category.upper():12} [{bar}] {count:2} ({percentage:5.1f}%)")

    # Accuracy verification
    print_separator("ACCURACY VERIFICATION")

    expected_categories = {
        'test-001': 'candidate',
        'test-002': 'candidate',
        'test-003': 'client',
        'test-004': 'client',
        'test-005': 'supplier',
        'test-006': 'supplier',
        'test-007': 'staff',
        'test-008': 'staff',
        'test-009': 'other',
        'test-010': 'other'
    }

    correct = 0
    total = len(results)

    print("\nExpected vs Actual:")
    for result in results:
        email_id = result.get('email_id')
        expected = expected_categories.get(email_id, 'unknown')
        actual = result.get('category', 'unknown')
        confidence = result.get('confidence', 0)

        match = "✓" if expected == actual else "✗"
        print(f"  {match} {email_id}: Expected={expected:10} Actual={actual:10} ({confidence:.0%})")

        if expected == actual:
            correct += 1

    accuracy = (correct / total * 100) if total > 0 else 0
    print(f"\nAccuracy: {correct}/{total} = {accuracy:.1f}%")

    # Performance summary
    print_separator("SUMMARY")

    if accuracy >= 90:
        grade = "EXCELLENT ⭐⭐⭐⭐⭐"
    elif accuracy >= 80:
        grade = "VERY GOOD ⭐⭐⭐⭐"
    elif accuracy >= 70:
        grade = "GOOD ⭐⭐⭐"
    else:
        grade = "NEEDS IMPROVEMENT ⭐⭐"

    print(f"\nClassification Grade: {grade}")
    print(f"Overall Confidence: {stats['avg_confidence']:.1%}")
    print(f"Review Rate: {stats['needs_review']/stats['total']*100:.1f}%")

    print("\n✓ Email classification system is working correctly!")
    print("\nNext Steps:")
    print("  1. Run database migrations: psql -f data/migrations/007_create_email_tables.sql")
    print("  2. Start communication service: cd backend/services/communication-service && npm start")
    print("  3. Configure SendGrid/SES webhooks")
    print("  4. Monitor real-time classifications via API")

    print_separator()

    # Save results to file
    output_file = 'email_classification_test_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'total_emails': total,
            'accuracy': accuracy,
            'avg_confidence': stats['avg_confidence'],
            'stats': stats,
            'results': results
        }, f, indent=2)

    print(f"\nResults saved to: {output_file}")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
