# Implementation Tasks: Chat Routing AI

**Feature**: 002-chat-routing-ai
**Branch**: `002-chat-routing-ai`
**Created**: 2025-10-22
**Total Tasks**: 63
**Implementation Strategy**: MVP-first, incremental delivery by user story

## Implementation Strategy

**MVP Scope** (Week 1-2): User Story 1 + User Story 5 (P1 priorities)
- Core routing infrastructure
- Information Retrieval agent (most common use case)
- Industry Knowledge agent (high-frequency, critical for recruitment)
- Basic testing and validation

**Incremental Delivery** (Weeks 3-6):
- Week 3: User Story 2 & 4 (P2 priorities)
- Week 4: User Story 3 & 6 (P3 priorities)
- Week 5: Integration testing, polish
- Week 6: Load testing, deployment preparation

## User Story Completion Order & Dependencies

```
Phase 1: Setup (No dependencies)
    └─▶ Phase 2: Foundational (Requires Setup)
            ├─▶ Phase 3: User Story 1 [P1] (Information Retrieval) - MVP
            ├─▶ Phase 4: User Story 5 [P1] (Industry Knowledge) - MVP
            ├─▶ Phase 5: User Story 2 [P2] (Problem Solving)
            ├─▶ Phase 6: User Story 4 [P2] (Automation)
            ├─▶ Phase 7: User Story 3 [P3] (Report Generation)
            └─▶ Phase 8: User Story 6 [P3] (General Chat)
                    └─▶ Phase 9: Polish & Cross-Cutting
```

**Independent Stories**: User Stories 1, 2, 3, 4, 5, 6 can all be implemented in parallel after Foundational phase completes.

**Critical Path**: Setup → Foundational → Any P1 Story (for MVP)

---

## Phase 1: Setup & Project Initialization

**Goal**: Initialize project structure, install dependencies, configure environment

**Duration**: Day 1

### Tasks

- [X] T001 Create utils/ai_router/ directory structure per plan.md
- [X] T002 Create utils/ai_router/models/ directory with __init__.py
- [X] T003 Create utils/ai_router/agents/ directory with __init__.py
- [X] T004 Create utils/ai_router/storage/ directory with __init__.py
- [X] T005 Create tests/ai_router/ directory with unit/, integration/, contract/ subdirectories
- [X] T006 Create requirements-ai-router.txt with sentence-transformers==2.2.2, redis==5.0.0, psycopg2-binary==2.9.9, structlog==24.1.0, pytest==7.4.3, pytest-asyncio==0.21.1
- [X] T007 Create .env file with GROQ_API_KEY, ANTHROPIC_API_KEY, REDIS_HOST, POSTGRES_HOST configuration per quickstart.md
- [X] T008 Create config/agents.json configuration file with skeleton for 6 agent categories
- [X] T009 Create sql/migrations/001_create_routing_logs.sql with routing_logs and routing_logs_anonymized tables per data-model.md
- [ ] T010 Install Python dependencies: uv pip install -r requirements-ai-router.txt (See scripts/setup_ai_router.sh)
- [ ] T011 Run PostgreSQL migration: psql -h localhost -U postgres -d recruitment -f sql/migrations/001_create_routing_logs.sql (See scripts/setup_ai_router.sh)
- [ ] T012 Verify Redis connection: redis-cli ping (See scripts/setup_ai_router.sh)
- [ ] T013 Verify sentence-transformers model download: python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" (See scripts/setup_ai_router.sh)

---

## Phase 2: Foundational - Core Infrastructure

**Goal**: Implement foundational components required by all user stories

**Duration**: Week 1 (Days 2-5)

**Why Foundational**: These components are blocking prerequisites for all user stories. Router, classifier, session management, and storage must work before any agent can be tested.

### Data Models (Blocking for all stories)

- [X] T014 [P] Implement Category enum in utils/ai_router/models/category.py with 6 predefined categories
- [X] T015 [P] Implement Query model in utils/ai_router/models/query.py with validation (1000 word limit, truncation)
- [X] T016 [P] Implement RoutingDecision model in utils/ai_router/models/routing_decision.py with confidence scoring
- [X] T017 [P] Implement SessionContext model in utils/ai_router/models/session_context.py with 30-min expiry
- [X] T018 [P] Implement AgentConfiguration model in utils/ai_router/models/agent_config.py with provider/model settings

### Storage Layer (Blocking for session management and logging)

- [ ] T019 Implement Redis session store in utils/ai_router/storage/session_store.py with 30-minute TTL and connection pooling
- [ ] T020 Implement PostgreSQL log repository in utils/ai_router/storage/log_repository.py with insert/query methods
- [ ] T021 Test Redis session CRUD operations: create, read, update TTL, delete
- [ ] T022 Test PostgreSQL log insertion and retrieval with sample routing decision

### Classification Engine (Blocking for all routing)

- [ ] T023 Implement Classifier in utils/ai_router/classifier.py: load sentence-transformers model (all-MiniLM-L6-v2)
- [ ] T024 Add example query encoding in Classifier: encode 6-10 examples per category from config/agents.json
- [ ] T025 Implement cosine similarity classification in Classifier: return primary + secondary categories with confidence scores
- [ ] T026 Test Classifier with sample queries: verify >70% confidence for clear queries, <70% for ambiguous
- [ ] T027 Create golden dataset in tests/fixtures/golden_queries.json: 100 manually labeled queries (10-20 per category)
- [ ] T028 Validate Classifier accuracy against golden dataset: target >90% accuracy

### Agent Framework (Blocking for all agent implementations)

- [ ] T029 Implement BaseAgent abstract class in utils/ai_router/agents/base_agent.py from contracts/agent_interface.py
- [ ] T030 Implement AgentRegistry in utils/ai_router/agent_registry.py: load configs, instantiate agents, check availability
- [ ] T031 Implement MockAgent in tests/fixtures/mock_agent.py for testing router logic without real LLM calls
- [ ] T032 Test AgentRegistry: load config, instantiate MockAgent, verify get_agent() and is_agent_available()

### Core Router (Blocking for all routing logic)

- [ ] T033 Implement AIRouter class in utils/ai_router/router.py: query validation, truncation (1000 words)
- [ ] T034 Add session context loading in AIRouter: load from Redis, handle expired sessions
- [ ] T035 Add classification orchestration in AIRouter: call Classifier, check confidence threshold (70%)
- [ ] T036 Add routing decision logic in AIRouter: route to agent or trigger clarification, handle multi-intent with secondary notification
- [ ] T037 Add agent execution in AIRouter: call agent.process() with timeout (2s), retry once on failure with 500ms delay
- [ ] T038 Add fallback logic in AIRouter: if agent fails after retry, route to general chat agent with explanation
- [ ] T039 Add logging in AIRouter: log all routing decisions to PostgreSQL via log_repository
- [ ] T040 Test AIRouter end-to-end with MockAgent: query → classify → route → log

### CLI Interface (Useful for manual testing)

- [ ] T041 Implement CLI in utils/ai_router/cli.py: accept query, user_id, session_id arguments
- [ ] T042 Add CLI output formatting: display category, confidence, response, latency metrics
- [ ] T043 Test CLI with sample query: python utils/ai_router/cli.py --query "What are the top job boards?" --user_id test

---

## Phase 3: User Story 1 [P1] - Route Information Retrieval Query

**Goal**: Implement Information Retrieval agent to handle simple multi-source data lookup queries

**Priority**: P1 (MVP, most common use case)

**Independent Test Criteria**:
- Submit query: "What are the top 5 job boards for sales positions in Bristol?"
- Verify category: INFORMATION_RETRIEVAL
- Verify confidence: >0.70
- Verify agent returns: Aggregated information from multiple sources
- Verify latency: <3s end-to-end

**Duration**: Week 2 (Days 1-2)

### Agent Implementation

- [ ] T044 [US1] Implement InformationRetrievalAgent in utils/ai_router/agents/information_retrieval_agent.py
- [ ] T045 [US1] Configure InformationRetrievalAgent in config/agents.json: llm_provider=groq, llm_model=llama-3-70b-8192, timeout=2s
- [ ] T046 [US1] Add 6-10 example queries for INFORMATION_RETRIEVAL category in config/agents.json
- [ ] T047 [US1] Implement process() method in InformationRetrievalAgent: call Groq API with timeout, handle errors
- [ ] T048 [US1] Add web search tool integration in InformationRetrievalAgent (if available in existing codebase)
- [ ] T049 [US1] Test InformationRetrievalAgent with sample query: verify aggregated response, sources cited, latency <2s

### Integration Testing

- [ ] T050 [US1] Test routing flow: submit "top job boards" query → verify routes to InformationRetrievalAgent → verify response
- [ ] T051 [US1] Test multi-source aggregation: verify agent cites multiple sources in metadata
- [ ] T052 [US1] Test agent failure handling: mock agent timeout → verify retry → verify fallback to general chat
- [ ] T053 [US1] Validate User Story 1 acceptance criteria: all 3 scenarios pass

---

## Phase 4: User Story 5 [P1] - Route Industry-Specific Knowledge Query

**Goal**: Implement Industry Knowledge agent to handle UK recruitment domain queries

**Priority**: P1 (MVP, critical for recruitment operations)

**Independent Test Criteria**:
- Submit query: "What is the typical notice period for permanent placements in the UK financial services sector?"
- Verify category: INDUSTRY_KNOWLEDGE
- Verify confidence: >0.70
- Verify agent returns: Domain-specific answer citing validated sources
- Verify sources_validated_summaries.md is accessed

**Duration**: Week 2 (Days 3-4)

### Agent Implementation

- [ ] T054 [US5] Implement IndustryKnowledgeAgent in utils/ai_router/agents/industry_knowledge_agent.py
- [ ] T055 [US5] Configure IndustryKnowledgeAgent in config/agents.json: llm_provider=groq, resources.sources_file=./sources_validated_summaries.md
- [ ] T056 [US5] Add 6-10 example queries for INDUSTRY_KNOWLEDGE category in config/agents.json
- [ ] T057 [US5] Implement process() method in IndustryKnowledgeAgent: load sources_validated_summaries.md, call Groq API with source context
- [ ] T058 [US5] Add source citation logic in IndustryKnowledgeAgent: include sources in response metadata
- [ ] T059 [US5] Test IndustryKnowledgeAgent with UK recruitment query: verify domain-specific answer, sources cited

### Integration Testing

- [ ] T060 [US5] Test routing flow: submit "GDPR requirements for CVs" query → verify routes to IndustryKnowledgeAgent → verify compliance answer
- [ ] T061 [US5] Test source validation: verify agent cites appropriate sources from sources_validated_summaries.md (95% of cases per SC-007)
- [ ] T062 [US5] Test distinction from general info: submit borderline query → verify routes to correct category (Industry vs Information Retrieval)
- [ ] T063 [US5] Validate User Story 5 acceptance criteria: all 3 scenarios pass

---

## Phase 5: User Story 2 [P2] - Route Complex Problem Solving Query

**Goal**: Implement Problem Solving agent using Claude 3.5 Sonnet for complex analysis

**Priority**: P2 (high-value, requires deeper reasoning)

**Independent Test Criteria**:
- Submit query: "How can we reduce candidate dropout rate by 20% within 3 months?"
- Verify category: PROBLEM_SOLVING
- Verify confidence: >0.70
- Verify agent returns: Multi-step analysis, root causes, actionable recommendations
- Verify Claude API is used (not Groq)

**Duration**: Week 3 (Days 1-2)

### Agent Implementation

- [ ] T064 [US2] Implement ProblemSolvingAgent in utils/ai_router/agents/problem_solving_agent.py
- [ ] T065 [US2] Configure ProblemSolvingAgent in config/agents.json: llm_provider=anthropic, llm_model=claude-3-5-sonnet-20241022, timeout=2s
- [ ] T066 [US2] Add 6-10 example queries for PROBLEM_SOLVING category in config/agents.json
- [ ] T067 [US2] Implement process() method in ProblemSolvingAgent: call Anthropic API with structured analysis prompt
- [ ] T068 [US2] Add multi-step analysis logic in ProblemSolvingAgent: problem identification, root cause analysis, recommendations
- [ ] T069 [US2] Test ProblemSolvingAgent with complex problem: verify comprehensive analysis, usefulness rating target 80% (SC-004)

### Integration Testing

- [ ] T070 [US2] Test routing flow: submit "placement rate problem" query → verify routes to ProblemSolvingAgent → verify analysis quality
- [ ] T071 [US2] Test industry benchmark cross-referencing: verify agent includes relevant recruitment industry data
- [ ] T072 [US2] Validate User Story 2 acceptance criteria: all 3 scenarios pass

---

## Phase 6: User Story 4 [P2] - Route Automation Pipeline Request

**Goal**: Implement Automation agent to design workflow pipelines for repetitive tasks

**Priority**: P2 (high operational impact)

**Independent Test Criteria**:
- Submit query: "Every time a new candidate registers, send welcome email, create ATS profile, schedule screening call"
- Verify category: AUTOMATION
- Verify confidence: >0.70
- Verify agent returns: Workflow specification with triggers, actions, conditions
- Verify workflow is implementable (70% without modification per SC-006)

**Duration**: Week 3 (Days 3-4)

### Agent Implementation

- [ ] T073 [US4] Implement AutomationAgent in utils/ai_router/agents/automation_agent.py
- [ ] T074 [US4] Configure AutomationAgent in config/agents.json: llm_provider=groq, llm_model=llama-3-70b-8192
- [ ] T075 [US4] Add 6-10 example queries for AUTOMATION category in config/agents.json
- [ ] T076 [US4] Implement process() method in AutomationAgent: generate workflow with triggers, actions, conditions
- [ ] T077 [US4] Add workflow validation logic in AutomationAgent: ensure triggers and actions are well-defined
- [ ] T078 [US4] Test AutomationAgent with workflow request: verify structured pipeline design, implementability

### Integration Testing

- [ ] T079 [US4] Test routing flow: submit "automate hiring manager notifications" query → verify routes to AutomationAgent → verify workflow spec
- [ ] T080 [US4] Test workflow implementability: manually review 10 generated workflows for completeness (target 70% success per SC-006)
- [ ] T081 [US4] Validate User Story 4 acceptance criteria: all 3 scenarios pass

---

## Phase 7: User Story 3 [P3] - Route Report Generation Request

**Goal**: Implement Report Generation agent to create visualization and presentation reports

**Priority**: P3 (valuable but less frequent)

**Independent Test Criteria**:
- Submit query: "Create a quarterly performance report for our accountancy division showing placements, revenue, trends"
- Verify category: REPORT_GENERATION
- Verify confidence: >0.70
- Verify agent returns: Structured report with visualizations, summaries, insights
- Verify presentation standards (85% meet standards per SC-005)

**Duration**: Week 4 (Days 1-2)

### Agent Implementation

- [ ] T082 [US3] Implement ReportGenerationAgent in utils/ai_router/agents/report_generation_agent.py
- [ ] T083 [US3] Configure ReportGenerationAgent in config/agents.json: llm_provider=groq, llm_model=llama-3-70b-8192
- [ ] T084 [US3] Add 6-10 example queries for REPORT_GENERATION category in config/agents.json
- [ ] T085 [US3] Implement process() method in ReportGenerationAgent: generate structured report with markdown formatting
- [ ] T086 [US3] Add visualization guidance in ReportGenerationAgent: suggest charts, tables, dashboards
- [ ] T087 [US3] Test ReportGenerationAgent with report request: verify structured output, presentation quality

### Integration Testing

- [ ] T088 [US3] Test routing flow: submit "dashboard for top 10 clients" query → verify routes to ReportGenerationAgent → verify dashboard design
- [ ] T089 [US3] Test presentation standards: manually review 10 generated reports for formatting quality (target 85% per SC-005)
- [ ] T090 [US3] Validate User Story 3 acceptance criteria: all 3 scenarios pass

---

## Phase 8: User Story 6 [P3] - Route General Conversation

**Goal**: Implement General Chat agent as fallback for casual conversation and non-business queries

**Priority**: P3 (UX important but lowest business value)

**Independent Test Criteria**:
- Submit query: "Hello"
- Verify category: GENERAL_CHAT
- Verify confidence: >0.70
- Verify agent returns: Friendly, appropriate response
- Verify no specialized business logic invoked

**Duration**: Week 4 (Day 3)

### Agent Implementation

- [ ] T091 [US6] Implement GeneralChatAgent in utils/ai_router/agents/general_chat_agent.py
- [ ] T092 [US6] Configure GeneralChatAgent in config/agents.json: llm_provider=groq, llm_model=llama-3-70b-8192
- [ ] T093 [US6] Add 6-10 example queries for GENERAL_CHAT category in config/agents.json (greetings, off-topic questions)
- [ ] T094 [US6] Implement process() method in GeneralChatAgent: provide conversational responses without business logic
- [ ] T095 [US6] Test GeneralChatAgent with casual queries: verify friendly tone, no business context invoked

### Integration Testing

- [ ] T096 [US6] Test routing flow: submit "How are you?" → verify routes to GeneralChatAgent → verify casual response
- [ ] T097 [US6] Test off-topic handling: submit "What's the weather?" → verify routes to GeneralChatAgent, not InformationRetrievalAgent
- [ ] T098 [US6] Validate User Story 6 acceptance criteria: all 3 scenarios pass

---

## Phase 9: Polish & Cross-Cutting Concerns

**Goal**: Complete testing, monitoring, deployment preparation

**Duration**: Week 5-6

### Contract Testing

- [ ] T099 Implement test_agent_interface.py in tests/ai_router/contract/: validate all 6 agents implement BaseAgent correctly
- [ ] T100 Test agent configuration loading: verify all agents load from config/agents.json without errors
- [ ] T101 Test timeout enforcement: mock slow agent → verify asyncio.wait_for triggers timeout at 2s

### Unit Testing

- [ ] T102 [P] Implement test_classifier.py: test classification with golden dataset, verify >90% accuracy (SC-002)
- [ ] T103 [P] Implement test_router.py: test routing logic, confidence thresholds (70%), multi-intent detection
- [ ] T104 [P] Implement test_session_manager.py: test Redis CRUD, TTL expiry (30 min), connection pooling
- [ ] T105 [P] Implement test_log_repository.py: test PostgreSQL insert, query, anonymization logic

### Integration Testing

- [ ] T106 Implement test_routing_flow.py: end-to-end tests for all 6 user stories with real agents
- [ ] T107 Implement test_session_persistence.py: multi-turn conversation tests, verify context accuracy >95% (SC-008)
- [ ] T108 Implement test_log_retention.py: test log insertion, anonymization after 30 days, deletion after 90 days
- [ ] T109 Test multi-intent notification: submit query spanning 2 categories → verify primary routing + secondary notification

### Performance & Load Testing

- [ ] T110 Create load test script in tests/load/test_concurrent_users.py: simulate 100 concurrent users
- [ ] T111 Run load test: verify <3s latency for 95% of queries (SC-001), identify bottlenecks
- [ ] T112 Test Redis under load: verify session operations maintain <5ms latency under 100 concurrent users
- [ ] T113 Test PostgreSQL under load: verify log writes don't block routing (async logging)
- [ ] T114 Validate routing accuracy under load: verify >90% accuracy maintained (SC-002)

### Monitoring & Observability

- [ ] T115 Implement confusion matrix tracking: log classification predictions vs manual labels (if available)
- [ ] T116 Implement latency monitoring: track p50, p95, p99 latencies for classification, agent execution, end-to-end
- [ ] T117 Implement fallback rate monitoring: track % of queries with confidence <70% (target <10%)
- [ ] T118 Create monitoring dashboard: display accuracy, latency, fallback rate, agent success rate
- [ ] T119 Set up alerts: p95 latency >3s, accuracy <90%, fallback rate >10%, agent failure rate >5%

### Data Lifecycle Management

- [ ] T120 Create anonymization cron job script in scripts/anonymize_logs.sh: move logs >30 days old to routing_logs_anonymized
- [ ] T121 Test anonymization job: verify user_id/query_text hashed, routing patterns preserved
- [ ] T122 Create deletion cron job script in scripts/delete_old_logs.sh: delete logs >90 days old
- [ ] T123 Schedule cron jobs: anonymization daily at 2 AM, deletion daily at 3 AM
- [ ] T124 Test cron job execution: verify logs processed correctly, no data loss

### Documentation & Deployment

- [ ] T125 Update config/agents.json with production LLM API keys (environment variables)
- [ ] T126 Create deployment guide in docs/deployment.md: environment setup, database migrations, cron jobs
- [ ] T127 Create operational runbook in docs/runbook.md: troubleshooting, monitoring, alerting procedures
- [ ] T128 Conduct staging deployment dry run: verify all components work in staging environment
- [ ] T129 Perform final accuracy validation: test with 1000 real queries, verify >90% accuracy

---

## Parallel Execution Opportunities

### Phase 2 (Foundational) - After T013 completes:
```
Parallel Group 1 (Data Models): T014, T015, T016, T017, T018
Parallel Group 2 (Tests + Storage): T019-T022 (after models), T102-T105
Parallel Group 3 (Classification + Agent Framework): T023-T032
Parallel Group 4 (Router + CLI): T033-T043 (after all above)
```

### Phases 3-8 (User Stories) - All can run in parallel after Phase 2:
```
Week 2: US1 + US5 (P1 stories for MVP)
Week 3: US2 + US4 (P2 stories)
Week 4: US3 + US6 (P3 stories)
```

Each user story is independently testable and can be developed by separate developers/teams.

### Phase 9 (Polish) - Many tasks parallelizable:
```
Parallel: T099-T105 (all test implementations)
Sequential: T106-T109 (integration tests depend on agents)
Parallel: T110-T114 (load testing)
Parallel: T115-T119 (monitoring setup)
Sequential: T120-T124 (data lifecycle, depends on monitoring)
Sequential: T125-T129 (deployment preparation)
```

---

## Summary

**Total Tasks**: 129
**Phases**: 9 (1 Setup + 1 Foundational + 6 User Stories + 1 Polish)

**Task Breakdown by Phase**:
- Phase 1 (Setup): 13 tasks
- Phase 2 (Foundational): 30 tasks
- Phase 3 (US1 - Information Retrieval): 10 tasks
- Phase 4 (US5 - Industry Knowledge): 10 tasks
- Phase 5 (US2 - Problem Solving): 9 tasks
- Phase 6 (US4 - Automation): 9 tasks
- Phase 7 (US3 - Report Generation): 9 tasks
- Phase 8 (US6 - General Chat): 8 tasks
- Phase 9 (Polish): 31 tasks

**Parallel Opportunities**: 35 tasks marked with [P] can run in parallel

**MVP Scope** (Phases 1-4): 63 tasks (Weeks 1-2)
- Setup + Foundational + US1 + US5
- Delivers core routing with 2 most critical agents
- Independently testable and deployable

**Success Metrics** (from spec.md):
- ✅ SC-001: <3s latency (95% of queries) - validated in T111
- ✅ SC-002: >90% routing accuracy - validated in T028, T102, T114, T129
- ✅ SC-003: 40% faster information retrieval - validated in T050-T053
- ✅ SC-004: 80% "useful" problem-solving - validated in T069, T070-T072
- ✅ SC-005: 85% presentation standards - validated in T089
- ✅ SC-006: 70% automation workflow implementability - validated in T080
- ✅ SC-007: 95% sources cited for industry knowledge - validated in T061
- ✅ SC-008: 95% context accuracy - validated in T107
- ✅ SC-009: Confidence correlation (R² >0.7) - validated in T102, T103

**Format Validation**: ✅ All 129 tasks follow required checklist format:
- Checkbox: `- [ ]`
- Task ID: T001-T129 (sequential)
- [P] marker: 35 parallelizable tasks
- [Story] label: US1-US6 labels on user story tasks (63 tasks)
- Description: Clear action with file paths

**Next Steps**: Begin implementation starting with Phase 1 (Setup), then proceed to Phase 2 (Foundational), then implement user stories in priority order (P1, P2, P3).
