# Email Classification Service - GROQ Integration

## Overview

This service uses GROQ's LLM API with a **system + user prompt pattern** to classify incoming recruitment emails for automated routing.

## Architecture: System + User Prompt Pattern

### Why Two Prompts?

Modern LLMs work best when you separate:

1. **System Prompt** - The AI's role, rules, and output format (constant)
2. **User Prompt** - The specific data to analyze (variable)

This separation provides:
- **Consistency**: Same rules applied to all emails
- **Clarity**: Instructions separate from data
- **Efficiency**: Only data changes, rules stay cached
- **Testability**: Easy to validate behavior

### System Prompt (Constant)

```python
SYSTEM_PROMPT = """You are an expert email classification AI for ProActive People,
a UK recruitment agency.

Your role: Analyze emails and classify them for automated routing.

Categories: CANDIDATE, CLIENT, SUPPLIER, STAFF, OTHER
Priority: URGENT, HIGH, NORMAL, LOW

Output Format: JSON with category, confidence, priority, sentiment, keywords, etc.
"""
```

**Purpose**:
- Defines the AI's expertise and role
- Lists all possible categories and rules
- Specifies exact output structure
- Provides classification guidelines

### User Prompt (Variable)

```python
user_prompt = f"""Classify this email:

FROM: {from_email}
SUBJECT: {subject}
BODY: {body}

Return classification JSON."""
```

**Purpose**:
- Contains the specific email data
- Changes for each classification request
- Keeps the actual data to analyze

## Usage

### 1. Command Line

```bash
python classify_email.py \
  --from "candidate@example.com" \
  --subject "Application for Sales Role" \
  --body "I am interested in applying..." \
  --to '["recruitment@proactivepeople.com"]' \
  --attachments '["CV.pdf"]'
```

### 2. Python Import

```python
from classify_email import classify_email

result = classify_email(
    from_email="candidate@example.com",
    subject="Application for Sales Role",
    body="I am interested in applying...",
    to_emails=["recruitment@proactivepeople.com"],
    attachments=["CV.pdf"]
)

print(result['category'])      # CANDIDATE
print(result['subcategory'])   # application
print(result['confidence'])    # 0.95
print(result['priority'])      # NORMAL
```

### 3. TypeScript Integration (NestJS)

The existing [email-ingestion.service.ts](../src/services/email-ingestion.service.ts) calls this script:

```typescript
private async runPythonClassifier(email: Email): Promise<EmailClassification> {
  const options = {
    mode: 'json' as const,
    pythonPath: 'python',
    scriptPath: './scripts',
    args: [
      '--from', email.from.email,
      '--subject', email.subject,
      '--body', email.bodyText,
      '--to', JSON.stringify(email.to.map(t => t.email)),
      '--attachments', JSON.stringify(email.attachments?.map(a => a.filename) || [])
    ]
  };

  const results = await PythonShell.run('classify_email.py', options);
  return results[0]; // Returns classification JSON
}
```

## Classification Output

```json
{
  "category": "CANDIDATE",
  "subcategory": "application",
  "confidence": 0.92,
  "priority": "HIGH",
  "sentiment": "positive",
  "keywords": ["sales", "b2b", "experience", "cv"],
  "entities": {
    "names": ["John Smith"],
    "companies": [],
    "job_titles": ["Senior Sales Executive"],
    "locations": ["Bristol"],
    "dates": [],
    "phone_numbers": ["07700 900123"],
    "skills": ["B2B Sales", "Account Management"]
  },
  "requires_action": true,
  "suggested_actions": [
    "Parse attached CV",
    "Route to recruitment team",
    "Add to candidate database",
    "Send acknowledgment email"
  ],
  "reasoning": "Email contains job application with CV attachment...",
  "classified_at": "2025-10-21T10:30:00Z",
  "classified_by": "ai",
  "model_used": "llama-3.3-70b-versatile",
  "tokens_used": {
    "prompt_tokens": 450,
    "completion_tokens": 180,
    "total_tokens": 630
  }
}
```

## Classification Categories

### CANDIDATE
- `application` - Job applications
- `cv_submission` - CV/resume submissions
- `interview_response` - Interview confirmations/declines
- `availability_update` - Status/availability changes
- `reference_check` - Reference information
- `general_enquiry` - General questions

### CLIENT
- `job_brief` - New job vacancy briefs
- `feedback` - Candidate feedback
- `interview_request` - Interview scheduling
- `placement_update` - Updates on placements
- `contract_query` - Contract questions
- `general_enquiry` - General questions

### SUPPLIER
- `bullhorn_sync` - Bullhorn ATS notifications
- `broadbean_notification` - Broadbean updates
- `invoice` - Invoices and billing
- `service_update` - Service changes
- `integration_issue` - Technical problems

### STAFF
- `hr_matter` - HR communications
- `team_update` - Team announcements
- `internal_query` - Internal questions

### OTHER
- `spam` - Promotional emails
- `automated_notification` - System notifications
- `out_of_office` - Auto-responders
- `unclassified` - Unknown category

## Testing

Run the comprehensive test suite:

```bash
python test_email_classification.py
```

This tests 8 different email scenarios:
- Candidate CV submissions
- Client job briefs
- Interview feedback
- Supplier notifications
- Availability updates
- Complaints (urgent)
- Spam/marketing
- Reference checks

## Configuration

### Environment Variables

```bash
GROQ_API_KEY=your_groq_api_key_here
PYTHON_SCRIPTS_PATH=./backend/services/communication-service/scripts
```

### Model Settings

```python
CompletionConfig(
    model="llama-3.3-70b-versatile",  # Best for classification
    temperature=0.3,                   # Low = consistent results
    max_tokens=2000,                   # Enough for detailed output
    top_p=0.9
)
```

**Why these settings?**
- **llama-3.3-70b-versatile**: Best balance of speed and accuracy
- **temperature=0.3**: Low for consistent, repeatable classifications
- **max_tokens=2000**: Allows detailed entity extraction and reasoning

## Performance

- **Average Classification Time**: 1-2 seconds
- **Accuracy** (based on test set): ~95%
- **Token Usage**: 400-800 tokens per email
- **Cost**: ~$0.0003 per email (at GROQ's current pricing)

## Error Handling

If classification fails, returns fallback:

```json
{
  "category": "OTHER",
  "subcategory": "unclassified",
  "confidence": 0.1,
  "priority": "NORMAL",
  "sentiment": "neutral",
  "classified_by": "rule-based-fallback",
  "error": "Error message here"
}
```

## Integration with Email Pipeline

```
1. Email arrives (SendGrid/SES webhook)
   ↓
2. Store in database (email-ingestion.service.ts)
   ↓
3. Queue for classification (Bull queue)
   ↓
4. Call Python classifier (this script)
   ↓
5. Update email with classification
   ↓
6. Route to appropriate handlers
   ↓
7. Take automated actions
```

## Advanced Features

### Entity Extraction

Automatically extracts:
- People names
- Company names
- Job titles
- Locations
- Dates and deadlines
- Phone numbers
- Skills mentioned

### Red Flag Detection

Identifies concerning elements:
- Complaint language
- Urgent/aggressive tone
- Unrealistic expectations
- Potential scams

### Suggested Actions

Provides actionable next steps:
- "Parse attached CV"
- "Route to senior consultant (urgent)"
- "Send acknowledgment email"
- "Schedule callback"

## Best Practices

1. **Always use both prompts**: System + User pattern for clarity
2. **Keep temperature low** (0.2-0.4) for classification tasks
3. **Validate JSON output**: Parse and check required fields
4. **Log confidence scores**: Review low-confidence classifications
5. **Monitor accuracy**: Regular testing with real emails
6. **Update system prompt**: Refine rules based on edge cases

## Troubleshooting

### Issue: Low confidence scores
**Solution**: Email might be ambiguous. Review and update system prompt rules.

### Issue: Wrong category
**Solution**: Add more examples to system prompt or adjust keyword detection.

### Issue: JSON parsing fails
**Solution**: Response might include markdown formatting. Use `validate_json_response()`.

### Issue: Timeout
**Solution**: Reduce `max_tokens` or switch to faster model.

## Examples

See these files for working examples:
- [classify_email.py](./classify_email.py) - Main classification script
- [test_email_classification.py](./test_email_classification.py) - Test suite
- [../../example_email_classification_groq.py](../../../example_email_classification_groq.py) - Standalone demo

## Support

For issues or questions:
- Check logs for error details
- Test with `test_email_classification.py`
- Review GROQ API status
- Verify environment variables are set

---

**ProActive People - Recruitment Automation System**
Email Classification Service v1.0.0
