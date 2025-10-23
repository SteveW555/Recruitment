# Implementation Tasks: Staff Specialisations

**Feature**: Staff Specialisations (003-staff-specialisations)
**Branch**: `003-staff-specialisations`
**Date**: 2025-10-23
**Total Tasks**: 92
**Phases**: 5 (Setup, Foundational, US1, US2, US3, Polish)

## Project Overview

This document contains all implementation tasks for the Staff Specialisations feature, organized by user story to enable independent implementation and parallel development. Each user story is independently testable and can be deployed separately.

**User Stories**:
- **User Story 1** (P1): Query Agent Receives Staff Role Parameter
- **User Story 2** (P1): Agent Accesses Role-Specific Resources
- **User Story 3** (P2): Agent Enhances Responses with Role Context

**Key Constraint**: No new external dependencies (uses only Python stdlib)

---

## Dependency Graph & Parallel Opportunities

```
Phase 1 (Setup)
  ↓
Phase 2 (Foundational)
  ├─→ US1 (can proceed in parallel after Phase 2)
  ├─→ US2 (depends on US1 completion)
  └─→ US3 (depends on US2 completion)

Parallel Opportunities:
  • Phase 1 tasks: All independent (can run in parallel)
  • US1 tasks: Can split into [P] parallelizable subtasks
  • US2 tasks: Can split into [P] parallelizable subtasks
  • US3 tasks: Sequential (builds on US1 + US2)
```

**MVP Scope** (Minimum Viable Product):
- Phase 1: Setup
- Phase 2: Foundational
- User Story 1: Complete (staff_role parameter recognition)
- User Story 2: Complete (resource loading)
- Polish: Basic validation

**Estimated MVP Timeline**: 6-8 working days (Phases 1-2 + US1 + US2 + basic polish)
**Estimated Full Timeline**: 12-16 working days (all phases including US3 + comprehensive polish and testing)

---

## Phase 1: Setup & Project Initialization

Project initialization, directory structure, and dependency verification.

### Setup Tasks

- [ ] T001 Create `utils/ai_router/staff_specialisations/` directory structure per plan.md in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/
- [ ] T002 Create `__init__.py` in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/__init__.py (empty, will export public classes)
- [ ] T003 Create `tests/ai_router/unit/test_staff_specialisations/` directory structure in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/
- [ ] T004 Create `tests/ai_router/integration/` directory structure in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/
- [ ] T005 Create `tests/ai_router/fixtures/` directory structure in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/fixtures/
- [ ] T006 Verify staff_specialisations resource directories exist (5 role directories created in Phase /speckit.specify) in /Users/steve/Documents/GitHub/Recruitment/specs/003-staff-specialisations/staff_specialisations/
- [ ] T007 Verify Python 3.11+ installed and pytest available via existing Chat Routing AI setup
- [ ] T008 Review existing Chat Routing AI module structure (utils/ai_router/) to understand integration patterns
- [ ] T009 Review existing agent interfaces (BaseAgent, AgentRequest, AgentResponse) in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/

---

## Phase 2: Foundational Components

Core data models and interfaces that all user stories depend on.

### Foundational Architecture

- [ ] T010 Implement `StaffRole` enum in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/models.py with 5 values (person_1_managing_director, person_2_temp_consultant, person_3_resourcer_admin_tech, person_4_compliance_wellbeing, person_5_finance_training)
- [ ] T011 Implement `ResourceFormat` enum in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/models.py with values (markdown, json, text, guide)
- [ ] T012 Implement `ResourceMetadata` dataclass in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/models.py with fields (name, path, format, size_bytes, is_guide, created_at, updated_at, checksum)
- [ ] T013 Implement `Resource` dataclass in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/models.py with fields (metadata, content, parsed, error) and `is_valid` property
- [ ] T014 Implement `SpecialisationStatus` enum in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/models.py with values (loaded, invalid_role, no_resources, error, not_requested)
- [ ] T015 Implement `SpecialisationContext` dataclass in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/models.py with fields (staff_role, resources, guide, status, error_message, loaded_at) and methods (is_available, is_error)

### Foundational Validation

- [ ] T016 Implement `validate_staff_role()` function in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/validators.py (case-sensitive enum validation with helpful error messages)
- [ ] T017 Implement `validate_resource_path()` function in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/validators.py (checks file exists, readable, size < 10MB, correct location)
- [ ] T018 Implement `validate_resource_content()` function in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/validators.py (validates UTF-8 encoding)

### Foundational Tests

- [ ] T019 Create test fixtures in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/fixtures/staff_specialisations_fixtures.py (sample role directories, test resources, mocked file system)
- [ ] T020 Create unit tests for `StaffRole` enum in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_models.py (all 5 values present, case-sensitive)
- [ ] T021 Create unit tests for `SpecialisationContext` dataclass in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_models.py (is_available, is_error, field validation)
- [ ] T022 Create unit tests for `validate_staff_role()` in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_validators.py (valid roles, invalid roles, case-sensitivity, error messages)
- [ ] T023 Create unit tests for `validate_resource_path()` in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_validators.py (file exists, readable, size limits, format support)

### Foundational Integration

- [ ] T024 Extend `AgentRequest` in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/models/agent_request.py to include optional fields (staff_role, specialisation_context)
- [ ] T025 Extend `AgentResponse` in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/models/agent_response.py to include optional field (staff_role_context) and metadata support
- [ ] T026 Create integration test setup in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (test fixtures, mocked Chat Routing AI components)

---

## User Story 1: Query Agent Receives Staff Role Parameter (P1)

**Goal**: Enable agents to receive and identify staff role parameters without errors.

**Acceptance Criteria**:
- [ ] Agent can parse staff_role parameter from request
- [ ] Agent can identify target role directory based on staff_role value
- [ ] Agent handles missing staff_role gracefully (continues normally)
- [ ] Agent handles invalid staff_role gracefully (logs warning, continues without specialisation)
- [ ] <1ms validation latency for staff role checking

**Independent Test**: Pass staff_role parameter to agent, verify correct role directory identification without requiring resource loading.

### US1: Resource Loader Implementation

- [ ] T027 [P] [US1] Implement `ResourceLoader` class in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/resource_loader.py with `__init__` method (base_path, cache_ttl_seconds)
- [ ] T028 [P] [US1] Implement `discover_resources()` method in ResourceLoader (glob pattern discovery, exclude resources-guide.md, return Dict[str, Path])
- [ ] T029 [P] [US1] Implement `load_guide()` method in ResourceLoader (read resources-guide.md if exists, return Optional[str])
- [ ] T030 [P] [US1] Implement `load_resource()` method in ResourceLoader (detect format, parse markdown/json/text, return Resource with error handling)
- [ ] T031 [P] [US1] Implement `load_resources()` method in ResourceLoader (with in-memory caching, 1-hour TTL, return Dict[str, Resource])
- [ ] T032 [P] [US1] Implement `invalidate_cache()` method in ResourceLoader (manual cache clearing for testing)

### US1: Specialisation Manager Implementation

- [ ] T033 [US1] Implement `SpecialisationManager` class in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/specialisation_manager.py with `__init__` method (loader injection)
- [ ] T034 [US1] Implement `get_specialisation_context()` method in SpecialisationManager (staff_role parameter validation, resource loading, error handling, return SpecialisationContext with appropriate status)
- [ ] T035 [US1] Implement `get_available_roles()` method in SpecialisationManager (return list of 5 valid role strings)
- [ ] T036 [US1] Implement `validate_staff_role()` wrapper method in SpecialisationManager (convenience method, O(1) lookup)
- [ ] T037 [US1] Implement `clear_cache()` method in SpecialisationManager (delegation to resource_loader)
- [ ] T038 [US1] Implement error handling in get_specialisation_context() for invalid roles (ValueError with helpful message, log warning, return context with status=INVALID_ROLE)
- [ ] T039 [US1] Implement error handling in get_specialisation_context() for missing directories (no error, log info, return context with status=NO_RESOURCES)

### US1: Agent Integration

- [ ] T040 [US1] Create wrapper function in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/__init__.py to initialize SpecialisationManager (module entry point)
- [ ] T041 [US1] Integrate SpecialisationManager into existing router in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/router.py (inject manager, populate specialisation_context on requests with staff_role)
- [ ] T042 [US1] Add staff_role parameter acceptance to router routing logic in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/router.py (pass through to agent request)
- [ ] T043 [US1] Update router response handling in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/router.py (add staff_role_context metadata if specialisation applied)

### US1: Unit Tests

- [ ] T044 [P] [US1] Create unit tests for `ResourceLoader.discover_resources()` in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_resource_loader.py (empty dir, multiple files, exclude guide, alphabetical order)
- [ ] T045 [P] [US1] Create unit tests for `ResourceLoader.load_guide()` in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_resource_loader.py (guide exists, guide missing, error handling)
- [ ] T046 [P] [US1] Create unit tests for `ResourceLoader.load_resource()` in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_resource_loader.py (markdown parsing, json parsing, text parsing, unsupported format, corrupted file)
- [ ] T047 [P] [US1] Create unit tests for caching behavior in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_resource_loader.py (cache hit <10ms, cache miss reload, TTL expiration)
- [ ] T048 [US1] Create unit tests for `SpecialisationManager.get_specialisation_context()` in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_specialisation_manager.py (valid role, invalid role, no resources, error handling, status codes)
- [ ] T049 [US1] Create unit tests for `SpecialisationManager.get_available_roles()` in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_specialisation_manager.py (returns exactly 5 roles, correct values)

### US1: Integration Tests

- [ ] T050 [US1] Create integration test for staff_role parameter handling in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (valid role → context loaded, invalid role → graceful degradation, no role → normal operation)
- [ ] T051 [US1] Create integration test for backward compatibility in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (queries without staff_role work unchanged)
- [ ] T052 [US1] Create integration test for directory structure discovery in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (all 5 roles discoverable, empty directories handled)

### US1: Performance Validation

- [ ] T053 [US1] Add performance test for resource discovery latency in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (measure <500ms initial load, <10ms cached)
- [ ] T054 [US1] Add performance test for validation latency in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (measure <1ms staff_role validation)

---

## User Story 2: Agent Accesses Role-Specific Resources (P1)

**Goal**: Enable agents to discover, load, and access role-specific resources.

**Acceptance Criteria**:
- [ ] All resources in role directory are discoverable
- [ ] Resources can be loaded with correct format parsing
- [ ] Empty resource directories handled gracefully
- [ ] Multiple resources accessible (returns dict of all resources)
- [ ] Resources-guide.md consulted for navigation (if present)
- [ ] <500ms resource loading latency
- [ ] Corrupted resources don't crash loading (error handling)

**Independent Test**: Place sample resources in role directory, load via SpecialisationManager, verify all resources retrieved and parsed correctly.

### US2: Context Builder Implementation

- [ ] T055 [US2] Implement `build_context_prompt()` function in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/context_builder.py (generate prompt addition from SpecialisationContext, include guide if available)
- [ ] T056 [US2] Implement `select_relevant_resources()` function in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/context_builder.py (agent-driven selection of resources based on query and guide)
- [ ] T057 [US2] Implement `build_metadata()` function in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/context_builder.py (create response metadata dict with role info, resources consulted, status)

### US2: Multiple Format Support

- [ ] T058 [US2] Implement Markdown parser in resource_loader.py (extract headings, preserve content, return parsed dict with format="markdown")
- [ ] T059 [US2] Implement JSON parser in resource_loader.py (json.loads(), validate structure, return parsed dict with format="json")
- [ ] T060 [US2] Implement Text parser in resource_loader.py (split into lines, return parsed dict with format="text")
- [ ] T061 [US2] Implement pluggable parser architecture in resource_loader.py (ResourceParser class with PARSERS dict for extensibility)

### US2: Unit Tests

- [ ] T062 [P] [US2] Create unit tests for context builder functions in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_context_builder.py (build_context_prompt with guide, without guide, empty context)
- [ ] T063 [P] [US2] Create unit tests for resource parsers in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_resource_loader.py (markdown headings extraction, json validation, text line splitting)
- [ ] T064 [US2] Create unit tests for multiple resource loading in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/unit/test_staff_specialisations/test_resource_loader.py (load 3+ resources, verify all accessible, correct format detection)

### US2: Integration Tests

- [ ] T065 [US2] Create integration test for multi-format resource loading in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (load markdown + json + text in same role, verify all accessible)
- [ ] T066 [US2] Create integration test for empty role directories in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (no crash, status=no_resources, agent continues normally)
- [ ] T067 [US2] Create integration test for resources-guide.md handling in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (guide loaded, guide missing handled, guide content accessible to agent)

---

## User Story 3: Agent Enhances Responses with Role Context (P2)

**Goal**: Enable agents to incorporate role-specific resources into responses.

**Acceptance Criteria**:
- [ ] Agent responses include role context when specialisation applied
- [ ] Responses reflect role-specific information from resources
- [ ] Response metadata includes staff_role_context tracking
- [ ] Responses accurate even when role context unavailable
- [ ] Responses note relevant role context appropriately
- [ ] 20%+ improvement in relevance for role-specific queries (qualitative)

**Independent Test**: Assign staff_role with resources, verify agent response incorporates role-relevant information (differs from non-specialised response).

### US3: Agent Response Enhancement

- [ ] T068 [US3] Update agent execution in router to include context prompt from SpecialisationContext in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/router.py
- [ ] T069 [US3] Update agent response handling in router to populate staff_role_context field in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/router.py
- [ ] T070 [US3] Update agent response metadata to include specialisation tracking (staff_role_used, specialisation_status, resources_consulted) in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/router.py

### US3: Integration Tests

- [ ] T071 [US3] Create integration test for response enhancement in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (response with role context differs from response without, role info incorporated)
- [ ] T072 [US3] Create integration test for role-aware responses in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (managing director query reflects strategy focus, compliance query reflects compliance focus)
- [ ] T073 [US3] Create integration test for graceful degradation in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (query outside role expertise still works, still helpful, notes role context)
- [ ] T074 [US3] Create end-to-end test for full specialisation flow in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/test_staff_specialisations_integration.py (request with staff_role → context loaded → response enhanced → metadata populated)

---

## Final Phase: Polish & Cross-Cutting Concerns

Quality assurance, documentation, and deployment preparation.

### Code Quality & Documentation

- [ ] T075 Add comprehensive docstrings to all functions/classes in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/ (module, class, method level)
- [ ] T076 Add type hints to all functions/classes in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/ (arguments, returns, Optional handling)
- [ ] T077 Update /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/__init__.py to export public classes (SpecialisationManager, ResourceLoader, StaffRole, SpecialisationContext)
- [ ] T078 Create README in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/ explaining module purpose, usage examples, configuration

### Error Handling & Logging

- [ ] T079 Add structured logging to ResourceLoader (debug discovery, info loaded resources, warn parse errors, error file access issues) in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/resource_loader.py
- [ ] T080 Add structured logging to SpecialisationManager (debug context loading, info empty directories, warn invalid roles, error critical failures) in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/specialisation_manager.py
- [ ] T081 Implement retry logic for file access errors in ResourceLoader in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/resource_loader.py (1 retry with exponential backoff)
- [ ] T082 Implement comprehensive error messages for validation failures in validators.py (list valid values, suggest corrections) in /Users/steve/Documents/GitHub/Recruitment/utils/ai_router/staff_specialisations/validators.py

### Testing Coverage & Validation

- [ ] T083 Run full unit test suite with coverage (target 90%+ in staff_specialisations module) via pytest tests/ai_router/unit/test_staff_specialisations/
- [ ] T084 Run full integration test suite via pytest tests/ai_router/integration/test_staff_specialisations_integration.py
- [ ] T085 Run performance tests and validate all latency targets (<500ms initial, <10ms cached, <1ms validation) via pytest tests/ai_router/integration/
- [ ] T086 Run backward compatibility tests (queries without staff_role work unchanged) via pytest tests/ai_router/integration/
- [ ] T087 Test with concurrent agent access (10+ agents accessing same role resources simultaneously) via custom performance test in /Users/steve/Documents/GitHub/Recruitment/tests/ai_router/integration/
- [ ] T088 Test graceful degradation scenarios (corrupted files, permission errors, missing directories) via pytest tests/ai_router/unit/

### Deployment & Verification

- [ ] T089 Verify all imports resolve correctly (no circular dependencies, all modules importable)
- [ ] T090 Verify no external dependencies added (only stdlib: pathlib, json, enum, logging, dataclasses, time)
- [ ] T091 Create deployment checklist document in /Users/steve/Documents/GitHub/Recruitment/specs/003-staff-specialisations/DEPLOYMENT_CHECKLIST.md
- [ ] T092 Update feature branch with commit message documenting all changes via git commit
- [ ] T093 Create pull request against master branch with feature overview and test instructions

---

## Summary by Phase

| Phase | Task Count | Status | Notes |
|-------|-----------|--------|-------|
| Phase 1: Setup | 9 | Pending | Project initialization, directory structure |
| Phase 2: Foundational | 17 | Pending | Core models, validation, integration setup |
| User Story 1 | 27 | Pending | Role parameter handling, discovery (P1) |
| User Story 2 | 13 | Pending | Resource loading, multi-format support (P1) |
| User Story 3 | 7 | Pending | Response enhancement with context (P2) |
| Polish | 19 | Pending | Quality, testing, deployment |
| **Total** | **92** | **Pending** | Complete implementation + testing |

## Summary by Task Type

| Type | Count | Notes |
|------|-------|-------|
| Core Implementation | 42 | Main modules, methods, classes |
| Testing (Unit) | 24 | Unit test files and cases |
| Testing (Integration) | 12 | Integration and end-to-end tests |
| Documentation | 8 | Docstrings, README, deployment guides |
| Quality & Validation | 6 | Coverage, performance, verification |

## Execution Notes

### MVP Path (6-8 days):
1. Complete Phase 1: Setup (1 day)
2. Complete Phase 2: Foundational (1-2 days)
3. Complete User Story 1 (2-3 days)
4. Complete User Story 2 (2-3 days)
5. Polish: Basic validation (1 day)

### Full Implementation Path (12-16 days):
Complete all phases including User Story 3 and comprehensive polish.

### Parallel Execution Opportunities:
- **Phase 1**: T001-T009 all independent, can run in parallel
- **Phase 2**: T010-T018 can run in parallel (separate models, validators), T019-T026 can run in parallel with implementation
- **US1**: T027-T032 (ResourceLoader methods) parallelizable, T044-T049 (tests) parallelizable with implementation
- **US2**: T058-T061 (parsers) parallelizable, T062-T064 (tests) can run after implementation
- **US3**: Sequential (builds on US1+US2)

### Test-First Strategy (Optional TDD):
1. Write test for each task before implementation
2. Run test (should fail - red)
3. Implement functionality (green)
4. Refactor if needed (refactor)
5. Move to next task

This approach ensures 90%+ test coverage by construction.

---

**Document Version**: 1.0
**Created**: 2025-10-23
**Phase**: Phase 2 Complete (/speckit.tasks)
**Status**: Ready for Implementation
