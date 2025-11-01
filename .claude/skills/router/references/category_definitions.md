# Category Definitions Reference

Complete reference guide for the AI Router's 7-category classification system.

## Category Overview

| Category | Priority | Description | Typical Response Time |
|----------|----------|-------------|----------------------|
| INFORMATION_RETRIEVAL | P1 | External information lookup | 500-2000ms |
| DATA_OPERATIONS | P1 | Internal system operations | 200-1000ms |
| PROBLEM_SOLVING | P2 | Complex analysis & recommendations | 1000-5000ms |
| REPORT_GENERATION | P3 | Structured reports & visualizations | 800-3000ms |
| AUTOMATION | P2 | Workflow pipeline design | 600-2500ms |
| INDUSTRY_KNOWLEDGE | P1 | UK recruitment domain expertise | 400-2000ms |
| GENERAL_CHAT | P3 | Casual conversation & fallback | 100-800ms |

---

## 1. INFORMATION_RETRIEVAL

### Description
External information retrieval from multiple data sources including databases, web searches, and industry resources.

### Key Characteristics
- Focuses on **finding and aggregating data** from external sources
- Returns information **with source attribution**
- May query job boards, salary databases, market research
- **Does NOT modify system data** (that's DATA_OPERATIONS)

### Example Queries

**Strong matches (confidence 0.85-0.95):**
- "What are current salary ranges for senior Java developers in London?"
- "Find me all active job postings for accountants on Totaljobs"
- "What's the market demand for cloud architects in the UK?"
- "Show me the top 10 job boards for tech recruitment"
- "What are typical interview questions for sales roles?"
- "How many candidates are available for React developer positions?"

**Medium matches (confidence 0.65-0.84):**
- "salary info for developers" (needs specificity)
- "find candidates" (unclear: external search or internal database?)
- "job market trends" (unclear: general knowledge or specific data?)

**Weak matches (confidence <0.65):**
- "get data" (too vague)
- "information" (no context)
- "search" (unclear what to search)

### Decision Tree

```
Is the query asking to FIND information from EXTERNAL sources?
├─ YES: Does it specify what to find?
│  ├─ YES: Does it involve recruitment data (salaries, candidates, jobs)?
│  │  ├─ YES → INFORMATION_RETRIEVAL (confidence: 0.85-0.95)
│  │  └─ NO: Is it general knowledge or industry expertise?
│  │     ├─ General → INDUSTRY_KNOWLEDGE
│  │     └─ Specific data → INFORMATION_RETRIEVAL (confidence: 0.70-0.80)
│  └─ NO → GENERAL_CHAT (too vague, confidence: <0.65)
└─ NO: Is it asking to modify/create/delete data?
   ├─ YES → DATA_OPERATIONS
   └─ NO → Check other categories
```

### Common Confusions

**INFORMATION_RETRIEVAL vs DATA_OPERATIONS:**
- INFORMATION_RETRIEVAL: "Find candidates with Python skills" (external search)
- DATA_OPERATIONS: "Update candidate status to 'Interviewed'" (internal modification)

**INFORMATION_RETRIEVAL vs INDUSTRY_KNOWLEDGE:**
- INFORMATION_RETRIEVAL: "What are current salaries for accountants?" (specific data lookup)
- INDUSTRY_KNOWLEDGE: "What are best practices for accountant recruitment?" (expertise/guidance)

---

## 2. DATA_OPERATIONS

### Description
Internal system operations involving CRUD (Create, Read, Update, Delete) operations on the recruitment database.

### Key Characteristics
- **Modifies or queries INTERNAL system data**
- Performs database operations (INSERT, UPDATE, DELETE, SELECT)
- Works with candidates, jobs, clients, placements in the system
- Returns structured data from the internal database

### Example Queries

**Strong matches (confidence 0.85-0.95):**
- "Add a new candidate to the database: John Smith, Java Developer"
- "Update the status of job #12345 to 'Closed'"
- "Delete all candidates who haven't responded in 6 months"
- "List all active placements for client 'Acme Corp'"
- "Show me candidates in the 'Interview' stage for the Frontend Developer role"
- "Create a new job posting for Senior Sales Manager"

**Medium matches (confidence 0.65-0.84):**
- "get candidates" (unclear: internal DB or external search?)
- "show jobs" (needs specificity: all jobs? active jobs?)
- "update data" (too vague: what data?)

**Weak matches (confidence <0.65):**
- "data" (no context)
- "database" (no action specified)
- "system" (too generic)

### Decision Tree

```
Is the query asking to CREATE, READ, UPDATE, or DELETE data?
├─ YES: Is it INTERNAL system data (candidates, jobs, clients, placements)?
│  ├─ YES: Is the operation clearly specified?
│  │  ├─ YES → DATA_OPERATIONS (confidence: 0.85-0.95)
│  │  └─ NO → DATA_OPERATIONS (confidence: 0.65-0.75)
│  └─ NO: Is it external data lookup?
│     └─ YES → INFORMATION_RETRIEVAL
└─ NO → Check other categories
```

### Common Confusions

**DATA_OPERATIONS vs INFORMATION_RETRIEVAL:**
- DATA_OPERATIONS: "Show me all candidates in our database" (internal query)
- INFORMATION_RETRIEVAL: "Find candidates for Python roles on LinkedIn" (external search)

**DATA_OPERATIONS vs REPORT_GENERATION:**
- DATA_OPERATIONS: "List all placements this month" (raw data list)
- REPORT_GENERATION: "Generate a report of this month's placements with charts" (structured report)

---

## 3. PROBLEM_SOLVING

### Description
Complex business analysis with multi-step problem decomposition, root cause identification, and evidence-based recommendations.

### Key Characteristics
- Requires **multi-step analytical reasoning**
- Identifies **root causes** and contributing factors
- Provides **strategic recommendations** with impact assessment
- Often involves "why" questions or complex "how" questions
- Uses Claude 3.5 Sonnet for superior reasoning

### Example Queries

**Strong matches (confidence 0.85-0.95):**
- "Why did our placement rate drop 15% this quarter? Analyze and recommend solutions"
- "How can we reduce time-to-hire from 45 to 30 days?"
- "Our client satisfaction scores are declining. What's causing this and what should we do?"
- "Analyze why tech candidates are dropping out at the interview stage"
- "We're losing candidates to competitors. How do we improve our offer acceptance rate?"
- "What's the root cause of our poor candidate-to-placement conversion in accountancy?"

**Medium matches (confidence 0.65-0.84):**
- "How to improve recruitment?" (needs specificity: what aspect?)
- "Why are we losing candidates?" (good intent, but needs more context)
- "Help with performance issues" (unclear: what issues?)

**Weak matches (confidence <0.65):**
- "improve things" (too vague)
- "fix problem" (no problem specified)
- "help" (no context)

### Decision Tree

```
Is the query asking to ANALYZE a complex problem?
├─ YES: Does it request root cause analysis or strategic recommendations?
│  ├─ YES: Is the problem business-related (recruitment, performance, strategy)?
│  │  ├─ YES → PROBLEM_SOLVING (confidence: 0.85-0.95)
│  │  └─ NO: Is it a technical system issue?
│  │     └─ YES → DATA_OPERATIONS (if it's a system bug/issue)
│  └─ NO: Does it ask "why" or "how to improve"?
│     ├─ YES → PROBLEM_SOLVING (confidence: 0.70-0.80)
│     └─ NO → Check other categories
└─ NO → Check other categories
```

### Common Confusions

**PROBLEM_SOLVING vs INFORMATION_RETRIEVAL:**
- PROBLEM_SOLVING: "Why are we losing tech candidates? Analyze and recommend solutions" (analysis)
- INFORMATION_RETRIEVAL: "What are typical reasons candidates decline offers?" (data lookup)

**PROBLEM_SOLVING vs AUTOMATION:**
- PROBLEM_SOLVING: "How can we reduce manual data entry errors?" (strategic analysis)
- AUTOMATION: "Design a workflow to automate data entry from email applications" (specific workflow)

---

## 4. REPORT_GENERATION

### Description
Structured report creation with executive summaries, visualizations, insights, and recommendations formatted for presentation.

### Key Characteristics
- Produces **structured reports** with multiple sections
- Includes **visualization suggestions** (charts, graphs, dashboards)
- Contains executive summary, key metrics, insights, recommendations
- **Presentation-ready** (85% ready without modification)
- Uses Groq llama-3-70b-8192 for fast generation

### Example Queries

**Strong matches (confidence 0.85-0.95):**
- "Generate a quarterly performance report with placement metrics and trend charts"
- "Create a dashboard showing this month's KPIs: placements, revenue, candidate pipeline"
- "Produce a report analyzing Q4 recruitment performance across all divisions"
- "Generate an executive summary of our 2024 recruitment metrics"
- "Create a visual report showing salary trends for tech roles over the past year"
- "Build a report comparing our performance vs industry benchmarks"

**Medium matches (confidence 0.65-0.84):**
- "make a report" (needs specificity: report about what?)
- "show me charts" (unclear: charts of what data?)
- "performance metrics" (is this a raw data request or a report?)

**Weak matches (confidence <0.65):**
- "report" (no context)
- "data visualization" (no subject specified)
- "dashboard" (what should the dashboard show?)

### Decision Tree

```
Is the query asking to GENERATE a report or visualization?
├─ YES: Does it specify what the report should contain?
│  ├─ YES: Does it mention presentation/visualization/charts?
│  │  ├─ YES → REPORT_GENERATION (confidence: 0.85-0.95)
│  │  └─ NO: Is it asking for structured insights?
│  │     ├─ YES → REPORT_GENERATION (confidence: 0.75-0.85)
│  │     └─ NO → DATA_OPERATIONS (raw data query)
│  └─ NO: Does it say "report" or "dashboard"?
│     ├─ YES → REPORT_GENERATION (confidence: 0.60-0.70, may need clarification)
│     └─ NO → Check other categories
└─ NO → Check other categories
```

### Common Confusions

**REPORT_GENERATION vs DATA_OPERATIONS:**
- REPORT_GENERATION: "Generate a monthly placement report with visualizations" (structured report)
- DATA_OPERATIONS: "List all placements this month" (raw data)

**REPORT_GENERATION vs PROBLEM_SOLVING:**
- REPORT_GENERATION: "Create a report showing our placement trends" (descriptive reporting)
- PROBLEM_SOLVING: "Analyze why our placements are declining and recommend solutions" (analytical reasoning)

---

## 5. AUTOMATION

### Description
Workflow pipeline design and specification for automation platforms like n8n, Zapier, Make, and IFTTT.

### Key Characteristics
- Designs **workflow specifications** with triggers, actions, conditions
- Identifies **integration points** between systems
- Provides **implementability scoring** (70%+ target)
- Supports multiple automation platforms
- Uses Groq llama-3-70b-8192 for fast workflow design

### Example Queries

**Strong matches (confidence 0.85-0.95):**
- "Design a workflow to automatically post jobs to Indeed when they're approved in our system"
- "Create an n8n workflow for candidate onboarding: send welcome email, schedule orientation, create accounts"
- "Automate our interview scheduling: check calendar availability, send invites, add to CRM"
- "Build a Zapier workflow to sync new Bullhorn candidates to our database every hour"
- "Design an automation to send weekly pipeline reports to recruiters every Friday"
- "Create a workflow to notify managers when candidates move to 'Offer' stage"

**Medium matches (confidence 0.65-0.84):**
- "automate candidate onboarding" (good intent, needs workflow specification)
- "how to automate job posting?" (question format, but automation intent clear)
- "workflow for interviews" (needs automation action verbs)

**Weak matches (confidence <0.65):**
- "automate" (no process specified)
- "workflow" (no context)
- "integration" (too vague)

### Decision Tree

```
Is the query asking to DESIGN or CREATE a workflow/automation?
├─ YES: Does it specify the process to automate?
│  ├─ YES: Does it mention triggers/actions or automation platforms?
│  │  ├─ YES → AUTOMATION (confidence: 0.85-0.95)
│  │  └─ NO: Is the automation intent clear?
│  │     ├─ YES → AUTOMATION (confidence: 0.75-0.85)
│  │     └─ NO → AUTOMATION (confidence: 0.65-0.75, may need clarification)
│  └─ NO: Does it say "automate" or "workflow"?
│     ├─ YES → AUTOMATION (confidence: 0.60-0.70, needs clarification)
│     └─ NO → Check other categories
└─ NO: Is it asking HOW to do something (procedural)?
   ├─ YES → PROBLEM_SOLVING (strategic) or INDUSTRY_KNOWLEDGE (best practices)
   └─ NO → Check other categories
```

### Common Confusions

**AUTOMATION vs PROBLEM_SOLVING:**
- AUTOMATION: "Design a workflow to automate candidate screening" (specific workflow)
- PROBLEM_SOLVING: "How can we make candidate screening more efficient?" (strategic analysis)

**AUTOMATION vs DATA_OPERATIONS:**
- AUTOMATION: "Automate syncing Bullhorn data to our database" (workflow design)
- DATA_OPERATIONS: "Sync Bullhorn data to our database now" (immediate operation)

---

## 6. INDUSTRY_KNOWLEDGE

### Description
UK recruitment domain expertise covering regulations, compliance, best practices, and industry standards.

### Key Characteristics
- Provides **regulatory compliance** information (GDPR, IR35, right-to-work)
- Covers **best practices** and industry standards
- UK-specific recruitment knowledge
- Cites **validated sources** from industry documentation
- Uses low temperature (0.2) for factual accuracy

### Example Queries

**Strong matches (confidence 0.85-0.95):**
- "What are the GDPR requirements for storing candidate data in the UK?"
- "Explain IR35 off-payroll working regulations for contractor placements"
- "What are the right-to-work verification steps for EU nationals post-Brexit?"
- "What's best practice for diversity and inclusion in recruitment?"
- "What employment law considerations apply to temporary placements?"
- "How should we handle salary benchmarking to stay compliant?"

**Medium matches (confidence 0.65-0.84):**
- "GDPR rules" (needs context: for what aspect?)
- "compliance requirements" (needs specificity: which regulations?)
- "best practices" (for what process?)

**Weak matches (confidence <0.65):**
- "regulations" (no domain specified)
- "legal stuff" (too vague)
- "compliance" (no context)

### Decision Tree

```
Is the query asking about UK recruitment REGULATIONS, COMPLIANCE, or BEST PRACTICES?
├─ YES: Does it mention specific regulations (GDPR, IR35, right-to-work, employment law)?
│  ├─ YES → INDUSTRY_KNOWLEDGE (confidence: 0.85-0.95)
│  └─ NO: Does it ask about recruitment best practices or industry standards?
│     ├─ YES → INDUSTRY_KNOWLEDGE (confidence: 0.75-0.85)
│     └─ NO → INDUSTRY_KNOWLEDGE (confidence: 0.65-0.75, may need clarification)
└─ NO: Is it asking "how to" do a recruitment task?
   ├─ YES: Is it asking for best practices?
   │  ├─ YES → INDUSTRY_KNOWLEDGE
   │  └─ NO → PROBLEM_SOLVING (strategic how-to)
   └─ NO → Check other categories
```

### Knowledge Domains

The Industry Knowledge Agent covers 9 major domains:

1. **GDPR compliance and data protection**
2. **IR35 off-payroll working regulations**
3. **Right-to-work verification**
4. **Employment law and contracts**
5. **Diversity and inclusion best practices**
6. **Recruitment process standards**
7. **Salary benchmarks and trends** (regulatory/compliance aspects)
8. **Industry certifications and standards**
9. **Ethical recruitment practices**

### Common Confusions

**INDUSTRY_KNOWLEDGE vs INFORMATION_RETRIEVAL:**
- INDUSTRY_KNOWLEDGE: "What are best practices for GDPR-compliant candidate storage?" (expertise)
- INFORMATION_RETRIEVAL: "Find me all GDPR regulations for recruitment" (data lookup)

**INDUSTRY_KNOWLEDGE vs PROBLEM_SOLVING:**
- INDUSTRY_KNOWLEDGE: "What's the standard notice period for permanent placements?" (domain knowledge)
- PROBLEM_SOLVING: "How should we restructure our notice period policy to reduce dropout?" (strategic analysis)

---

## 7. GENERAL_CHAT

### Description
Casual conversation, greetings, off-topic queries, and fallback for ambiguous/unclear queries.

### Key Characteristics
- Handles **greetings** (hello, hi, good morning)
- Responds to **social queries** (how are you, what's up)
- Manages **off-topic** questions without dismissal
- Serves as **fallback** when confidence < threshold
- Uses temperature 0.7 for friendly, conversational tone

### Example Queries

**Strong matches (confidence 0.85-0.95):**
- "Hello!"
- "Good morning, how are you?"
- "What's the weather like today?"
- "Tell me a joke"
- "Can you sing?"
- "What's your name?"

**Medium matches (confidence 0.65-0.84):**
- "Hi there" (clear greeting but minimal)
- "How's it going?" (social query)
- "Thanks!" (acknowledgment)

**Weak matches (confidence <0.65):**
- Any query that's too vague to classify → Routes to GENERAL_CHAT as fallback
- Any query where the LLM returns confidence <0.65 → Fallback to GENERAL_CHAT

### Decision Tree

```
Is the query a greeting or casual conversation?
├─ YES → GENERAL_CHAT (confidence: 0.85-0.95)
└─ NO: Is it off-topic (not related to recruitment/business)?
   ├─ YES → GENERAL_CHAT (confidence: 0.75-0.85)
   └─ NO: Is the query unclear or too vague to classify?
      ├─ YES → GENERAL_CHAT (confidence: <0.65, FALLBACK)
      └─ NO → Check other categories
```

### Fallback Behavior

GENERAL_CHAT also serves as the **fallback category** when:

1. **Classification confidence < threshold** (default: 0.65)
2. **Groq API fails** or returns invalid response
3. **Query is genuinely ambiguous** with no clear category
4. **Another agent fails** to process the query

In fallback mode, the agent:
- Acknowledges the user's query
- Provides a brief, friendly response
- May suggest rephrasing for better routing
- Offers to help in other ways

### Common Confusions

**GENERAL_CHAT vs INFORMATION_RETRIEVAL:**
- GENERAL_CHAT: "What's the weather today?" (off-topic, casual)
- INFORMATION_RETRIEVAL: "What are typical office hours for recruiters?" (recruitment info)

**GENERAL_CHAT (fallback) vs Legitimate Categories:**
- If the query is vague but has recruitment intent, improve query phrasing instead of accepting GENERAL_CHAT routing

---

## Multi-Category Queries

Some queries may seem to fit multiple categories. Here's how to prioritize:

### Example: "Find salaries for developers and create a report"

This query has two intents:
1. Find salaries (INFORMATION_RETRIEVAL)
2. Create a report (REPORT_GENERATION)

**Resolution:**
- **Primary category**: REPORT_GENERATION (the end goal)
- **Secondary action**: The report agent can call information retrieval internally
- **Confidence**: 0.80-0.90 (clear combined intent)

### Example: "Update candidate status and analyze why they're dropping out"

This query has two intents:
1. Update status (DATA_OPERATIONS)
2. Analyze dropout (PROBLEM_SOLVING)

**Resolution:**
- **Primary category**: PROBLEM_SOLVING (more complex, strategic)
- **Secondary action**: The problem-solving agent can trigger data operations as needed
- **Confidence**: 0.75-0.85 (clear but mixed intent)

### Prioritization Rule

When multiple categories apply:
1. Choose the **most complex/strategic** category (higher priority)
2. Let that agent **orchestrate** calls to other agents
3. Use **primary_category** for routing, note secondary intent in reasoning

Priority order (highest to lowest):
1. PROBLEM_SOLVING (most complex)
2. AUTOMATION (workflow design)
3. REPORT_GENERATION (structured output)
4. INFORMATION_RETRIEVAL / DATA_OPERATIONS (data handling, tied)
5. INDUSTRY_KNOWLEDGE (domain expertise)
6. GENERAL_CHAT (fallback)

---

## Confidence Score Calibration

### High Confidence (0.85-1.0)
- Query clearly matches category description
- Contains category-specific keywords
- Intent is unambiguous
- Matches example queries closely

**Example**: "What are the IR35 regulations?" → INDUSTRY_KNOWLEDGE (0.92)

### Medium Confidence (0.65-0.84)
- Query matches category but lacks specificity
- Could potentially fit 2 categories
- Intent is clear but phrasing is ambiguous
- Requires minor interpretation

**Example**: "Get me salary data" → INFORMATION_RETRIEVAL (0.72)

### Low Confidence (<0.65)
- Query is too vague to classify reliably
- Could fit multiple categories equally
- Lacks context or specificity
- **Triggers fallback to GENERAL_CHAT**

**Example**: "Help with data" → Confidence 0.45 → Routes to GENERAL_CHAT

### Confidence Threshold Tuning

Default threshold: **0.65**

- **Lower threshold (0.55-0.60)**: More aggressive routing, may misclassify
  - Use when: You prefer any routing over fallback
  - Risk: More misclassifications

- **Higher threshold (0.70-0.75)**: More conservative, more fallback
  - Use when: Accuracy is critical
  - Risk: More queries route to GENERAL_CHAT

---

## Category Examples by Industry Domain

### Sales Recruitment

| Query | Category | Confidence |
|-------|----------|-----------|
| "Find active sales job postings in Bristol" | INFORMATION_RETRIEVAL | 0.90 |
| "Update candidate John Doe's status to 'Offer Extended'" | DATA_OPERATIONS | 0.92 |
| "Why are sales candidates rejecting our offers?" | PROBLEM_SOLVING | 0.88 |
| "Generate Q4 sales placement report" | REPORT_GENERATION | 0.91 |
| "Automate follow-up emails to sales candidates" | AUTOMATION | 0.89 |
| "What's the typical commission structure for sales roles?" | INDUSTRY_KNOWLEDGE | 0.85 |

### Tech Recruitment

| Query | Category | Confidence |
|-------|----------|-----------|
| "What are current salaries for React developers?" | INFORMATION_RETRIEVAL | 0.93 |
| "Add new Java Developer job to system" | DATA_OPERATIONS | 0.94 |
| "How can we reduce time-to-hire for tech roles?" | PROBLEM_SOLVING | 0.87 |
| "Create dashboard of tech candidate pipeline" | REPORT_GENERATION | 0.90 |
| "Design workflow to auto-post tech jobs to Stack Overflow" | AUTOMATION | 0.92 |
| "What are best practices for tech stack assessment?" | INDUSTRY_KNOWLEDGE | 0.84 |

### Compliance

| Query | Category | Confidence |
|-------|----------|-----------|
| "Find GDPR compliance checklists" | INFORMATION_RETRIEVAL | 0.80 |
| "Update candidate consent status in database" | DATA_OPERATIONS | 0.91 |
| "Analyze why we're getting GDPR complaints" | PROBLEM_SOLVING | 0.86 |
| "Generate compliance audit report" | REPORT_GENERATION | 0.89 |
| "Automate GDPR consent request emails" | AUTOMATION | 0.88 |
| "What are the GDPR requirements for candidate data?" | INDUSTRY_KNOWLEDGE | 0.95 |

---

## Summary Decision Matrix

| If the query... | Route to... |
|-----------------|-------------|
| Asks to **find/lookup external data** | INFORMATION_RETRIEVAL |
| Asks to **create/read/update/delete internal data** | DATA_OPERATIONS |
| Asks **why** or requests **analysis with recommendations** | PROBLEM_SOLVING |
| Asks to **generate report/dashboard/visualization** | REPORT_GENERATION |
| Asks to **design/create workflow/automation** | AUTOMATION |
| Asks about **UK regulations/compliance/best practices** | INDUSTRY_KNOWLEDGE |
| Is a **greeting**, **off-topic**, or **too vague** | GENERAL_CHAT |

---

**Version**: 1.0.0
**Last Updated**: 2025-01-01
