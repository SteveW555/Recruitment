# Data Model: Chat Routing AI

**Feature**: 002-chat-routing-ai
**Date**: 2025-10-22
**Purpose**: Define entity models, relationships, validation rules, and state transitions

## Entity Definitions

### 1. Query

**Purpose**: Represents a user input message requiring classification and routing

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Required, Primary Key | Unique identifier for the query |
| `text` | String | Required, Max 1000 words | User's question/request content |
| `user_id` | String | Required, Max 255 chars | Identifier of the user making the query |
| `session_id` | String | Required, UUID format | Session this query belongs to |
| `timestamp` | DateTime | Required, Auto-generated | When query was received (UTC) |
| `word_count` | Integer | Required, Computed | Number of words in query text |
| `truncated` | Boolean | Required, Default False | Whether query exceeded 1000 words |
| `context_messages` | List[Dict] | Optional | Previous messages from session for context |

**Validation Rules**:
- `text` cannot be empty or whitespace-only
- If `word_count` > 1000, `text` is truncated to first 1000 words and `truncated` set to True
- `user_id` must match authenticated user (enforced by caller)
- `session_id` must be valid UUID v4 format

**Relationships**:
- One-to-One with `RoutingDecision` (each query produces exactly one routing decision)
- Many-to-One with `SessionContext` (multiple queries belong to one session)

**Example**:
```python
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "text": "What are the top 5 job boards for sales positions in Bristol?",
    "user_id": "user_12345",
    "session_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "timestamp": "2025-10-22T10:30:00Z",
    "word_count": 11,
    "truncated": false,
    "context_messages": [
        {"role": "user", "content": "Hello", "category": "General Chat"}
    ]
}
```

---

### 2. Category

**Purpose**: Represents one of six classification types for routing

**Enum Values**:
- `INFORMATION_RETRIEVAL` - Simple multi-source data lookup
- `PROBLEM_SOLVING` - Complex analysis and recommendations
- `REPORT_GENERATION` - Visualization and presentation creation
- `AUTOMATION` - Workflow pipeline design
- `INDUSTRY_KNOWLEDGE` - UK recruitment domain expertise
- `GENERAL_CHAT` - Casual conversation

**Attributes (Configuration)**:

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Human-readable category name |
| `priority` | Integer | P1, P2, or P3 (1=highest) |
| `description` | String | Category purpose for classification |
| `example_queries` | List[String] | 6-10 example queries for few-shot learning |
| `agent_class` | String | Python class name for agent handler |

**Validation Rules**:
- Must be one of the 6 predefined enum values
- Cannot be extended at runtime (design decision: extensibility via code deployment)

**Relationships**:
- One-to-Many with `RoutingDecision` (one category has many routing decisions)
- One-to-One with `AgentConfiguration` (each category configured to one agent)

**Example Configuration (JSON)**:
```json
{
    "INFORMATION_RETRIEVAL": {
        "name": "Information Retrieval",
        "priority": 1,
        "description": "Simple information retrieval from multiple sources",
        "example_queries": [
            "What are the top 5 job boards for sales positions in Bristol?",
            "What are the average salaries for software engineers in London?",
            "List the best recruitment agencies in Manchester",
            "What are the current hiring trends in fintech?",
            "Show me competitor analysis for our accountancy division",
            "What certifications are required for IT support roles?"
        ],
        "agent_class": "InformationRetrievalAgent"
    }
}
```

---

### 3. RoutingDecision

**Purpose**: Classification result containing assigned category, confidence, and routing metadata

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | Required, Primary Key | Unique identifier for the decision |
| `query_id` | UUID | Required, Foreign Key | Query this decision is for |
| `primary_category` | Category | Required, Enum | Highest-confidence category |
| `primary_confidence` | Decimal | Required, 0.0-1.0 | Confidence score for primary (e.g., 0.85) |
| `secondary_category` | Category | Optional, Enum | Second-highest category (for multi-intent) |
| `secondary_confidence` | Decimal | Optional, 0.0-1.0 | Confidence score for secondary |
| `reasoning` | String | Optional, Max 500 chars | Why this category was chosen (for debugging) |
| `classification_latency_ms` | Integer | Required | Time taken to classify (milliseconds) |
| `fallback_triggered` | Boolean | Required, Default False | Whether confidence < 0.7 triggered clarification |
| `user_override` | Boolean | Required, Default False | Whether user explicitly requested category |
| `timestamp` | DateTime | Required, Auto-generated | When decision was made (UTC) |

**Validation Rules**:
- `primary_confidence` must be between 0.0 and 1.0
- If `secondary_category` is set, `secondary_confidence` must also be set
- `secondary_confidence` < `primary_confidence` always
- If `fallback_triggered` is True, `primary_confidence` < 0.7

**State Transitions**:
1. **Created**: Decision made, not yet executed
2. **Routing**: Agent being invoked
3. **Completed**: Agent returned response
4. **Failed**: Agent failed/timeout, fallback triggered
5. **Clarification**: User asked to choose category (confidence < 70%)

**Relationships**:
- One-to-One with `Query` (each decision for exactly one query)
- Many-to-One with `Category` (via primary_category and secondary_category)

**Example**:
```python
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "query_id": "550e8400-e29b-41d4-a716-446655440000",
    "primary_category": "INFORMATION_RETRIEVAL",
    "primary_confidence": 0.92,
    "secondary_category": "INDUSTRY_KNOWLEDGE",
    "secondary_confidence": 0.35,
    "reasoning": "Query asks for factual list ('top 5 job boards'), clear information retrieval pattern",
    "classification_latency_ms": 87,
    "fallback_triggered": false,
    "user_override": false,
    "timestamp": "2025-10-22T10:30:00.087Z"
}
```

---

### 4. SessionContext

**Purpose**: Conversation state tracking previous messages, routing decisions, and user preferences

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `session_id` | String | Required, Primary Key, UUID | Unique session identifier |
| `user_id` | String | Required | User this session belongs to |
| `created_at` | DateTime | Required, Auto-generated | When session started (UTC) |
| `last_activity_at` | DateTime | Required, Auto-updated | Last query timestamp |
| `expires_at` | DateTime | Required, Computed | When session expires (last_activity + 30 min) |
| `message_history` | List[Dict] | Required, Max 50 messages | Recent conversation turns |
| `routing_history` | List[UUID] | Required | List of routing_decision_ids in order |
| `user_preferences` | Dict | Optional | Persistent preferences (e.g., preferred category for ambiguous queries) |
| `metadata` | Dict | Optional | Additional context (location, role, etc.) |

**Validation Rules**:
- `session_id` must be valid UUID v4
- `expires_at` = `last_activity_at` + 30 minutes
- `message_history` limited to last 50 messages (oldest dropped)
- `routing_history` limited to last 50 routing decisions

**State Transitions**:
1. **Active**: Last activity within 30 minutes
2. **Expired**: No activity for >30 minutes (Redis TTL expired)
3. **Terminated**: User explicitly ended session

**Storage**: Redis with 30-minute TTL, key format: `session:{user_id}:{session_id}`

**Relationships**:
- One-to-Many with `Query` (one session has multiple queries)
- One-to-Many with `RoutingDecision` (via routing_history)

**Example**:
```python
{
    "session_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "user_id": "user_12345",
    "created_at": "2025-10-22T10:00:00Z",
    "last_activity_at": "2025-10-22T10:30:00Z",
    "expires_at": "2025-10-22T11:00:00Z",
    "message_history": [
        {
            "role": "user",
            "content": "Hello",
            "timestamp": "2025-10-22T10:00:00Z",
            "category": "GENERAL_CHAT"
        },
        {
            "role": "assistant",
            "content": "Hello! How can I help you today?",
            "timestamp": "2025-10-22T10:00:01Z"
        },
        {
            "role": "user",
            "content": "What are the top 5 job boards for sales?",
            "timestamp": "2025-10-22T10:30:00Z",
            "category": "INFORMATION_RETRIEVAL"
        }
    ],
    "routing_history": [
        "660e8400-e29b-41d4-a716-446655440001"
    ],
    "user_preferences": {
        "preferred_agent": null,
        "explicit_routing_allowed": true
    },
    "metadata": {
        "user_role": "recruitment_consultant",
        "location": "Bristol"
    }
}
```

---

### 5. AgentConfiguration

**Purpose**: Definition of agent capabilities including available tools, knowledge sources, and processing strategies

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `category` | Category | Required, Primary Key | Category this config is for |
| `agent_class` | String | Required | Python class name (e.g., "InformationRetrievalAgent") |
| `llm_provider` | String | Required, Enum | "groq" or "anthropic" |
| `llm_model` | String | Required | Model identifier (e.g., "llama-3-70b-8192") |
| `timeout_seconds` | Integer | Required, Default 2 | Max execution time |
| `retry_count` | Integer | Required, Default 1 | Number of retries on failure |
| `retry_delay_ms` | Integer | Required, Default 500 | Delay between retries |
| `tools` | List[String] | Optional | Available tools (e.g., ["web_search", "sources_md"]) |
| `resources` | Dict | Optional | Resource paths (e.g., {"sources_file": "./sources_validated_summaries.md"}) |
| `system_prompt` | String | Required | Agent's system prompt/instructions |
| `enabled` | Boolean | Required, Default True | Whether agent is active |

**Validation Rules**:
- `timeout_seconds` must be ≤ 2 (to meet overall latency requirement)
- `llm_provider` must be "groq" or "anthropic"
- `llm_model` must be valid for the provider
- If `category` is INDUSTRY_KNOWLEDGE, `resources.sources_file` must be set

**Relationships**:
- One-to-One with `Category` (each category has one configuration)
- Referenced by agent instances at runtime

**Example**:
```json
{
    "category": "INFORMATION_RETRIEVAL",
    "agent_class": "InformationRetrievalAgent",
    "llm_provider": "groq",
    "llm_model": "llama-3-70b-8192",
    "timeout_seconds": 2,
    "retry_count": 1,
    "retry_delay_ms": 500,
    "tools": ["web_search", "database_query"],
    "resources": {},
    "system_prompt": "You are an information retrieval specialist. When asked a question, search multiple sources and provide a concise, aggregated answer with citations.",
    "enabled": true
}
```

---

### 6. RoutingLog (Database Persistence)

**Purpose**: Audit trail of all routing decisions for analysis and compliance

**Table Schema** (PostgreSQL):

```sql
CREATE TABLE routing_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- User & Session (anonymized after 30 days)
    user_id VARCHAR(255) NOT NULL,
    session_id UUID NOT NULL,

    -- Query Details
    query_text TEXT NOT NULL,
    query_length_words INT NOT NULL,
    query_truncated BOOLEAN NOT NULL DEFAULT FALSE,

    -- Classification Results
    primary_category VARCHAR(50) NOT NULL,
    primary_confidence DECIMAL(5,4) NOT NULL,
    secondary_category VARCHAR(50),
    secondary_confidence DECIMAL(5,4),

    -- Performance Metrics
    classification_latency_ms INT NOT NULL,
    agent_execution_latency_ms INT,

    -- Outcome
    agent_success BOOLEAN NOT NULL,
    fallback_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    user_override BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,

    -- Audit
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_routing_logs_timestamp ON routing_logs(timestamp);
CREATE INDEX idx_routing_logs_user_id ON routing_logs(user_id);
CREATE INDEX idx_routing_logs_category ON routing_logs(primary_category);
CREATE INDEX idx_routing_logs_session ON routing_logs(session_id);
```

**Anonymized Table** (30-90 days):

```sql
CREATE TABLE routing_logs_anonymized (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,

    -- Hashed Identifiers
    session_hash VARCHAR(64) NOT NULL,  -- SHA-256(session_id + salt)
    query_hash VARCHAR(64) NOT NULL,    -- SHA-256(query_text + salt)

    -- Preserved Analytics Data
    query_length_words INT NOT NULL,
    query_truncated BOOLEAN NOT NULL,
    primary_category VARCHAR(50) NOT NULL,
    primary_confidence DECIMAL(5,4) NOT NULL,
    secondary_category VARCHAR(50),
    secondary_confidence DECIMAL(5,4),
    classification_latency_ms INT NOT NULL,
    agent_execution_latency_ms INT,
    agent_success BOOLEAN NOT NULL,
    fallback_triggered BOOLEAN NOT NULL,
    user_override BOOLEAN NOT NULL,

    -- Audit
    anonymized_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_routing_logs_anonymized_timestamp ON routing_logs_anonymized(timestamp);
CREATE INDEX idx_routing_logs_anonymized_category ON routing_logs_anonymized(primary_category);
```

---

## Entity Relationships Diagram

```
┌─────────────────┐
│     Query       │
├─────────────────┤
│ id (PK)         │
│ text            │──┐
│ user_id         │  │
│ session_id (FK) │  │ 1:1
│ timestamp       │  │
└─────────────────┘  │
         │           │
         │ M:1       ▼
         │     ┌──────────────────┐
         │     │ RoutingDecision  │
         │     ├──────────────────┤
         │     │ id (PK)          │
         │     │ query_id (FK)    │
         │     │ primary_category │───┐
         │     │ confidence       │   │ M:1
         │     │ timestamp        │   │
         │     └──────────────────┘   │
         │                            │
         ▼                            ▼
┌─────────────────┐          ┌──────────────────┐
│ SessionContext  │          │    Category      │
├─────────────────┤          ├──────────────────┤
│ session_id (PK) │          │ name (PK)        │
│ user_id         │          │ priority         │
│ message_history │          │ example_queries  │
│ routing_history │          │ agent_class      │
│ expires_at      │          └──────────────────┘
└─────────────────┘                   │
                                      │ 1:1
                                      ▼
                            ┌──────────────────────┐
                            │ AgentConfiguration   │
                            ├──────────────────────┤
                            │ category (PK,FK)     │
                            │ llm_provider         │
                            │ llm_model            │
                            │ timeout_seconds      │
                            │ system_prompt        │
                            └──────────────────────┘
```

---

## Validation Summary

### Cross-Entity Validation Rules

1. **Session-Query Consistency**:
   - All queries with same `session_id` must have same `user_id`
   - Query `timestamp` must be ≤ SessionContext `expires_at`

2. **Routing-Category Consistency**:
   - `RoutingDecision.primary_category` must reference valid Category enum
   - `AgentConfiguration.category` must match Category enum

3. **Confidence Logic**:
   - If `secondary_confidence` > `primary_confidence`, reject (data integrity error)
   - If `primary_confidence` < 0.7, `fallback_triggered` must be True

4. **Timeout Constraints**:
   - `classification_latency_ms` + `agent_execution_latency_ms` should be < 3000ms (SC-001 target)
   - Individual `agent_execution_latency_ms` should be < 2000ms per AgentConfiguration

---

## State Machine: Query Processing Lifecycle

```
[Query Received]
      │
      ▼
[Validate & Truncate]  (if > 1000 words)
      │
      ▼
[Load Session Context] (from Redis)
      │
      ▼
[Classify Query]  (sentence-transformers)
      │
      ├─ confidence >= 0.7 ──▶ [Create RoutingDecision]
      │                              │
      │                              ▼
      │                        [Route to Agent]
      │                              │
      │                              ├─ success ──▶ [Return Response]
      │                              │
      │                              └─ failure ──▶ [Retry Once]
      │                                                  │
      │                                                  ├─ success ──▶ [Return Response]
      │                                                  │
      │                                                  └─ failure ──▶ [Fallback to General Chat]
      │
      └─ confidence < 0.7 ──▶ [Ask User Clarification]
                                    │
                                    ▼
                              [User Selects Category]
                                    │
                                    ▼
                              [Route to Selected Agent]
```

---

**Data Model Complete**: All entities defined with validation rules, relationships, and state transitions. Ready for contract generation (Phase 1 continued).
