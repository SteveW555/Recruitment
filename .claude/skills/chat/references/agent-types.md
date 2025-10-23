# Agent Types Reference

## Overview

The system includes 7 specialized agents, each handling specific query types. All agents inherit from `BaseAgent` abstract class and must implement the `process(request: AgentRequest) -> AgentResponse` method.

## Base Agent Contract

All agents must respect:
- **Timeout:** 2 seconds maximum execution time
- **Request:** AgentRequest object with query, user_id, session_id, context, metadata
- **Response:** AgentResponse object with success, content, metadata, error
- **Error Handling:** No exceptions raised to caller; all errors handled gracefully

### AgentRequest
```python
@dataclass
class AgentRequest:
    query: str                                  # Max 1000 words
    user_id: str                                # User ID
    session_id: str                             # Session UUID
    context: Optional[Dict] = None              # Session context
    metadata: Dict[str, Any] = {}               # Request metadata
    staff_role: Optional[str] = None            # For specializations
    specialisation_context: Optional[Dict] = None
```

### AgentResponse
```python
@dataclass
class AgentResponse:
    success: bool                               # Execution success
    content: str                                # Response text (required if success=True)
    metadata: Dict[str, Any] = {}               # Response metadata
    error: Optional[str] = None                 # Error message (required if success=False)
    staff_role_context: Optional[str] = None
```

**Contract Requirements:**
- `success=True` requires non-empty content
- `success=False` requires error message
- Must include `agent_latency_ms` in metadata
- Should include `sources` list if citing external data
- May include `tokens_used` for cost tracking

---

## Agent 1: GENERAL_CHAT (Priority: P3)

**File:** `/utils/ai_router/agents/general_chat_agent.py`

### Purpose
Friendly fallback for casual conversation and off-topic queries. Also serves as primary fallback when other agents fail.

### Configuration
- **LLM Provider:** Groq
- **Model:** llama-3-70b-8192
- **Temperature:** 0.7 (friendly, conversational)
- **Max Tokens:** 1000
- **Tools:** None

### When to Use
- User greetings (hello, hi, good morning, how are you)
- Casual social questions (what's up, how are you, etc.)
- Off-topic queries not matching other categories
- Failed agent fallback (when other agents timeout/fail)
- Joke requests or friendly banter

### Example Queries
- "Hello", "Hi there", "Good morning"
- "How are you?", "What's up?", "Tell me a joke"
- "What's the weather like?", "What time is it?"

### Characteristics
- Brief, conversational responses (50-200 words)
- Friendly, warm tone
- Does NOT attempt business logic
- Acknowledges limitations appropriately

---

## Agent 2: INFORMATION_RETRIEVAL (Priority: P1 - MVP)

**File:** `/utils/ai_router/agents/information_retrieval_agent.py`

### Purpose
Search and retrieve data from internal databases, external sources, and web. Aggregates information with source attribution.

### Configuration
- **LLM Provider:** Groq
- **Model:** llama-3-70b-8192
- **Temperature:** 0.3 (factual, structured)
- **Max Tokens:** 2000
- **Tools:** web_search, database_query, multi_source_aggregation

### When to Use
- Finding candidates by skills, experience, location
- Searching for job postings
- Looking up placement data
- Researching market salaries and trends
- Retrieving candidate profiles
- Searching job boards

### Example Queries
- "Find candidates with 5+ years sales experience in London"
- "Show me John Smith's candidate profile"
- "List all active jobs in Bristol"
- "What are the average salaries for software engineers?"
- "What are current hiring trends in fintech?"
- "Search for all placements in Q4 2024"

### Response Format
- Aggregated results from multiple sources
- Each result includes: data, source, confidence
- Summary statistics when applicable
- Next steps for user action

### Implementation Details
- Simulates searching 3 source types: database, web, industry
- Returns aggregated results with source attribution
- Fallback aggregation if LLM API fails
- Handles no-results gracefully

---

## Agent 3: PROBLEM_SOLVING (Priority: P2)

**File:** `/utils/ai_router/agents/problem_solving_agent.py`

### Purpose
Complex business analysis and multi-step problem solving with evidence-based recommendations.

### Configuration
- **LLM Provider:** Anthropic
- **Model:** claude-3-5-sonnet-20241022
- **Temperature:** 0.5 (balanced reasoning)
- **Max Tokens:** 2000
- **Tools:** industry_research, data_analysis, benchmarking

### When to Use
- Analyzing business problems and challenges
- Identifying root causes
- Benchmarking against industry standards
- Developing strategic recommendations
- Multi-step problem decomposition
- Performance improvement analysis

### Example Queries
- "How can we reduce candidate dropout rate by 20%?"
- "Why is our placement rate 15% lower than industry average?"
- "What strategies improve time-to-hire for technical roles?"
- "How do we scale without compromising quality?"
- "Analyze our fee recovery challenges"

### Response Format
- **6-Step Analysis Framework:**
  1. Problem Statement Clarification
  2. Root Cause Identification (with probability ranking)
  3. Industry Benchmark Cross-Reference (6 categories)
  4. Evidence-Based Recommendations (3-5 items)
  5. Implementation Roadmap (phases + timeline)
  6. Success Metrics & Monitoring

### Implementation Details
- Uses Claude 3.5 Sonnet for superior reasoning
- 2-second timeout with graceful fallback
- Confidence scoring based on analysis quality
- 6 benchmark categories: placement rate, time-to-hire, dropout, satisfaction, fees, salary
- Comprehensive error handling

---

## Agent 4: REPORT_GENERATION (Priority: P3)

**File:** `/utils/ai_router/agents/report_generation_agent.py`

### Purpose
Create professional reports and visualizations with markdown formatting and visual recommendations.

### Configuration
- **LLM Provider:** Groq
- **Model:** llama-3-70b-8192
- **Temperature:** 0.3 (professional, structured)
- **Max Tokens:** 2000
- **Tools:** data_visualization, report_formatting, chart_suggestions

### When to Use
- Creating quarterly performance reports
- Generating executive dashboards
- Building market analysis reports
- Producing candidate pipeline reports
- Placement trends analysis
- Presentation-ready outputs

### Example Queries
- "Create a quarterly performance report"
- "Generate a dashboard showing top 10 clients"
- "Build a market analysis report for tech sector"
- "Generate placement trends and pipeline report"
- "Create financial performance summary"

### Response Format
- **8-Section Report Structure:**
  1. Title & Executive Summary
  2. Key Metrics Dashboard (3-5 KPIs)
  3. Detailed Findings (2-3 sections)
  4. Visualization Suggestions (with chart types)
  5. Data Tables (Markdown formatted)
  6. Key Insights (5-7 bullet points)
  7. Recommendations (3-5 actionable items with impact)
  8. Conclusion & Next Steps

### Implementation Details
- Professional markdown formatting
- 6 visualization pattern types: trends, comparison, composition, distribution, relationships, proportions
- 5 built-in report templates: Quarterly Performance, Division Performance, Market Analysis, Candidate Pipeline, Executive Summary
- 85% presentation-ready target (SC-005 spec)
- ~950-1100 words typical length

---

## Agent 5: AUTOMATION (Priority: P2)

**File:** `/utils/ai_router/agents/automation_agent.py`

### Purpose
Design and specify workflow automation pipelines for business processes.

### Configuration
- **LLM Provider:** Groq
- **Model:** llama-3-70b-8192
- **Temperature:** 0.3 (structured, precise)
- **Max Tokens:** 2000
- **Tools:** workflow_builder, platform_specification

### When to Use
- Designing automated workflows
- Creating trigger-action specifications
- Planning workflow implementation
- Evaluating process automation opportunities
- Scheduling automation setup
- Integration planning

### Example Queries
- "Auto-send welcome email when candidates register"
- "Notify hiring managers when candidates apply for their jobs"
- "Create workflow for interview reminders"
- "Build automated candidate nurturing sequence"
- "Design placement follow-up automation"

### Response Format
- **Workflow Specification Structure:**
  - Workflow Name & Objective
  - Triggers (events that start workflow)
  - Actions (steps to execute)
  - Conditions & Decision Points
  - Recommended Platform (n8n, Zapier, Make, IFTTT, etc.)
  - Integration Points (system-to-system data)
  - Error Handling & Failure Scenarios
  - Success Metrics & Time Savings
  - Implementation Complexity Score
  - Quick Implementation Check

### Implementation Details
- Supports 7 automation platforms: n8n, Zapier, Make, IFTTT, Integromat, PagerDuty, Slack
- 5 built-in workflow templates
- Implementability scoring (target: 70%+)
- ~1000 words typical length
- Platform-agnostic specifications

---

## Agent 6: INDUSTRY_KNOWLEDGE (Priority: P1 - MVP)

**File:** `/utils/ai_router/agents/industry_knowledge_agent.py`

### Purpose
UK-specific recruitment domain expertise with validated source citations.

### Configuration
- **LLM Provider:** Groq
- **Model:** llama-3-70b-8192
- **Temperature:** 0.2 (factual, precise)
- **Max Tokens:** 1500
- **Tools:** sources_md_lookup, compliance_checker

### When to Use
- GDPR compliance questions
- IR35 off-payroll working regulations
- Right-to-work verification procedures
- Employment law and contract questions
- Diversity and inclusion best practices
- Recruitment process standards
- Salary benchmarks and trends
- UK-specific regulations

### Example Queries
- "What is typical notice period for UK financial services?"
- "What are GDPR requirements for storing candidate CVs?"
- "What are IR35 compliance requirements?"
- "How do we comply with right-to-work regulations?"
- "What diversity and inclusion best practices apply?"

### Response Format
- Domain-specific guidance
- Validated source citations (from sources_validated_summaries.md)
- UK-focus (not general)
- Actionable recommendations
- Compliance-aware

### Implementation Details
- 9 major knowledge domains:
  1. GDPR compliance and data protection
  2. IR35 off-payroll working regulations
  3. Right-to-work verification
  4. Employment law and contracts
  5. Diversity and inclusion best practices
  6. Recruitment process standards
  7. Salary benchmarks and trends
  8. Contractual obligations
  9. Worker classification
- Loads validated sources from sources_validated_summaries.md
- Built-in defaults (9 domains) if sources file unavailable
- Low temperature (0.2) for factual accuracy
- Source citation in all responses

---

## Agent 7: DATA_OPERATIONS (Priority: P1 - MVP)

**File:** `/utils/ai_router/agents/data_operations_agent.py`

### Purpose
Create, Update, Delete, and Schedule data operations and administrative tasks.

### Configuration
- **LLM Provider:** Groq
- **Model:** llama-3-70b-8192
- **Temperature:** 0.3 (structured, precise)
- **Max Tokens:** 1500
- **Tools:** crud_operations, calendar_api, email_api, document_generation

### When to Use
- Creating records (invoices, placements, jobs, etc.)
- Updating existing records
- Deleting or archiving data
- Scheduling interviews or meetings
- Sending communications
- Generating documents
- Administrative operations

### Example Queries
- "Create an invoice for placement ID 12345"
- "Update client ABC Corp's status to active"
- "Schedule an interview with Jane Doe for Tuesday"
- "Mark candidate as hired for job REF-2024-001"
- "Send timesheet to client XYZ Ltd"
- "Generate offer letter for John Smith"

### Response Format
- Operation confirmation (success/failure)
- Record IDs and details affected
- Confirmation details for user verification
- Any errors or warnings
- Next steps

### Implementation Details
- Validates operations before execution
- Requires confirmation for destructive operations
- Logs all operations for audit trail
- Handles conflicts and duplicates gracefully
- Email/calendar integration ready

---

## Agent Configuration (agents.json)

Each agent is configured in `/config/agents.json` with:

```json
{
  "AGENT_NAME": {
    "name": "Display name",
    "priority": 1,
    "description": "What this agent does",
    "agent_class": "module.path:ClassName",
    "llm_provider": "groq|anthropic",
    "llm_model": "model-id",
    "timeout_seconds": 2,
    "retry_count": 1,
    "retry_delay_ms": 500,
    "tools": ["tool1", "tool2"],
    "resources": {"key": "value"},
    "system_prompt": "Agent instructions...",
    "enabled": true,
    "example_queries": [
      "Example query 1",
      "Example query 2"
    ]
  }
}
```

## Agent Selection Criteria

Agents are selected based on query classification:

1. **Confidence >= 0.7:** Route to primary agent
2. **Confidence 0.5-0.7:** Consider secondary agent or clarify
3. **Confidence < 0.5:** Route to General Chat with clarification

The system prioritizes:
- Query semantic similarity to examples
- Confidence threshold enforcement
- Fallback to General Chat on uncertainty
- Timeout protection (2s max)
- Error logging and recovery

## Extending the System

To add a new agent:

1. Create agent class in `/utils/ai_router/agents/[name]_agent.py`
2. Inherit from `BaseAgent`
3. Implement `process(request: AgentRequest) -> AgentResponse`
4. Implement `get_category() -> Category`
5. Add to `config/agents.json` with configuration
6. Provide 5-10 example queries for semantic classification
7. Create system prompt at `/backend-api/prompts/agent-system-prompts/[name].txt`
