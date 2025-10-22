# Research: Chat Routing AI

**Feature**: 002-chat-routing-ai
**Date**: 2025-10-22
**Purpose**: Resolve technical unknowns and establish best practices for implementation

## Research Questions

### 1. NLP Framework Selection for Query Classification

**Question**: Which NLP framework should be used for classifying queries into 6 categories with >90% accuracy and <3s latency?

**Options Evaluated**:

| Framework | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **sentence-transformers** | Lightweight, fast inference (<100ms), semantic similarity-based, works offline | Requires custom training data for 6 categories | ⭐ RECOMMENDED |
| **spaCy + custom model** | Full NLP pipeline, proven accuracy, Python-native | Heavier memory footprint, slower inference (200-500ms) | Backup option |
| **OpenAI/Anthropic embeddings + vector DB** | State-of-art accuracy, no training needed | External API dependency, higher latency (>500ms), ongoing costs | Not suitable for latency requirement |
| **Hugging Face transformers (BERT/RoBERTa)** | High accuracy potential | Slow inference without GPU (1-2s), requires fine-tuning | Not suitable for latency requirement |

**Decision**: **sentence-transformers with pre-trained all-MiniLM-L6-v2 model**

**Rationale**:
- **Performance**: <100ms inference latency allows meeting <3s end-to-end requirement even with database lookups and agent execution
- **Accuracy**: Semantic similarity approach naturally handles multi-intent queries and can achieve >90% accuracy with proper prompt engineering
- **Offline**: No external API dependencies, critical for reliability and cost control
- **Lightweight**: ~25MB model size, minimal memory footprint
- **Few-shot capable**: Can use example-based classification without requiring thousands of training samples

**Implementation Approach**:
1. Pre-define 6-10 example queries per category (60 total examples)
2. Encode examples using sentence-transformers
3. For new query: encode and compute cosine similarity to all examples
4. Return top category with confidence score (percentage of top match vs. second-best)
5. If confidence < 70%, trigger clarification flow (FR-007)

**Alternatives Considered & Rejected**:
- **spaCy**: Rejected due to slower inference (200-500ms) pushing latency budget
- **LLM APIs**: Rejected due to >500ms latency and external dependency risk
- **BERT-based transformers**: Rejected due to >1s inference without GPU acceleration

---

### 2. LLM Provider Selection for Agent Execution

**Question**: Which LLM provider should power the 6 specialized agents?

**Options Evaluated**:

| Provider | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Groq (llama-3-70b-8192)** | Ultra-fast inference (500-800 tokens/sec), cost-effective, proven in existing codebase | Requires API key, limited context window (8K) | ⭐ RECOMMENDED |
| **Anthropic Claude** | High-quality reasoning, large context (200K), proven reliability | Higher cost, slower than Groq | Premium option |
| **OpenAI GPT-4** | Strong general capability, widely documented | Expensive, moderate speed | Backup option |
| **Local LLM (Ollama/llama.cpp)** | No API costs, full control | Requires GPU/high CPU, complex deployment, slower inference | Not suitable for production |

**Decision**: **Groq (llama-3-70b-8192) as primary, Claude 3.5 Sonnet for complex problem-solving**

**Rationale**:
- **Groq for 5 agents** (Information Retrieval, Report Generation, Automation, Industry Knowledge, General Chat):
  - Speed: 500-800 tokens/sec meets <2s agent timeout
  - Cost: ~10x cheaper than GPT-4
  - Proven: Already used in example_email_classification_groq.py
  - Sufficient: These categories don't require deepest reasoning

- **Claude 3.5 Sonnet for Problem Solving agent**:
  - Reasoning depth: Complex multi-step analysis benefits from Claude's capabilities
  - Context: 200K window handles extensive industry data cross-referencing
  - Accuracy: Higher quality solutions justify slightly higher cost for high-impact use case

**Implementation Approach**:
- Agent configuration file (JSON/YAML) specifies model per agent
- Base agent class abstracts provider differences
- Environment variables for API keys (GROQ_API_KEY, ANTHROPIC_API_KEY)
- Fallback chain: Groq → Claude → Error (for Groq-powered agents)

**Alternatives Considered & Rejected**:
- **Single provider for all**: Rejected to optimize cost/performance per use case
- **Local LLMs**: Rejected due to infrastructure complexity and slower inference
- **GPT-4 everywhere**: Rejected due to unnecessary cost for simpler categories

---

### 3. Redis vs. In-Memory Session Storage

**Question**: Should session context use Redis or in-memory storage?

**Options Evaluated**:

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **Redis with 30-min TTL** | Persistent across restarts, scales horizontally, automatic expiry | External dependency, network latency (~1-5ms) | ⭐ RECOMMENDED |
| **In-memory dict with background cleanup** | Zero latency, no dependencies | Lost on restart, single-server limit, manual TTL management | Not suitable |
| **PostgreSQL with timestamp checks** | Already in stack, persistent | Slower (10-50ms), requires cleanup job, not designed for sessions | Not suitable |

**Decision**: **Redis with 30-minute TTL**

**Rationale**:
- **Requirement**: FR-005 requires session persistence across queries (multi-turn conversations)
- **Scale**: Redis scales horizontally if concurrent users increase beyond single-server capacity
- **Reliability**: Survives application restarts without losing active sessions
- **Performance**: 1-5ms latency negligible compared to 2s agent execution budget
- **Automatic expiry**: Native TTL support eliminates need for cleanup jobs

**Implementation Approach**:
```python
# Session key format: session:{user_id}:{session_id}
# Value: JSON serialized SessionContext
# TTL: 1800 seconds (30 minutes)
redis_client.setex(f"session:{user_id}:{session_id}", 1800, json.dumps(context))
```

**Alternatives Considered & Rejected**:
- **In-memory**: Rejected due to loss on restart and single-server scaling limit
- **PostgreSQL**: Rejected due to slower performance and need for custom cleanup logic

---

### 4. PostgreSQL Schema for Routing Logs

**Question**: How should routing logs be structured for 90-day retention with 30-day anonymization?

**Decision**: **Two-table approach with scheduled anonymization job**

**Schema**:

```sql
-- Table 1: Full logs (0-30 days)
CREATE TABLE routing_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id VARCHAR(255) NOT NULL,              -- Anonymized after 30 days
    session_id VARCHAR(255) NOT NULL,
    query_text TEXT NOT NULL,                    -- Truncated to 1000 words
    query_length_words INT NOT NULL,
    classified_category VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    secondary_category VARCHAR(50),              -- For multi-intent tracking
    secondary_confidence DECIMAL(5,4),
    routing_latency_ms INT NOT NULL,
    agent_success BOOLEAN NOT NULL,
    agent_latency_ms INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Table 2: Anonymized logs (30-90 days) - moved via cron job
CREATE TABLE routing_logs_anonymized (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    session_hash VARCHAR(64) NOT NULL,          -- SHA-256(session_id + salt)
    query_hash VARCHAR(64) NOT NULL,            -- SHA-256(query_text + salt)
    query_length_words INT NOT NULL,
    classified_category VARCHAR(50) NOT NULL,
    confidence_score DECIMAL(5,4) NOT NULL,
    secondary_category VARCHAR(50),
    secondary_confidence DECIMAL(5,4),
    routing_latency_ms INT NOT NULL,
    agent_success BOOLEAN NOT NULL,
    agent_latency_ms INT,
    anonymized_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_routing_logs_timestamp ON routing_logs(timestamp);
CREATE INDEX idx_routing_logs_user_id ON routing_logs(user_id);
CREATE INDEX idx_routing_logs_category ON routing_logs(classified_category);
CREATE INDEX idx_routing_logs_anonymized_timestamp ON routing_logs_anonymized(timestamp);
CREATE INDEX idx_routing_logs_anonymized_category ON routing_logs_anonymized(classified_category);
```

**Anonymization Process**:
- Scheduled job runs daily at 2 AM
- Moves records >30 days old from routing_logs → routing_logs_anonymized
- Hashes user_id, session_id, query_text (one-way with salt)
- Deletes records >90 days old from routing_logs_anonymized

**Rationale**:
- **Privacy**: User IDs removed after 30 days (GDPR-compliant)
- **Analysis**: Patterns preserved via hashes for trend analysis
- **Performance**: Old records don't slow down current queries
- **Compliance**: Automatic 90-day purge ensures data minimization

**Alternatives Considered & Rejected**:
- **Single table with nullable user_id**: Rejected due to confusing semantics and harder to enforce cleanup
- **Separate database**: Rejected as unnecessary complexity for single-feature logs

---

### 5. Agent Interface Contract

**Question**: What should the base agent interface look like for extensibility?

**Decision**: **Abstract base class with async process() method**

**Interface Design**:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AgentRequest:
    query: str
    user_id: str
    session_id: str
    context: Optional[Dict[str, Any]] = None  # Previous routing decisions, user preferences

@dataclass
class AgentResponse:
    success: bool
    content: str
    metadata: Dict[str, Any]  # Sources cited, processing time, etc.
    error: Optional[str] = None

class BaseAgent(ABC):
    """Abstract base class for all agent handlers"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize agent with configuration (model, tools, resources)"""
        self.config = config
        self.timeout = config.get('timeout_seconds', 2)

    @abstractmethod
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process request and return response. Must complete within self.timeout."""
        pass

    @abstractmethod
    def get_category(self) -> str:
        """Return the category this agent handles"""
        pass

    def validate_request(self, request: AgentRequest) -> bool:
        """Validate request before processing. Override if needed."""
        return len(request.query) > 0
```

**Rationale**:
- **Async**: Allows concurrent agent execution and proper timeout handling
- **Dataclasses**: Type-safe, serializable request/response objects
- **Config-driven**: Agent behavior customizable without code changes
- **Metadata**: Flexible response envelope for sources, timing, etc.
- **Timeout**: Enforced at base level, agents must respect or handle internally

**Example Implementation**:

```python
class InformationRetrievalAgent(BaseAgent):
    def get_category(self) -> str:
        return "Information Retrieval"

    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            # Execute within timeout using asyncio.wait_for
            result = await asyncio.wait_for(
                self._fetch_information(request.query),
                timeout=self.timeout
            )
            return AgentResponse(
                success=True,
                content=result,
                metadata={"sources": ["source1", "source2"], "latency_ms": 450}
            )
        except asyncio.TimeoutError:
            return AgentResponse(
                success=False,
                content="",
                metadata={},
                error="Agent timeout exceeded"
            )
```

**Alternatives Considered & Rejected**:
- **Synchronous interface**: Rejected as blocks event loop and complicates timeout handling
- **Function-based agents**: Rejected due to lack of state management and configuration
- **gRPC/REST APIs**: Rejected as over-engineered for in-process agents (may reconsider for remote agents)

---

## Best Practices Summary

### Classification Best Practices
1. **Few-shot learning**: Use 6-10 carefully crafted examples per category
2. **Confidence thresholds**: 70% for routing, 50% for secondary intent
3. **Calibration**: Log predictions vs. manual labels for first 1000 queries
4. **Monitoring**: Track confusion matrix weekly to identify misclassifications

### Agent Best Practices
1. **Timeout handling**: Use asyncio.wait_for with circuit breakers
2. **Retry logic**: Single retry with exponential backoff (wait 500ms before retry)
3. **Graceful degradation**: Always provide fallback response (general chat)
4. **Tool access**: Agents load tools dynamically via config (e.g., sources_validated_summaries.md path)

### Storage Best Practices
1. **Session cleanup**: Redis SCAN for orphaned keys, manual cleanup if TTL fails
2. **Log partitioning**: Consider partitioning routing_logs by month if volume >1M/month
3. **Backup**: Daily pg_dump of routing_logs before anonymization job
4. **Monitoring**: Alert if anonymization job fails or takes >10 minutes

### Testing Best Practices
1. **Contract tests**: Ensure all agents implement BaseAgent interface correctly
2. **Integration tests**: Mock Redis/PostgreSQL using docker-compose for CI
3. **Load tests**: Simulate 100 concurrent users to validate <3s latency
4. **Accuracy tests**: Maintain golden dataset of 100 manually labeled queries per category

---

## Technology Stack Summary

| Component | Technology | Version | Justification |
|-----------|-----------|---------|---------------|
| Classification | sentence-transformers | 2.2+ | Fast inference (<100ms), semantic similarity |
| Primary LLM | Groq (llama-3-70b) | latest | Ultra-fast (500-800 tok/s), cost-effective |
| Premium LLM | Claude 3.5 Sonnet | latest | Complex reasoning for Problem Solving agent |
| Session Storage | Redis | 7.0+ | TTL support, horizontal scaling, persistence |
| Log Storage | PostgreSQL | 14+ | ACID compliance, mature, already in stack |
| Testing | pytest + pytest-asyncio | latest | Async test support, fixture ecosystem |
| Monitoring | structlog | latest | Structured logging for log aggregation |

---

## Open Questions for Implementation Phase

1. **Load balancing**: Should multiple router instances share Redis, or use consistent hashing?
   - **Recommendation**: Share Redis with connection pooling (simpler, Redis handles concurrency)

2. **Agent versioning**: How to handle agent updates without breaking in-flight sessions?
   - **Recommendation**: Version agents in config, session stores agent_version, route to matching version

3. **Multi-language support**: FR-012 mentions non-English queries as edge case - defer or handle?
   - **Recommendation**: Defer to v2, current scope is English-only (document in assumptions)

4. **Cost monitoring**: How to track LLM API costs per agent category?
   - **Recommendation**: Log token usage per request in routing_logs.metadata JSON field

---

**Research Complete**: All NEEDS CLARIFICATION items resolved. Ready for Phase 1 (Design & Contracts).
