# Implementation Plan: Chat Routing AI

**Branch**: `002-chat-routing-ai` | **Date**: 2025-10-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-chat-routing-ai/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement an AI-powered query routing system that classifies user queries into six categories (Information Retrieval, Problem Solving, Report Generation, Automation, Industry Knowledge, General Chat) and routes them to specialized agent handlers. The system must achieve 90% routing accuracy, handle queries within 3 seconds, support multi-intent detection, session context management (30-minute expiry), and graceful failure handling with retry logic. Technical approach: Modular Python-based router using NLP classification, with pluggable agent handlers stored in utils/ai_router/.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: NEEDS CLARIFICATION (NLP framework: transformers, spaCy, or sentence-transformers for classification; LLM provider: OpenAI/Anthropic/Groq for agent execution)
**Storage**: Redis for session context (30-min TTL) + PostgreSQL for routing logs (90-day retention with anonymization)
**Testing**: pytest with fixtures for agent mocking, contract tests for agent interfaces
**Target Platform**: Linux server (existing ProActive People infrastructure)
**Project Type**: Single (backend library + CLI interface for testing)
**Performance Goals**: <3s end-to-end latency for 95% of queries, >90% routing accuracy across 6 categories
**Constraints**: <2s timeout for agent execution (with 1 retry), 70% confidence threshold for routing, 1000-word query limit
**Scale/Scope**: 6 agent categories initially (extensible architecture for future categories), handle concurrent users per existing infrastructure limits

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: No project constitution file found at `.specify/memory/constitution.md`. Using standard software engineering gates.

### Modularity & Testability
- ✅ **Modular Design**: Router core separated from agent implementations (utils/ai_router/)
- ✅ **Testable Components**: Agent interface allows mocking for unit tests
- ✅ **Clear Boundaries**: Classification, routing, and agent execution are distinct concerns

### Performance & Scalability
- ✅ **Performance Targets Defined**: <3s end-to-end, <2s agent timeout (SC-001)
- ✅ **Scalability Considered**: Extensible architecture supports future agent categories (FR-011)
- ⚠️ **NEEDS VALIDATION**: Concurrent load handling per existing infrastructure

### Data & Privacy
- ✅ **Data Retention Policy**: 90-day logs with 30-day anonymization (FR-006, GDPR-compliant)
- ✅ **Session Management**: 30-minute TTL prevents indefinite data retention (FR-005)
- ✅ **Privacy by Design**: User IDs removed after 30 days in routing logs

### Operational Readiness
- ✅ **Observability**: Logging all routing decisions with confidence scores (FR-006)
- ✅ **Error Handling**: Retry logic + fallback to general chat (FR-009)
- ✅ **Graceful Degradation**: Low-confidence queries trigger user clarification (FR-007)

**Gate Status**: ✅ PASS (with research required for NLP framework selection and load testing)

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
utils/ai_router/                    # New modular routing system
├── __init__.py
├── router.py                       # Main AIRouter class
├── classifier.py                   # Query classification logic
├── session_manager.py              # Session context with Redis
├── agent_registry.py               # Agent configuration & loading
├── models/
│   ├── __init__.py
│   ├── query.py                    # Query entity
│   ├── routing_decision.py         # RoutingDecision entity
│   ├── session_context.py          # SessionContext entity
│   └── agent_config.py             # AgentConfiguration entity
├── agents/                         # Agent handler implementations
│   ├── __init__.py
│   ├── base_agent.py               # Abstract base class
│   ├── information_retrieval_agent.py
│   ├── problem_solving_agent.py
│   ├── report_generation_agent.py
│   ├── automation_agent.py
│   ├── industry_knowledge_agent.py
│   └── general_chat_agent.py
├── storage/
│   ├── __init__.py
│   ├── log_repository.py           # PostgreSQL routing logs
│   └── session_store.py            # Redis session management
└── cli.py                          # CLI interface for testing

tests/ai_router/
├── unit/
│   ├── test_classifier.py
│   ├── test_router.py
│   ├── test_session_manager.py
│   └── test_agents/
├── integration/
│   ├── test_routing_flow.py
│   ├── test_session_persistence.py
│   └── test_log_retention.py
└── contract/
    └── test_agent_interface.py     # Contract tests for agent base class
```

**Structure Decision**: Single project structure using utils/ai_router/ as specified in requirements. This keeps the routing system modular and allows easy integration with existing ProActive People codebase. The agent/ subdirectory provides clear separation of concerns for the six agent categories while maintaining a common base interface.

## Complexity Tracking

No constitutional violations requiring justification. Design follows modular, testable architecture with clear separation of concerns.

---

## Post-Design Constitution Re-Evaluation

**Date**: 2025-10-22
**Status**: ✅ PASS - All gates validated after Phase 1 design completion

### Modularity & Testability ✅
- **Confirmed**: Router core (`router.py`, `classifier.py`, `session_manager.py`) cleanly separated from agent implementations
- **Confirmed**: Agent interface contract defined in `contracts/agent_interface.py` with MockAgent for testing
- **Confirmed**: Data models isolated in `models/` directory
- **Confirmed**: Storage layer abstracted (`storage/log_repository.py`, `storage/session_store.py`)

### Performance & Scalability ✅
- **Confirmed**: Classification latency budget <100ms (sentence-transformers)
- **Confirmed**: Agent timeout enforced at 2s via asyncio.wait_for
- **Confirmed**: Total latency path: 87ms (classify) + 2000ms (agent) + 100ms (DB) = 2.2s < 3s (meets SC-001)
- **Confirmed**: Extensible architecture supports adding new agent categories without core changes

### Data & Privacy ✅
- **Confirmed**: Two-table schema (routing_logs + routing_logs_anonymized) implements 30-day anonymization
- **Confirmed**: Scheduled job design (cron) for automatic data lifecycle management
- **Confirmed**: Session TTL (30 min) enforced at Redis level
- **Confirmed**: No PII in anonymized logs (SHA-256 hashing with salt)

### Operational Readiness ✅
- **Confirmed**: Structured logging with classification confidence scores, latency metrics
- **Confirmed**: Retry logic (1 retry, 500ms delay) + fallback to general chat agent
- **Confirmed**: Health check endpoint design includes agent availability and storage connectivity
- **Confirmed**: Monitoring points: confusion matrix tracking, latency p95, fallback rate

### Additional Validation

- **API Contract**: OpenAPI 3.0 spec complete (`contracts/router_api.yaml`)
- **Agent Contract**: Python interface contract with validation helpers (`contracts/agent_interface.py`)
- **Data Model**: All entities defined with validation rules and state transitions
- **Quickstart Guide**: 6-week implementation timeline with testing strategy

**Final Gate Status**: ✅ PASS - Ready for Phase 2 (Task Decomposition via `/speckit.tasks`)
