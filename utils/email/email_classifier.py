"""
Email Classification Service using GROQ AI
ProActive People - Recruitment Automation System

Categorizes emails as: Candidate, Client, Supplier, Staff, or Other
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from groq_client import GroqClient, TaskType


class EmailClassifier:
    """
    AI-powered email classifier using GROQ Llama 3.3-70B model.
    Categorizes emails and extracts relevant entities and metadata.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the email classifier with GROQ client."""
        self.groq = GroqClient(api_key=api_key)

        # Category detection patterns (rule-based fallback)
        self.patterns = {
            'candidate': [
                r'\bcv\b', r'\bresume\b', r'\bapplication\b',
                r'\bapplying for\b', r'\bjob opportunity\b',
                r'\binterview\b', r'\bavailability\b',
                r'\bnotice period\b', r'\bsalary expectation\b'
            ],
            'client': [
                r'\bjob brief\b', r'\bvacancy\b', r'\bhiring\b',
                r'\bfeedback on candidate\b', r'\binterview slot\b',
                r'\bplacement\b', r'\bcontract\b', r'\bstart date\b',
                r'\brate\b', r'\bservice level agreement\b'
            ],
            'supplier': [
                r'\binvoice\b', r'\bpayment\b', r'\bbullhorn\b',
                r'\bbroadbean\b', r'\bintegration\b', r'\bapi\b',
                r'\bservice status\b', r'\bmaintenance\b',
                r'\bjob board\b', r'\bsubscription\b'
            ],
            'staff': [
                r'\bteam meeting\b', r'\binternal\b', r'\bhr\b',
                r'\bholiday request\b', r'\bexpense claim\b',
                r'\b1-2-1\b', r'\bperformance review\b',
                r'\btraining\b', r'\bcompany update\b'
            ],
            'spam': [
                r'\bunsubscribe\b', r'\bclick here\b',
                r'\bfree money\b', r'\bwin now\b',
                r'\blimited time offer\b', r'\bact now\b'
            ]
        }

        # Known supplier domains
        self.supplier_domains = [
            'bullhorn.com', 'broadbean.com', 'indeed.com',
            'totaljobs.com', 'cv-library.co.uk', 'reed.co.uk',
            'sendgrid.com', 'aws.amazon.com', 'stripe.com'
        ]

        # Internal staff domains (customize for your organization)
        self.staff_domains = [
            'proactivepeople.com', 'proactive-people.co.uk'
        ]

    def classify_email(
        self,
        from_email: str,
        subject: str,
        body_text: str,
        to_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict:
        """
        Classify an email into one of: candidate, client, supplier, staff, other.

        Args:
            from_email: Sender email address
            subject: Email subject line
            body_text: Email body content (plain text)
            to_emails: List of recipient email addresses
            attachments: List of attachment filenames

        Returns:
            Classification results with category, confidence, priority, etc.
        """
        # First apply rule-based classification
        rule_based_result = self._rule_based_classification(
            from_email, subject, body_text, attachments
        )

        # Then apply AI classification
        ai_result = self._ai_classification(
            from_email, subject, body_text, to_emails, attachments
        )

        # Combine results (AI takes precedence if confidence > 0.7)
        final_result = self._merge_classifications(rule_based_result, ai_result)

        return final_result

    def _rule_based_classification(
        self,
        from_email: str,
        subject: str,
        body_text: str,
        attachments: Optional[List[str]] = None
    ) -> Dict:
        """Apply pattern-based rules for quick classification."""
        from_domain = from_email.split('@')[-1].lower() if '@' in from_email else ''
        combined_text = f"{subject} {body_text}".lower()

        # Check staff domain
        if from_domain in self.staff_domains:
            return {
                'category': 'staff',
                'confidence': 0.95,
                'method': 'rule-based',
                'reason': 'Internal email domain'
            }

        # Check supplier domain
        if from_domain in self.supplier_domains:
            return {
                'category': 'supplier',
                'confidence': 0.90,
                'method': 'rule-based',
                'reason': 'Known supplier domain'
            }

        # Pattern matching
        scores = {cat: 0 for cat in ['candidate', 'client', 'supplier', 'staff', 'spam']}

        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    scores[category] += 1

        # Check for CV attachment (strong candidate signal)
        if attachments:
            cv_patterns = [r'\.pdf$', r'\.docx?$', r'\bcv\b', r'\bresume\b']
            for attachment in attachments:
                for pattern in cv_patterns:
                    if re.search(pattern, attachment, re.IGNORECASE):
                        scores['candidate'] += 3
                        break

        # Determine category from scores
        if max(scores.values()) == 0:
            return {
                'category': 'other',
                'confidence': 0.5,
                'method': 'rule-based',
                'reason': 'No pattern matches'
            }

        category = max(scores, key=scores.get)
        confidence = min(0.85, scores[category] / 10)  # Cap at 0.85 for rule-based

        return {
            'category': category if category != 'spam' else 'other',
            'confidence': confidence,
            'method': 'rule-based',
            'reason': f'Pattern matches: {scores[category]}'
        }

    def _ai_classification(
        self,
        from_email: str,
        subject: str,
        body_text: str,
        to_emails: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None
    ) -> Dict:
        """Use GROQ AI for intelligent email classification."""

        # Prepare context for AI
        context = {
            'from': from_email,
            'subject': subject,
            'body': body_text[:2000],  # Limit body length
            'to': to_emails or [],
            'attachments': attachments or []
        }

        # Craft classification prompt
        prompt = self._build_classification_prompt(context)

        try:
            # Use GROQ for classification
            response = self.groq.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an email classification expert for a recruitment agency.
Classify emails into exactly one category: candidate, client, supplier, staff, or other.
Also identify: subcategory, priority (urgent/high/normal/low), sentiment (positive/neutral/negative),
keywords, and whether action is required.

Respond ONLY with valid JSON in this format:
{
  "category": "candidate|client|supplier|staff|other",
  "subcategory": "string",
  "confidence": 0.0-1.0,
  "priority": "urgent|high|normal|low",
  "sentiment": "positive|neutral|negative|mixed",
  "keywords": ["keyword1", "keyword2"],
  "requires_action": true|false,
  "suggested_actions": ["action1", "action2"],
  "reasoning": "brief explanation"
}"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=500
            )

            # Parse AI response
            ai_output = response.choices[0].message.content.strip()
            result = self._parse_ai_response(ai_output)
            result['method'] = 'ai'

            return result

        except Exception as e:
            print(f"AI classification error: {e}")
            return {
                'category': 'other',
                'confidence': 0.3,
                'method': 'ai-error',
                'error': str(e)
            }

    def _build_classification_prompt(self, context: Dict) -> str:
        """Build the classification prompt for the AI."""
        attachments_str = ", ".join(context['attachments']) if context['attachments'] else "None"

        return f"""Classify this email for a recruitment agency (ProActive People).

**Email Details:**
- From: {context['from']}
- To: {', '.join(context['to'])}
- Subject: {context['subject']}
- Attachments: {attachments_str}

**Email Body:**
{context['body']}

**Categories:**
- candidate: Job applications, CV submissions, interview responses, availability updates
- client: Companies hiring, job briefs, candidate feedback, interview requests, placements
- supplier: Bullhorn, Broadbean, job boards, software vendors, invoices
- staff: Internal emails from @proactivepeople.com team members
- other: Marketing, spam, newsletters, unrelated

Classify this email and provide detailed analysis."""

    def _parse_ai_response(self, ai_output: str) -> Dict:
        """Parse JSON response from AI, with fallback handling."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_output, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())

                # Validate required fields
                if 'category' not in result:
                    result['category'] = 'other'
                if 'confidence' not in result:
                    result['confidence'] = 0.5

                return result
            else:
                raise ValueError("No JSON found in AI response")

        except (json.JSONDecodeError, ValueError) as e:
            print(f"AI response parsing error: {e}\nResponse: {ai_output}")
            return {
                'category': 'other',
                'confidence': 0.3,
                'error': 'Failed to parse AI response'
            }

    def _merge_classifications(self, rule_result: Dict, ai_result: Dict) -> Dict:
        """Merge rule-based and AI classifications intelligently."""

        # If AI has high confidence, use it
        if ai_result.get('confidence', 0) >= 0.7:
            return {
                **ai_result,
                'rule_based_category': rule_result.get('category'),
                'rule_based_confidence': rule_result.get('confidence')
            }

        # If rule-based has high confidence, use it but add AI insights
        if rule_result.get('confidence', 0) >= 0.8:
            return {
                **rule_result,
                'subcategory': ai_result.get('subcategory'),
                'priority': ai_result.get('priority', 'normal'),
                'sentiment': ai_result.get('sentiment', 'neutral'),
                'keywords': ai_result.get('keywords', []),
                'requires_action': ai_result.get('requires_action', False),
                'suggested_actions': ai_result.get('suggested_actions', []),
                'ai_category': ai_result.get('category'),
                'ai_confidence': ai_result.get('confidence')
            }

        # Both have medium confidence - prefer AI but flag for review
        return {
            **ai_result,
            'confidence': (ai_result.get('confidence', 0.5) + rule_result.get('confidence', 0.5)) / 2,
            'needs_manual_review': True,
            'rule_based_category': rule_result.get('category'),
            'rule_based_confidence': rule_result.get('confidence')
        }

    def classify_batch(self, emails: List[Dict]) -> List[Dict]:
        """
        Classify multiple emails in batch.

        Args:
            emails: List of email dicts with keys: from_email, subject, body_text, etc.

        Returns:
            List of classification results
        """
        results = []

        for email in emails:
            try:
                result = self.classify_email(
                    from_email=email.get('from_email', ''),
                    subject=email.get('subject', ''),
                    body_text=email.get('body_text', ''),
                    to_emails=email.get('to_emails'),
                    attachments=email.get('attachments')
                )
                result['email_id'] = email.get('id', email.get('message_id'))
                results.append(result)
            except Exception as e:
                results.append({
                    'email_id': email.get('id', email.get('message_id')),
                    'category': 'other',
                    'confidence': 0.0,
                    'error': str(e)
                })

        return results

    def get_category_stats(self, classifications: List[Dict]) -> Dict:
        """Calculate statistics across multiple classifications."""
        stats = {
            'total': len(classifications),
            'by_category': {},
            'avg_confidence': 0.0,
            'needs_review': 0
        }

        confidences = []

        for result in classifications:
            category = result.get('category', 'other')
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1

            confidence = result.get('confidence', 0.0)
            confidences.append(confidence)

            if result.get('needs_manual_review') or confidence < 0.6:
                stats['needs_review'] += 1

        stats['avg_confidence'] = sum(confidences) / len(confidences) if confidences else 0.0

        # Calculate percentages
        for category, count in stats['by_category'].items():
            stats['by_category'][category] = {
                'count': count,
                'percentage': round(count / stats['total'] * 100, 2)
            }

        return stats


def main():
    """Example usage of the EmailClassifier."""

    # Initialize classifier
    classifier = EmailClassifier()

    # Test emails
    test_emails = [
        {
            'id': 'email-001',
            'from_email': 'john.smith@gmail.com',
            'subject': 'Application for Sales Executive Role',
            'body_text': 'Dear Hiring Manager, I am writing to apply for the Sales Executive position. '
                        'Please find attached my CV. I have 5 years experience in B2B sales.',
            'attachments': ['John_Smith_CV.pdf']
        },
        {
            'id': 'email-002',
            'from_email': 'hr@techcorp.co.uk',
            'subject': 'Feedback on candidate - Sarah Jones',
            'body_text': 'Hi, Thanks for sending Sarah for interview. She performed very well and we would '
                        'like to proceed to a second interview. Can we schedule for next Tuesday?',
            'attachments': []
        },
        {
            'id': 'email-003',
            'from_email': 'support@bullhorn.com',
            'subject': 'API Rate Limit Notification',
            'body_text': 'Your account has exceeded the API rate limit. Please review your integration.',
            'attachments': []
        },
        {
            'id': 'email-004',
            'from_email': 'emma@proactivepeople.com',
            'subject': 'Team Meeting - Friday 2pm',
            'body_text': 'Hi team, Reminder about our weekly catch-up this Friday at 2pm. See you there!',
            'attachments': []
        }
    ]

    print("=" * 80)
    print("EMAIL CLASSIFICATION DEMO")
    print("=" * 80)
    print()

    # Classify each email
    results = classifier.classify_batch(test_emails)

    for i, result in enumerate(results, 1):
        email = test_emails[i-1]
        print(f"Email #{i}: {email['subject']}")
        print(f"  From: {email['from_email']}")
        print(f"  Category: {result['category'].upper()}")
        print(f"  Confidence: {result['confidence']:.2%}")

        if result.get('subcategory'):
            print(f"  Subcategory: {result['subcategory']}")
        if result.get('priority'):
            print(f"  Priority: {result['priority']}")
        if result.get('sentiment'):
            print(f"  Sentiment: {result['sentiment']}")
        if result.get('requires_action'):
            print(f"  Requires Action: YES")
            if result.get('suggested_actions'):
                print(f"  Suggested Actions: {', '.join(result['suggested_actions'])}")

        print(f"  Method: {result.get('method', 'unknown')}")

        if result.get('needs_manual_review'):
            print("  ⚠️  NEEDS MANUAL REVIEW")

        print()

    # Show statistics
    stats = classifier.get_category_stats(results)
    print("=" * 80)
    print("CLASSIFICATION STATISTICS")
    print("=" * 80)
    print(f"Total Emails: {stats['total']}")
    print(f"Average Confidence: {stats['avg_confidence']:.2%}")
    print(f"Needs Review: {stats['needs_review']}")
    print()
    print("By Category:")
    for category, data in stats['by_category'].items():
        print(f"  {category.upper()}: {data['count']} ({data['percentage']}%)")


if __name__ == '__main__':
    main()
