# AI Router Implementation Guide

**Feature**: Chat Routing AI (002-chat-routing-ai)
**Created**: 2025-10-22
**Status**: Phase 1 Complete, Phase 2 In Progress
**Progress**: 11/129 tasks completed (9%)

## Quick Start

### 1. Environment Setup

```bash
# Run the automated setup script
chmod +x scripts/setup_ai_router.sh
./scripts/setup_ai_router.sh

# Copy environment template and configure API keys
cp .env.example .env
# Edit .env and add:
#   GROQ_API_KEY=your_actual_key
#   ANTHROPIC_API_KEY=your_actual_key
```

### 2. Verify Installation

```bash
# Test imports
python -c "from utils.ai_router import AIRouter; print('✓ Import successful')"

# Run tests
pytest tests/ai_router/ -v
```

### 3. Test CLI

```bash
# Basic query routing
python utils/ai_router/cli.py \
  --query "What are the top job boards for sales?" \
  --user_id test_user \
  --session_id $(uuidgen)
```

## Implementation Status

### ✅ Phase 1: Setup Complete (Tasks T001-T013)

**Infrastructure Created**:
- [X] Directory structure: `utils/ai_router/` with models/, agents/, storage/
- [X] Test structure: `tests/ai_router/` with unit/, integration/, contract/
- [X] Dependencies: `requirements-ai-router.txt` with all packages
- [X] Configuration: `config/agents.json` with 6 agent definitions
- [X] Database: `sql/migrations/001_create_routing_logs.sql`
- [X] Environment: `.env.example` updated with AI Router config
- [X] Automation: `scripts/setup_ai_router.sh` for environment setup
- [X] Ignore patterns: `.gitignore` enhanced for Python/ML

**Environment Setup** (via setup script):
- [ ] T010: Install dependencies (`uv pip install -r requirements-ai-router.txt`)
- [ ] T011: Run database migration
- [ ] T012: Verify Redis connection
- [ ] T013: Download sentence-transformers model

### 🔄 Phase 2: Foundational Infrastructure (Tasks T014-T043)

**Data Models** (T014-T018) - ✅ 3/5 Complete:
- [X] T014: Category enum with priority mapping
- [X] T015: Query model with validation and truncation
- [X] T016: RoutingDecision model with confidence scoring
- [ ] T017: SessionContext model with Redis TTL
- [ ] T018: AgentConfiguration model

**Storage Layer** (T019-T022):
- [ ] T019: Redis SessionStore with connection pooling
- [ ] T020: PostgreSQL LogRepository
- [ ] T021: Test Redis CRUD operations
- [ ] T022: Test PostgreSQL logging

**Classification Engine** (T023-T028):
- [ ] T023: Classifier with sentence-transformers
- [ ] T024: Load example queries per category
- [ ] T025: Implement cosine similarity classification
- [ ] T026: Test classification accuracy
- [ ] T027: Create golden dataset (100 queries)
- [ ] T028: Validate >90% accuracy against golden dataset

**Agent Framework** (T029-T032):
- [ ] T029: BaseAgent abstract class from contracts
- [ ] T030: AgentRegistry for configuration loading
- [ ] T031: MockAgent for testing
- [ ] T032: Test AgentRegistry

**Core Router** (T033-T040):
- [ ] T033: AIRouter class with query validation
- [ ] T034: Session context loading
- [ ] T035: Classification orchestration
- [ ] T036: Routing decision logic + multi-intent
- [ ] T037: Agent execution with timeout/retry
- [ ] T038: Fallback logic
- [ ] T039: PostgreSQL logging
- [ ] T040: End-to-end test with MockAgent

**CLI Interface** (T041-T043):
- [ ] T041: CLI implementation
- [ ] T042: Output formatting
- [ ] T043: Test CLI execution

### ⏳ Phase 3: Information Retrieval Agent [P1] (Tasks T044-T053)

**Agent Implementation**:
- [ ] T044: InformationRetrievalAgent class
- [ ] T045: Configure with Groq llama-3-70b-8192
- [ ] T046: Add 6-10 example queries
- [ ] T047: Implement process() with Groq API
- [ ] T048: Web search tool integration
- [ ] T049: Test agent with sample query

**Integration Testing**:
- [ ] T050: Test full routing flow
- [ ] T051: Test multi-source aggregation
- [ ] T052: Test agent failure handling
- [ ] T053: Validate User Story 1 acceptance criteria

### ⏳ Phase 4: Industry Knowledge Agent [P1] (Tasks T054-T063)

**Agent Implementation**:
- [ ] T054: IndustryKnowledgeAgent class
- [ ] T055: Configure with sources_validated_summaries.md
- [ ] T056: Add 6-10 example queries
- [ ] T057: Implement process() with sources lookup
- [ ] T058: Add source citation logic
- [ ] T059: Test with UK recruitment query

**Integration Testing**:
- [ ] T060: Test routing flow
- [ ] T061: Test source validation (95% citation rate)
- [ ] T062: Test category distinction
- [ ] T063: Validate User Story 5 acceptance criteria

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI / API Layer                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                       AIRouter Core                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Query Validation & Truncation (1000 words)        │   │
│  │ 2. Session Context Loading (Redis, 30-min TTL)      │   │
│  │ 3. Classification (sentence-transformers <100ms)     │   │
│  │ 4. Routing Decision (confidence threshold 70%)       │   │
│  │ 5. Agent Execution (timeout 2s, retry once)          │   │
│  │ 6. Fallback (general chat on failure)                │   │
│  │ 7. Logging (PostgreSQL, 90-day retention)            │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴─────────────┬──────────────┐
        ▼                          ▼              ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│ Classifier       │   │ SessionStore     │   │ LogRepository    │
│ (sentence-trans) │   │ (Redis)          │   │ (PostgreSQL)     │
└──────────────────┘   └──────────────────┘   └──────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                      Agent Registry                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Load config/agents.json → Instantiate Agents        │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴──────────┬─────────────┬───────────┐
        ▼                       ▼             ▼           ▼
┌────────────────┐   ┌──────────────┐   ┌─────────┐   ┌──────────┐
│ Information    │   │ Problem      │   │ Report  │   │ Industry │
│ Retrieval      │   │ Solving      │   │ Gen     │   │ Know     │
│ (Groq)         │   │ (Claude)     │   │ (Groq)  │   │ (Groq)   │
└────────────────┘   └──────────────┘   └─────────┘   └──────────┘
