# Quick Start Guide: Chat Routing AI

**Feature**: 002-chat-routing-ai
**Date**: 2025-10-22
**Audience**: Developers implementing the Chat Routing AI system

## Overview

The Chat Routing AI system classifies user queries into six categories and routes them to specialized agent handlers. This guide will help you set up the system, understand the architecture, and start implementing agents.

## Prerequisites

Before starting implementation, ensure you have:

- **Python 3.11+** installed
- **Redis 7.0+** running (for session management)
- **PostgreSQL 14+** running (for routing logs)
- **API Keys**:
  - Groq API key (`GROQ_API_KEY`)
  - Anthropic API key (`ANTHROPIC_API_KEY`)
- **Development Tools**:
  - `uv` or `pip` for package management
  - `pytest` for testing
  - Docker (optional, for local Redis/PostgreSQL)

## Installation

### 1. Install Dependencies

```bash
# Using uv (recommended)
cd d:/Recruitment
uv pip install sentence-transformers==2.2.2
uv pip install redis==5.0.0
uv pip install psycopg2-binary==2.9.9
uv pip install structlog==24.1.0
uv pip install pytest==7.4.3
uv pip install pytest-asyncio==0.21.1

# Or using pip
pip install -r requirements-ai-router.txt
```

Create `requirements-ai-router.txt`:
```
sentence-transformers==2.2.2
redis==5.0.0
psycopg2-binary==2.9.9
structlog==24.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
```

### 2. Set Environment Variables

Create `.env` file in project root:
```bash
# LLM API Keys
GROQ_API_KEY=gsk_your_groq_api_key_here
ANTHROPIC_API_KEY=sk-ant-your_anthropic_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Empty if no password

# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=recruitment
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password_here

# Router Configuration
ROUTER_CONFIDENCE_THRESHOLD=0.7
ROUTER_MAX_QUERY_WORDS=1000
ROUTER_SESSION_TTL_SECONDS=1800  # 30 minutes
ROUTER_AGENT_TIMEOUT_SECONDS=2
ROUTER_LOG_RETENTION_DAYS=90
ROUTER_LOG_ANONYMIZE_AFTER_DAYS=30
```

### 3. Set Up Database

Run the SQL migration to create routing log tables:

```bash
psql -h localhost -U postgres -d recruitment -f sql/migrations/001_create_routing_logs.sql
```

Contents of `sql/migrations/001_create_routing_logs.sql`:
```sql
-- Create routing logs table
CREATE TABLE IF NOT EXISTS routing_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id VARCHAR(255) NOT NULL,
    session_id UUID NOT NULL,
    query_text TEXT NOT NULL,
    query_length_words INT NOT NULL,
    query_truncated BOOLEAN NOT NULL DEFAULT FALSE,
    primary_category VARCHAR(50) NOT NULL,
    primary_confidence DECIMAL(5,4) NOT NULL,
    secondary_category VARCHAR(50),
    secondary_confidence DECIMAL(5,4),
    classification_latency_ms INT NOT NULL,
    agent_execution_latency_ms INT,
    agent_success BOOLEAN NOT NULL,
    fallback_triggered BOOLEAN NOT NULL DEFAULT FALSE,
    user_override BOOLEAN NOT NULL DEFAULT FALSE,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_routing_logs_timestamp ON routing_logs(timestamp);
CREATE INDEX idx_routing_logs_user_id ON routing_logs(user_id);
CREATE INDEX idx_routing_logs_category ON routing_logs(primary_category);
CREATE INDEX idx_routing_logs_session ON routing_logs(session_id);

-- Create anonymized logs table
CREATE TABLE IF NOT EXISTS routing_logs_anonymized (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    session_hash VARCHAR(64) NOT NULL,
    query_hash VARCHAR(64) NOT NULL,
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
    anonymized_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_routing_logs_anonymized_timestamp ON routing_logs_anonymized(timestamp);
CREATE INDEX idx_routing_logs_anonymized_category ON routing_logs_anonymized(primary_category);
```

## Architecture Overview

```
┌─────────────┐
│   User      │
│   Query     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│        AIRouter (router.py)             │
│                                         │
│  1. Validate & Truncate Query          │
│  2. Load Session Context (Redis)       │
│  3. Classify Query (classifier.py)     │
│  4. Make Routing Decision              │
│  5. Route to Agent                     │
│  6. Log Decision (PostgreSQL)          │
│  7. Return Response                    │
└──────┬──────────────────────────────────┘
       │
       ├──▶ [Confidence >= 70%] ──▶ Agent Handler
       │
       └──▶ [Confidence < 70%]  ──▶ User Clarification
                                          │
                                          ▼
                                    User Selects Category
                                          │
                                          ▼
                                    Agent Handler
                                          │
                                          ▼
┌──────────────────────────────────────────────────┐
│    Agent Handlers (agents/)                      │
│                                                  │
│  • InformationRetrievalAgent                    │
│  • ProblemSolvingAgent (Claude 3.5 Sonnet)     │
│  • ReportGenerationAgent                        │
│  • AutomationAgent                              │
│  • IndustryKnowledgeAgent                       │
│  • GeneralChatAgent                             │
│                                                  │
│  Each agent:                                    │
│  1. Validates request                           │
│  2. Executes with timeout                       │
│  3. Returns AgentResponse                       │
│  4. Handles errors gracefully                   │
└──────────────────────────────────────────────────┘
```

## Implementation Checklist

### Phase 1: Core Router (Week 1)

- [ ] Create `utils/ai_router/` directory structure
- [ ] Implement `models/` (Query, RoutingDecision, SessionContext, AgentConfig)
- [ ] Implement `classifier.py`:
  - Load sentence-transformers model (all-MiniLM-L6-v2)
  - Encode 6-10 example queries per category
  - Implement cosine similarity classification
  - Return primary + secondary categories with confidence
- [ ] Implement `session_manager.py`:
  - Redis connection with connection pooling
  - Session CRUD operations
  - 30-minute TTL management
- [ ] Implement `storage/log_repository.py`:
  - PostgreSQL connection
  - Insert routing logs
  - Query log analytics
- [ ] Implement `router.py` (main AIRouter class):
  - Query validation and truncation
  - Session context loading
  - Classification orchestration
  - Routing logic with confidence threshold
  - Error handling and fallback

### Phase 2: Agent Framework (Week 2)

- [ ] Implement `agents/base_agent.py` (abstract base class from contract)
- [ ] Implement `agent_registry.py`:
  - Load agent configurations from JSON
  - Dynamic agent instantiation
  - Agent availability checks
- [ ] Create agent configuration file (`config/agents.json`):
  ```json
  {
    "INFORMATION_RETRIEVAL": {
      "agent_class": "InformationRetrievalAgent",
      "llm_provider": "groq",
      "llm_model": "llama-3-70b-8192",
      "timeout_seconds": 2,
      "system_prompt": "You are an information retrieval specialist...",
      "tools": ["web_search"],
      "enabled": true
    },
    "PROBLEM_SOLVING": {
      "agent_class": "ProblemSolvingAgent",
      "llm_provider": "anthropic",
      "llm_model": "claude-3-5-sonnet-20241022",
      "timeout_seconds": 2,
      "system_prompt": "You are a problem-solving expert...",
      "tools": ["web_search", "analysis"],
      "enabled": true
    }
    // ... other agents
  }
  ```

### Phase 3: Agent Implementations (Weeks 3-4)

Implement each agent in priority order:

**Priority 1 (Week 3)**:
- [ ] `information_retrieval_agent.py` (P1, high frequency)
- [ ] `industry_knowledge_agent.py` (P1, high frequency)
  - Must access `sources_validated_summaries.md`
- [ ] `general_chat_agent.py` (P3, fallback agent)

**Priority 2 (Week 4)**:
- [ ] `problem_solving_agent.py` (P2, uses Claude)
- [ ] `automation_agent.py` (P2, workflow design)
- [ ] `report_generation_agent.py` (P3, visualization)

### Phase 4: Testing (Week 5)

**Contract Tests**:
- [ ] Test all agents implement BaseAgent interface correctly
- [ ] Validate agent configuration loading
- [ ] Test timeout enforcement

**Unit Tests**:
- [ ] `test_classifier.py` - Classification accuracy with golden dataset
- [ ] `test_router.py` - Routing logic, confidence thresholds
- [ ] `test_session_manager.py` - Redis operations, TTL
- [ ] `test_agents/test_*_agent.py` - Each agent's process() method

**Integration Tests**:
- [ ] `test_routing_flow.py` - End-to-end query → agent → response
- [ ] `test_session_persistence.py` - Multi-turn conversation context
- [ ] `test_log_retention.py` - PostgreSQL logging and anonymization

**Load Tests**:
- [ ] Simulate 100 concurrent users
- [ ] Validate <3s latency for 95% of requests
- [ ] Test Redis/PostgreSQL under load

### Phase 5: Deployment Readiness (Week 6)

- [ ] Create `cli.py` for command-line testing
- [ ] Set up anonymization cron job (runs daily at 2 AM)
- [ ] Configure monitoring and alerting
- [ ] Write deployment documentation
- [ ] Conduct load testing in staging environment

## Quick Test

Test the router with a simple query:

```python
# test_quick_start.py
import asyncio
from utils.ai_router.router import AIRouter
from utils.ai_router.models.query import Query

async def main():
    # Initialize router
    router = AIRouter()

    # Create test query
    query = Query(
        text="What are the top 5 job boards for sales positions?",
        user_id="test_user",
        session_id="550e8400-e29b-41d4-a716-446655440000"
    )

    # Route query
    response = await router.route(query)

    # Print results
    print(f"Category: {response.routing_decision.primary_category}")
    print(f"Confidence: {response.routing_decision.primary_confidence:.2f}")
    print(f"Response: {response.agent_response.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run with:
```bash
python test_quick_start.py
```

Expected output:
```
Category: INFORMATION_RETRIEVAL
Confidence: 0.92
Response: Based on my research, the top 5 job boards for sales positions are: 1. Indeed, 2. Reed, 3. Totaljobs, 4. CV-Library, 5. Monster.
```

## Debugging

### Enable Debug Logging

```python
import structlog
import logging

logging.basicConfig(level=logging.DEBUG)
structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG)
)
```

### Check Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### Check PostgreSQL Connection

```bash
psql -h localhost -U postgres -d recruitment -c "SELECT COUNT(*) FROM routing_logs;"
```

### Test Classification Model

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
query = "What are the top job boards?"
embedding = model.encode(query)
print(f"Embedding shape: {embedding.shape}")  # Should be (384,)
```

## Common Issues

### Issue: `ModuleNotFoundError: No module named 'sentence_transformers'`
**Solution**: Install dependencies: `uv pip install sentence-transformers`

### Issue: `redis.exceptions.ConnectionError`
**Solution**: Start Redis: `redis-server` or `docker run -d -p 6379:6379 redis:7`

### Issue: `psycopg2.OperationalError: could not connect to server`
**Solution**: Check PostgreSQL is running and credentials are correct in `.env`

### Issue: Agent timeout after 2 seconds
**Solution**:
1. Check LLM API keys are valid
2. Verify network connection to Groq/Anthropic
3. Consider increasing timeout in agent config (but stay under 2s for SC-001)

### Issue: Classification confidence always low (<70%)
**Solution**: Review and improve example queries in agent configuration. Ensure examples cover diverse phrasings for each category.

## Next Steps

1. **Review Documentation**:
   - [data-model.md](data-model.md) - Entity definitions and relationships
   - [research.md](research.md) - Technology decisions and best practices
   - [contracts/](contracts/) - API contracts and agent interface

2. **Implement Core Router** (Phase 1):
   - Start with `classifier.py` - this is the critical component
   - Test classification accuracy with golden dataset (target >90%)
   - Integrate with session management

3. **Implement Agents** (Phase 2-3):
   - Use `MockAgent` from `contracts/agent_interface.py` for testing router logic
   - Implement real agents in priority order
   - Test each agent independently before integration

4. **Set Up Monitoring**:
   - Track classification accuracy (log confusion matrix weekly)
   - Monitor agent latency (alert if p95 > 2s)
   - Track fallback rate (target <10%)

## Support

For questions or issues during implementation:

1. Check [research.md](research.md) for technology decisions and rationale
2. Review [data-model.md](data-model.md) for entity definitions
3. Check contract tests in `tests/ai_router/contract/`
4. Refer to [plan.md](plan.md) for overall architecture

## Success Metrics

Track these metrics to ensure implementation meets requirements:

- **Routing Accuracy**: >90% (SC-002)
- **Latency (p95)**: <3s end-to-end (SC-001)
- **Agent Success Rate**: >95% (within timeout)
- **Fallback Rate**: <10% (confidence < 70%)
- **Session Context Accuracy**: >95% multi-turn conversations (SC-008)

---

**Implementation Timeline**: 6 weeks (see Implementation Checklist)
**Next Command**: `/speckit.tasks` - Generate detailed task breakdown from this plan
