# Email Categorization System - Flow Diagram

## Overall System Flow

```
┌──────────────────────────────────────────────────────────────────────┐
│                         INCOMING EMAILS                               │
│                                                                       │
│  📧 Candidate Applications  │  📧 Client Briefs  │  📧 Supplier Msgs  │
│  📧 Interview Responses     │  📧 Feedback       │  📧 Staff Comms    │
└───────────────────────┬──────────────────────────────────────────────┘
                        │
                        │  SendGrid/SES Webhook
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  EMAIL INGESTION SERVICE (NestJS)                     │
│                                                                       │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  1. Webhook Handler                                     │         │
│  │     • Parse email payload                               │         │
│  │     • Extract sender, recipients, subject, body         │         │
│  │     • Store attachments                                 │         │
│  └────────────────────────────────────────────────────────┘         │
│                        │                                              │
│                        ▼                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  2. Database Storage                                    │         │
│  │     • Save to email_messages table                      │         │
│  │     • Generate unique ID                                │         │
│  │     • Set processed = false                             │         │
│  └────────────────────────────────────────────────────────┘         │
│                        │                                              │
│                        ▼                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  3. Queue for Classification                            │         │
│  │     • Add to RabbitMQ queue                             │         │
│  │     • Set priority based on keywords                    │         │
│  │     • Track queue position                              │         │
│  └────────────────────────────────────────────────────────┘         │
└───────────────────────┬──────────────────────────────────────────────┘
                        │
                        │  Queue Message
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│              EMAIL CLASSIFIER (Python + GROQ AI)                      │
│                                                                       │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  STEP 1: Rule-Based Pre-Classification                 │         │
│  │  ───────────────────────────────────────────────       │         │
│  │  ✓ Domain Recognition                                  │         │
│  │    • proactivepeople.com → STAFF                       │         │
│  │    • bullhorn.com → SUPPLIER                           │         │
│  │                                                         │         │
│  │  ✓ Keyword Pattern Matching                            │         │
│  │    • "cv", "application" → CANDIDATE                   │         │
│  │    • "job brief", "vacancy" → CLIENT                   │         │
│  │    • "invoice", "payment" → SUPPLIER                   │         │
│  │                                                         │         │
│  │  ✓ Attachment Detection                                │         │
│  │    • .pdf, .docx with "CV" → CANDIDATE                 │         │
│  │                                                         │         │
│  │  Result: {category, confidence: 0-0.85}                │         │
│  └────────────────────────────────────────────────────────┘         │
│                        │                                              │
│                        ▼                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  STEP 2: AI Classification (GROQ Llama 3.3-70B)        │         │
│  │  ───────────────────────────────────────────────       │         │
│  │  📝 Prompt Construction:                                │         │
│  │     • From/To/Subject/Body                              │         │
│  │     • Attachment names                                  │         │
│  │     • Context about business                            │         │
│  │                                                         │         │
│  │  🤖 AI Analysis:                                        │         │
│  │     • Context understanding                             │         │
│  │     • Intent recognition                                │         │
│  │     • Entity extraction                                 │         │
│  │     • Sentiment analysis                                │         │
│  │     • Priority detection                                │         │
│  │     • Action suggestions                                │         │
│  │                                                         │         │
│  │  Result: {category, subcategory, confidence: 0-1,       │         │
│  │           priority, sentiment, keywords, entities}      │         │
│  └────────────────────────────────────────────────────────┘         │
│                        │                                              │
│                        ▼                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  STEP 3: Hybrid Merging                                │         │
│  │  ───────────────────────────────────────────────       │         │
│  │  Decision Logic:                                        │         │
│  │                                                         │         │
│  │  IF AI confidence >= 0.7:                              │         │
│  │    → Use AI classification                              │         │
│  │                                                         │         │
│  │  ELSE IF Rule confidence >= 0.8:                       │         │
│  │    → Use rule-based, add AI insights                   │         │
│  │                                                         │         │
│  │  ELSE:                                                  │         │
│  │    → Combine both, flag for manual review              │         │
│  │                                                         │         │
│  │  Final Result: {category, confidence, metadata,        │         │
│  │                 needs_manual_review: true/false}       │         │
│  └────────────────────────────────────────────────────────┘         │
└───────────────────────┬──────────────────────────────────────────────┘
                        │
                        │  Classification Result
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│              UPDATE DATABASE (PostgreSQL)                             │
│                                                                       │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  1. Store Classification                                │         │
│  │     INSERT INTO email_classifications (...)             │         │
│  │     • category, subcategory                             │         │
│  │     • confidence, priority, sentiment                   │         │
│  │     • keywords, entities                                │         │
│  │     • requires_action, suggested_actions                │         │
│  └────────────────────────────────────────────────────────┘         │
│                        │                                              │
│                        ▼                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  2. Update Email Status                                 │         │
│  │     UPDATE email_messages SET                           │         │
│  │     • processed = true                                  │         │
│  │     • processed_at = NOW()                              │         │
│  └────────────────────────────────────────────────────────┘         │
│                        │                                              │
│                        ▼                                              │
│  ┌────────────────────────────────────────────────────────┐         │
│  │  3. Auto-Link Entities (Trigger)                        │         │
│  │     • Link to candidate_id if entities.candidates       │         │
│  │     • Link to client_id if entities.clients             │         │
│  │     • Link to job_id if entities.jobs                   │         │
│  └────────────────────────────────────────────────────────┘         │
└───────────────────────┬──────────────────────────────────────────────┘
                        │
                        │  Classification Complete
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    EMAIL ROUTER (NestJS)                              │
│                                                                       │
│  Route based on category:                                            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────┐            │
│  │  📥 CANDIDATE Emails                                 │            │
│  │  ─────────────────────────────────────────────      │            │
│  │  → Candidate Service (8081)                         │            │
│  │  → CV Parser (if attachments)                       │            │
│  │  → Matching Engine (8084)                           │            │
│  │  → Workflow Service (8085)                          │            │
│  │                                                      │            │
│  │  IF subcategory = "application":                    │            │
│  │    → Trigger CV parsing                             │            │
│  │    → Create candidate profile                       │            │
│  │                                                      │            │
│  │  IF subcategory = "interview_response":             │            │
│  │    → Scheduling Service (8086)                      │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────┐            │
│  │  🏢 CLIENT Emails                                    │            │
│  │  ─────────────────────────────────────────────      │            │
│  │  → Client Service (8082)                            │            │
│  │  → Job Service (8083)                               │            │
│  │  → Account Manager                                  │            │
│  │                                                      │            │
│  │  IF subcategory = "job_brief":                      │            │
│  │    → Create new job posting                         │            │
│  │                                                      │            │
│  │  IF subcategory = "feedback":                       │            │
│  │    → Update candidate status                        │            │
│  │    → Notify recruitment consultant                  │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────┐            │
│  │  🔗 SUPPLIER Emails                                  │            │
│  │  ─────────────────────────────────────────────      │            │
│  │  → Integration Hub (8093)                           │            │
│  │                                                      │            │
│  │  IF from bullhorn.com:                              │            │
│  │    → Bullhorn Sync Service                          │            │
│  │                                                      │            │
│  │  IF from broadbean.com:                             │            │
│  │    → Broadbean Service                              │            │
│  │                                                      │            │
│  │  IF subcategory = "invoice":                        │            │
│  │    → Finance Service (8088)                         │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────┐            │
│  │  👥 STAFF Emails                                     │            │
│  │  ─────────────────────────────────────────────      │            │
│  │  → Internal Inbox                                   │            │
│  │  → User-specific routing                            │            │
│  │                                                      │            │
│  │  IF subcategory = "hr_matter":                      │            │
│  │    → HR Team                                        │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────┐            │
│  │  📂 OTHER Emails                                     │            │
│  │  ─────────────────────────────────────────────      │            │
│  │  → General Inbox                                    │            │
│  │  → Archive (if spam)                                │            │
│  └─────────────────────────────────────────────────────┘            │
│                                                                       │
│  ┌─────────────────────────────────────────────────────┐            │
│  │  🔴 URGENT/HIGH Priority Handling                    │            │
│  │  ─────────────────────────────────────────────      │            │
│  │  IF priority = "urgent" OR "high":                  │            │
│  │    → Send real-time notification                    │            │
│  │    → Slack/SMS/Push notification                    │            │
│  │    → Add to priority queue                          │            │
│  └─────────────────────────────────────────────────────┘            │
└───────────────────────┬──────────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  TARGET MICROSERVICES                                 │
│                                                                       │
│  Process email according to category:                                │
│                                                                       │
│  • Parse CVs and create candidate profiles                           │
│  • Create job postings from briefs                                   │
│  • Schedule interviews                                                │
│  • Update placement status                                            │
│  • Sync with Bullhorn/Broadbean                                      │
│  • Route to team members                                              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Classification Decision Tree

```
                        📧 New Email
                             │
                             ▼
                   ┌─────────────────┐
                   │ From Domain?    │
                   └─────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
  @proactivepeople     @bullhorn.com      Other domains
        │                    │                    │
        ▼                    ▼                    │
    🟦 STAFF            🟨 SUPPLIER               │
                                                  ▼
                                        ┌─────────────────┐
                                        │ Has CV/Resume   │
                                        │ attachment?     │
                                        └─────────────────┘
                                                  │
                                        ┌─────────┴─────────┐
                                        ▼                   ▼
                                       YES                 NO
                                        │                   │
                                        ▼                   ▼
                                  🟩 CANDIDATE    ┌─────────────────┐
                                                  │ Content         │
                                                  │ Analysis (AI)   │
                                                  └─────────────────┘
                                                          │
                            ┌─────────────────────────────┼─────────────────┐
                            │                             │                 │
                            ▼                             ▼                 ▼
                    "job brief"                  "feedback"           "invoice"
                    "vacancy"                    "interview"          "payment"
                    "hiring need"                "placement"          "newsletter"
                            │                             │                 │
                            ▼                             ▼                 ▼
                      🟦 CLIENT                    🟦 CLIENT          🟨 SUPPLIER
                                                   or 🟩 CANDIDATE    or 🟪 OTHER
```

---

## Priority Detection Flow

```
                        📧 Email Received
                             │
                             ▼
                   ┌─────────────────────┐
                   │ Check Subject Line  │
                   └─────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
Contains "URGENT"     Contains "ASAP"     Contains "Important"
"Emergency"           "Critical"          "Priority"
        │                    │                    │
        ▼                    ▼                    ▼
    🔴 URGENT            🔴 URGENT            🟠 HIGH
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │ Send Immediate      │
                   │ Notification        │
                   │ • Slack             │
                   │ • SMS               │
                   │ • Push              │
                   └─────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │ Priority Queue      │
                   │ Position = 1        │
                   └─────────────────────┘
```

---

## Confidence-Based Routing

```
                    📊 Classification Result
                             │
                             ▼
                   ┌─────────────────────┐
                   │ Check Confidence    │
                   │ Score               │
                   └─────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
  Confidence >= 0.9    Confidence 0.6-0.9   Confidence < 0.6
        │                    │                    │
        ▼                    ▼                    ▼
    ✅ AUTO             ✅ AUTO              ⚠️ MANUAL
    PROCESS             PROCESS              REVIEW
        │                    │                    │
        │                    │                    ▼
        │                    │          ┌─────────────────┐
        │                    │          │ Add to Review   │
        │                    │          │ Queue           │
        │                    │          └─────────────────┘
        │                    │                    │
        └────────────────────┴────────────────────┘
                             │
                             ▼
                   ┌─────────────────────┐
                   │ Route to Services   │
                   └─────────────────────┘
```

---

## Manual Review Workflow

```
                ⚠️ Low Confidence Email
                        │
                        ▼
            ┌───────────────────────┐
            │ Email Review Queue     │
            │ Sorted by confidence   │
            │ (lowest first)         │
            └───────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ Reviewer Dashboard     │
            │ • View email content   │
            │ • See AI suggestion    │
            │ • View confidence      │
            └───────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ Manual Classification  │
            │ • Select category      │
            │ • Set priority         │
            │ • Add notes            │
            └───────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ Update Database        │
            │ • classifiedBy=manual  │
            │ • confidence=1.0       │
            │ • reviewed=true        │
            └───────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │ Re-route Email         │
            │ (if category changed)  │
            └───────────────────────┘
```

---

## Data Flow Summary

```
┌─────────────┐  Webhook   ┌──────────────┐  Queue    ┌────────────┐
│   SendGrid  │ ────────>  │  Ingestion   │ ───────>  │ Classifier │
│   AWS SES   │            │   Service    │           │  (Python)  │
└─────────────┘            └──────────────┘           └────────────┘
                                   │                          │
                                   │ Store                    │ Classify
                                   ▼                          ▼
                           ┌──────────────┐          ┌────────────┐
                           │  PostgreSQL  │ <─────── │   GROQ AI  │
                           │   Database   │  Result  │   API      │
                           └──────────────┘          └────────────┘
                                   │
                                   │ Read
                                   ▼
                           ┌──────────────┐
                           │    Router    │
                           │   Service    │
                           └──────────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
         ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
         │  Candidate  │  │   Client    │  │ Integration │
         │  Service    │  │  Service    │  │    Hub      │
         └─────────────┘  └─────────────┘  └─────────────┘
```

---

## Performance Metrics

```
┌──────────────────────────────────────────────────────┐
│                   Email Received                      │
│                   (Time = 0ms)                        │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼ (~50ms)
┌──────────────────────────────────────────────────────┐
│              Webhook Processing & Storage             │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼ (~20ms)
┌──────────────────────────────────────────────────────┐
│                  Queue Message                        │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼ (~50ms)
┌──────────────────────────────────────────────────────┐
│              Rule-Based Classification                │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼ (~300ms)
┌──────────────────────────────────────────────────────┐
│           AI Classification (GROQ API)                │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼ (~30ms)
┌──────────────────────────────────────────────────────┐
│          Store Classification & Route                 │
└───────────────────────┬──────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────┐
│           TOTAL TIME: ~450ms (p50)                    │
│                      ~800ms (p95)                     │
└──────────────────────────────────────────────────────┘
```

---

**Legend:**
- 🟩 CANDIDATE (Green)
- 🟦 CLIENT (Blue)
- 🟨 SUPPLIER (Yellow)
- 🟥 STAFF (Red)
- 🟪 OTHER (Purple)
- 🔴 URGENT
- 🟠 HIGH
- 🟢 NORMAL
- ⚪ LOW
