# Implementation Plan: Staff Specialisations

**Branch**: `003-staff-specialisations` | **Date**: 2025-10-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-staff-specialisations/spec.md`

## Summary

Implement a staff specialisation system that extends the Chat Routing AI agents with role-specific resource capabilities. Each agent can receive an optional `staff_role` parameter referencing one of 5 ProActive People organizational roles (Managing Director, Temp Consultant, Resourcer/Admin/Tech, Compliance/Wellbeing, Finance/Training). Agents access role-specific resources from dedicated directories and incorporate relevant context into responses. Technical approach: Modular Python extension to existing AI router, adding optional staff role parameter handling, resource discovery/loading, and response enhancement with role context.

## Technical Context

**Language/Version**: Python 3.11+ (extends existing router infrastructure)
**Primary Dependencies**: Existing AI router modules (utils/ai_router/), pathlib for file system access, json/yaml for resource parsing
**Storage**: File system-based resource directories (`Staff Specialisation Resources/`) + optional in-memory resource cache for performance
**Testing**: pytest with agent mocks, integration tests for resource loading, end-to-end tests for role-context responses
**Target Platform**: Linux server (same as Chat Routing AI, existing ProActive People infrastructure)
**Project Type**: Single (extension to backend library + CLI interface for testing)
**Performance Goals**: <500ms resource retrieval latency, <3s end-to-end impact on existing agent latency, 100% resource accuracy
**Constraints**: Optional staff_role parameter (backward compatible), case-sensitive validation, agents must handle empty resource directories gracefully
**Scale/Scope**: 5 staff roles with extensible resource directories, supports concurrent agent access, no modification of existing agent contract

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: No project constitution file found at `.specify/memory/constitution.md`. Using standard software engineering gates from parent feature (Chat Routing AI).

### Modularity & Testability
- ✅ **Modular Design**: Staff specialisation system separate from agent implementations (utils/ai_router/staff_specialisations/)
- ✅ **Backward Compatible**: Optional staff_role parameter doesn't break existing agent interface
- ✅ **Testable Components**: Resource discovery and loading can be mocked for unit tests
- ✅ **Clear Boundaries**: Staff role validation, resource discovery, and resource integration are distinct

### Performance & Scalability
- ✅ **Performance Targets Defined**: <500ms resource retrieval, <3s total impact on agent latency (SC-002)
- ✅ **Scalability Considered**: Extensible directory structure supports new roles without code changes
- ✅ **Concurrent Access**: File system reads are thread-safe, caching can handle multiple agents

### Data & Privacy
- ✅ **No New Data Sensitive**: Resources are job-related documents, no personal data handling required
- ✅ **File System Security**: Resources stored in version-controlled `staff_specialisations/` directory
- ✅ **No Session State**: Staff specialisation is request-scoped, no persistent user data

### Operational Readiness
- ✅ **Observability**: Agent responses can include `staff_role_context` metadata (FR-010)
- ✅ **Error Handling**: Graceful degradation if resources unavailable or corrupted (FR-004)
- ✅ **Extensibility**: New resources can be added without code deployment (FR-008)

**Gate Status**: ✅ PASS (staff specialisation is non-breaking extension with clear scope)

## Project Structure

### Documentation (this feature)

```text
specs/003-staff-specialisations/
├── plan.md                          # This file (/speckit.plan command output)
├── research.md                      # Phase 0 output (/speckit.plan command)
├── data-model.md                    # Phase 1 output (/speckit.plan command)
├── quickstart.md                    # Phase 1 output (/speckit.plan command)
├── contracts/                       # Phase 1 output (/speckit.plan command)
│   └── staff_specialisations_interface.md
├── spec.md                          # Feature specification
├── README.md                        # Feature overview
├── CLARIFICATIONS.md                # Clarification session report
└── checklists/requirements.md       # Quality checklist
```

### Source Code (repository root)

```text
utils/ai_router/                    # Existing routing system
├── ...existing modules...
├── Staff Specialisation Resources/  # NEW: Staff specialisation resource module
│   ├── __init__.py
│   ├── specialisation_manager.py    # Main StaffSpecialisationManager class
│   ├── resource_loader.py           # Resource discovery and loading
│   ├── models.py                    # StaffRole enum, resource models
│   ├── validators.py                # Staff role validation
│   └── context_builder.py           # Build response context from resources

Staff Specialisation Resources/     # Resource directories (initially empty)
├── person_1_managing_director/
│   └── resources-guide.md           # (will be added later)
├── person_2_temp_consultant/
├── person_3_resourcer_admin_tech/
├── person_4_compliance_wellbeing/
└── person_5_finance_training/

tests/ai_router/                    # Existing test structure
├── unit/
│   └── test_staff_specialisations/  # NEW unit tests
│       ├── test_resource_loader.py
│       ├── test_validators.py
│       └── test_context_builder.py
├── integration/
│   └── test_staff_specialisations_integration.py  # NEW integration tests
└── fixtures/
    └── staff_specialisations_fixtures.py  # Shared test fixtures
```

**Structure Decision**: Extension to existing Chat Routing AI module structure. Staff specialisation system is added as a new submodule (`utils/ai_router/staff_specialisations/`) that integrates with existing agent infrastructure. Maintains separation of concerns and allows independent testing of specialisation features before full integration.

## Integration Points

### With Existing Chat Routing AI
- **AgentRequest**: Extended to include optional `staff_role` parameter
- **AgentResponse**: Enhanced to include optional `staff_role_context` field
- **Agent Base Class**: No changes required; specialisation happens before agent invocation
- **Routing Decision**: Can track which staff role was used (for monitoring/logging)

### Resource Discovery
- **File System**: Primary storage in `Staff Specialisation Resources/{role}/`
- **Resource Guide**: Optional `resources-guide.md` in each role directory for agent guidance
- **Resource Formats**: Support multiple formats (markdown, text, JSON) through pluggable parsers

## Phase 0: Research & Unknowns

**Unknowns identified in spec:**
1. Resource file format preferences (markdown, JSON, YAML, text)
2. Resource caching strategy (in-memory vs. lazy-load)
3. Concurrent access patterns and file locking requirements
4. Resource guide structure and format

**Research Tasks:**
- Research Python file system patterns for concurrent safe access
- Research best practices for resource discovery and loading
- Research caching strategies for file-based resources in Python
- Review YAML vs JSON vs Markdown for resource guide structure

**Research Output**: research.md (Phase 0 deliverable)

## Phase 1: Design & Contracts

**Phase 1 Tasks:**

1. **Data Model Design** (data-model.md)
   - StaffRole enum (5 defined roles with descriptions)
   - ResourceMetadata (path, type, created, updated, format)
   - SpecialisationContext (role, loaded_resources, resource_guide)
   - Resource types (guideline, template, knowledge_base, training)

2. **API Contracts** (contracts/)
   - StaffSpecialisationManager interface (get_specialisation, load_resources)
   - Resource loader contract (discover_resources, load_resource)
   - Validator contract (validate_staff_role, validate_resource_path)
   - Integration with existing AgentRequest/AgentResponse

3. **Quickstart Guide** (quickstart.md)
   - Environment setup (no new dependencies, uses existing Python env)
   - Resource directory structure explanation
   - Integration steps with existing agents
   - Testing procedures (unit + integration)
   - Deployment checklist

## Phase 2: Tasks (NOT created by /speckit.plan)

Task generation handled by `/speckit.tasks` command:
- Dependency mapping and priority ordering
- Parallel execution opportunities
- Testing strategy per task
- Acceptance criteria mapping
- Risk mitigation tasks

**Output**: tasks.md

## Technology Decisions

### 1. Resource Storage Location
**Decision**: File system (`Staff Specialisation Resources/`)
**Rationale**:
- Aligns with git-based management (easy to version control)
- Human-readable structure for future resource additions
- No new infrastructure dependencies
**Alternative Rejected**: Database storage (adds complexity, not needed for small resource sets)

### 2. Resource Loading Strategy
**Decision**: Agent-driven with optional `resources-guide.md` for navigation
**Rationale**:
- Delegates prioritization to agent intelligence
- Avoids brittle file ordering requirements
- Flexible to agent-specific needs
**Alternative Rejected**: Rigid priority-based ordering (less flexible for different agent types)

### 3. Staff Role Validation
**Decision**: Case-sensitive exact matching
**Rationale**:
- Prevents ambiguity and confusion
- Aligns with system parameter best practices
- Simple and predictable behavior
**Alternative Rejected**: Case-insensitive (could mask typos)

### 4. Resource Format Support
**Decision**: Flexible format support (start with Markdown, add JSON if needed)
**Rationale**:
- Markdown is human-friendly for documentation
- JSON enables structured data when needed
- Pluggable parser allows easy format addition
**Alternative Rejected**: Single format only (less flexible for diverse resource types)

### 5. Performance Strategy
**Decision**: Lazy loading with optional in-memory cache
**Rationale**:
- Resources loaded only when staff_role specified
- No overhead for queries without specialisation
- Cache improves performance for repeated role queries
- <500ms target easily achieved with file system + cache
**Alternative Rejected**: Eager loading at startup (wastes memory, not needed)

## Key Considerations

### Backward Compatibility
- Staff role is **optional** parameter - queries without it work unchanged
- No changes to existing AgentRequest/AgentResponse contracts (extension only)
- Existing agents continue to work without specialisation

### Extensibility
- Resource directory structure allows adding new roles without code changes
- Plugin architecture for resource parsers (start with plain text, add JSON/YAML later)
- `resources-guide.md` provides room for future metadata/guidance

### Risk Mitigation
1. **Missing Resources**: Agents gracefully handle empty directories
2. **File Access Issues**: Fallback to agent execution without specialisation
3. **Resource Corruption**: Error handling in resource parser, graceful degradation
4. **Concurrent Access**: File system reads are atomic, no write conflicts expected

### Testing Strategy
- **Unit Tests**: Resource discovery, validation, context building (mocked file system)
- **Integration Tests**: End-to-end with actual directory structure, multiple resources
- **Performance Tests**: Verify <500ms loading latency
- **Compatibility Tests**: Ensure non-specialised queries unaffected

## Success Metrics

1. **Functional**: All 10 functional requirements met (FR-001 through FR-010)
2. **Performance**: <500ms resource retrieval (SC-002), <3s total agent latency (SC-004)
3. **Compatibility**: 100% of existing queries work unchanged (SC-004)
4. **Relevance**: 20%+ improvement in response relevance for role-specific queries (SC-007)
5. **Code Quality**: 90%+ test coverage, clean separation of concerns, no tech debt

## Timeline Estimate

**Phase 0 (Research)**: 1-2 days
- Technology decision validation
- Best practices research
- Alternative evaluation

**Phase 1 (Design & Contracts)**: 2-3 days
- Data model definition
- Contract specification
- Quickstart documentation

**Phase 2 (Implementation & Testing)**: 5-7 days
- Core module implementation
- Unit tests (70% coverage)
- Integration tests (80% coverage)
- Performance validation

**Phase 3 (Polish & Deployment)**: 2-3 days
- Final testing
- Documentation review
- Staging validation
- Production deployment

**Total**: ~12-16 working days

---

**Document Version**: 1.0
**Created**: 2025-10-23
**Status**: Ready for Phase 0 Research
