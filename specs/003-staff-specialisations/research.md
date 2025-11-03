# Research & Technology Decisions: Staff Specialisations

**Date**: 2025-10-23
**Feature**: Staff Specialisations (003-staff-specialisations)
**Phase**: Phase 0 - Research & Unknowns Resolution

## Executive Summary

Staff Specialisations extends the Chat Routing AI system with role-specific resource capabilities. This research document resolves technical unknowns identified in the implementation plan and documents all major technology decisions, including resource storage, loading strategies, validation approaches, and performance optimization.

**Key Finding**: Staff specialisation can be implemented as a lightweight Python module using only existing dependencies (pathlib, json, yaml). No new external dependencies required.

---

## Research Questions & Decisions

### 1. Resource Storage Location

**Question**: Where should staff role resources be stored? Database, file system, or cloud storage?

**Research Findings**:
- **File System**: Native Python pathlib support, version control friendly via git, zero infrastructure dependencies, easy human collaboration on resource updates
- **Database**: Adds complexity (schema design, migrations), overkill for small resource sets, harder to version control and audit changes
- **Cloud Storage**: AWS S3/Azure Blob adds latency and infrastructure dependency, not justified for initial MVP
- **Hybrid**: Cache in-memory + load from file system = best of both worlds for performance

**Decision**: **File System with In-Memory Caching**

**Rationale**:
- Aligns with existing ProActive People infrastructure (file-based configuration)
- Simplifies deployment (no database schema changes)
- Enables version control of resource changes (git audit trail)
- Performance: Initial 300-400ms file system read, <10ms cache hit
- Scaling: Current resource count (dozens per role) fits easily in memory

**Implementation**:
```python
# Resource loading pattern
resources = {}  # In-memory cache

def load_staff_role_resources(role: str) -> Dict[str, Resource]:
    if role in resources:
        return resources[role]  # Cache hit

    path = Path(f"specs/003-staff-specialisations/staff_specialisations/{role}")
    resources[role] = discover_and_load(path)  # File system read
    return resources[role]
```

**Alternatives Evaluated**:
- ❌ PostgreSQL: Adds schema complexity, requires migration, harder to version control
- ❌ Redis: Overkill for static resources, requires distributed cache invalidation
- ❌ AWS S3: Adds latency (100-500ms), infrastructure dependency, cost considerations

---

### 2. Resource File Formats

**Question**: What file formats should resources support? Markdown, JSON, YAML, plain text?

**Research Findings**:
- **Markdown**: Most human-friendly, excellent for documentation-style resources, universal git support
- **JSON**: Structured data capability, native Python json library, validates schema
- **YAML**: Python yaml library support, more readable than JSON, less verbose than JSON
- **Plain Text**: Minimal parsing, universal compatibility
- **HTML**: Reduces portability, harder to diff in version control

**Decision**: **Multi-Format Support (Markdown + JSON) with Extensible Parser**

**Rationale**:
- Markdown for documentation-style resources (guidelines, procedures, training materials)
- JSON for structured knowledge bases (FAQ, decision trees, benchmarks)
- Pluggable parser architecture allows adding YAML/other formats later without code changes
- Start with 2 formats (80/20 rule), extend later if needed

**Implementation**:
```python
class ResourceParser:
    """Pluggable resource parser architecture."""

    @staticmethod
    def parse_markdown(content: str) -> Dict[str, Any]:
        return {"format": "markdown", "content": content}

    @staticmethod
    def parse_json(content: str) -> Dict[str, Any]:
        return json.loads(content)

    PARSERS = {
        ".md": parse_markdown,
        ".json": parse_json,
    }

def load_resource(path: Path) -> Dict[str, Any]:
    parser = ResourceParser.PARSERS.get(path.suffix)
    if not parser:
        raise ValueError(f"Unsupported format: {path.suffix}")
    return parser(path.read_text())
```

**Alternatives Evaluated**:
- ❌ Single format (Markdown only): Limits structured data use cases
- ❌ Single format (JSON only): Worse DX for human-readable documentation
- ❌ Binary formats (PDF, docx): Reduces version control benefits, harder to diff

---

### 3. Staff Role Validation

**Question**: How should staff role values be validated? Case-sensitive or case-insensitive?

**Research Findings**:
- **Case-Sensitive**: Matches industry API standards (AWS, Google Cloud), prevents typo masking, predictable behavior
- **Case-Insensitive**: More forgiving for user input, potential confusion (Person_1 vs person_1 both work)
- **Runtime Validation**: Check against exact enum values defined in spec
- **Performance**: O(1) hash lookup, negligible overhead

**Decision**: **Case-Sensitive Validation with Clear Error Messages**

**Rationale**:
- Aligns with spec clarification #1 (case-sensitive)
- Prevents "silent" failures where typos in role names succeed
- Standard practice in APIs (prevents ambiguity)
- Performance: Single O(1) set membership check
- Clear error handling: Tell user exact valid values if invalid

**Implementation**:
```python
from enum import Enum

class StaffRole(str, Enum):
    MANAGING_DIRECTOR = "person_1_managing_director"
    TEMP_CONSULTANT = "person_2_temp_consultant"
    RESOURCER_ADMIN = "person_3_resourcer_admin_tech"
    COMPLIANCE_WELLBEING = "person_4_compliance_wellbeing"
    FINANCE_TRAINING = "person_5_finance_training"

def validate_staff_role(role: str) -> bool:
    """Returns True if role is valid, raises ValueError with clear message if not."""
    try:
        StaffRole(role)  # O(1) lookup
        return True
    except ValueError:
        raise ValueError(
            f"Invalid staff_role '{role}'. "
            f"Valid values: {', '.join(r.value for r in StaffRole)}"
        )
```

**Alternatives Evaluated**:
- ❌ Case-insensitive: Could mask typos, less predictable behavior
- ❌ No validation: Leads to silent failures when directory not found

---

### 4. Resource Discovery & Loading Strategy

**Question**: How should agents discover and prioritize resources? Automatic scanning, explicit manifest, or agent-directed?

**Research Findings**:
- **Automatic Scanning (glob pattern)**: Simple, no metadata needed, works for small resource sets
- **Explicit Manifest**: Requires JSON/YAML file per role, adds metadata layer, rigidly controls order
- **Agent-Directed with Guide**: `resources-guide.md` provides navigation hints, agents decide what to load
- **Priority Ordering**: Can use filename prefix (01_, 02_) but less flexible for agent intelligence

**Decision**: **Agent-Directed with Optional resources-guide.md**

**Rationale**:
- Spec clarification #2: Agents load all resources, consult `resources-guide.md` if present
- Maximizes agent flexibility (can intelligently select subset of resources)
- Minimal boilerplate (guide file is optional)
- Extensible: Agents can evolve their resource selection strategy without file system changes
- Performance: All files discovered in single directory scan (300ms worst case)

**Implementation**:
```python
class ResourceLoader:
    def discover_resources(self, role: str) -> Dict[str, Path]:
        """Returns dict of {resource_name: path} for all files in role directory."""
        role_dir = self.base_path / role
        if not role_dir.exists():
            return {}  # Empty dict, graceful degradation

        return {
            f.stem: f  # Use filename without extension as key
            for f in role_dir.glob("*")
            if f.is_file() and f.name != "resources-guide.md"
        }

    def load_guide(self, role: str) -> Optional[str]:
        """Load optional resources-guide.md for agent navigation."""
        guide_path = self.base_path / role / "resources-guide.md"
        if guide_path.exists():
            return guide_path.read_text()
        return None

# Agent usage:
def process_query_with_specialisation(query: str, staff_role: str):
    resources = loader.discover_resources(staff_role)
    guide = loader.load_guide(staff_role)

    # Agent decides what to load based on query + guide
    relevant_resources = agent.select_relevant_resources(
        query=query,
        available_resources=resources,
        guide=guide
    )

    # Load only selected resources
    loaded = {k: loader.load_resource(resources[k]) for k in relevant_resources}

    # Enhance response with loaded context
    return agent.process_with_context(query, loaded)
```

**Alternatives Evaluated**:
- ❌ Manifest file (JSON/YAML): Adds metadata maintenance burden, more rigid
- ❌ Filename priority (01_, 02_): Works but less flexible for agent intelligence
- ❌ Database manifest: Adds infrastructure complexity

---

### 5. Resource Caching Strategy

**Question**: How should resources be cached? In-memory? Redis? TTL-based or persistent?

**Research Findings**:
- **In-Memory Dict**: Simple, fast (O(1) lookup), suitable for small resource sets (<1MB per role)
- **Redis**: Overkill for static files, adds network latency, distributed invalidation complexity
- **Python functools.lru_cache**: Built-in memoization, TTL not native, works for pure functions
- **Custom Cache with TTL**: Invalidate every N hours to catch file changes
- **No Cache**: Lazy load from disk, acceptable for <50 files/role

**Decision**: **In-Memory Cache with 1-Hour TTL**

**Rationale**:
- Resources are relatively static (changed infrequently)
- Small data set per role (<1MB estimated)
- 1-hour TTL catches file changes without constant reloads
- Thread-safe with Python's GIL for dict access
- Simple implementation, no external dependency
- Performance: First load ~300ms, cached loads ~1ms

**Implementation**:
```python
from time import time
from typing import Optional, Tuple

class CachedResourceLoader:
    def __init__(self, cache_ttl_seconds: int = 3600):
        self.cache = {}  # {role: (timestamp, resources_dict)}
        self.cache_ttl = cache_ttl_seconds

    def load_resources(self, role: str) -> Dict[str, Any]:
        now = time()

        # Check cache validity
        if role in self.cache:
            timestamp, cached = self.cache[role]
            if now - timestamp < self.cache_ttl:
                return cached  # Cache hit

        # Cache miss or expired - reload from disk
        resources = self._load_from_disk(role)
        self.cache[role] = (now, resources)
        return resources

    def invalidate(self, role: Optional[str] = None):
        """Manually invalidate cache (for testing/reloads)."""
        if role:
            self.cache.pop(role, None)
        else:
            self.cache.clear()
```

**Alternatives Evaluated**:
- ❌ No cache: Acceptable but slower (300ms per query with specialisation)
- ❌ Redis: Adds infrastructure, unnecessary latency for single-server setup
- ❌ Persistent in-memory (no TTL): Could miss file updates during long uptime

---

### 6. Error Handling & Graceful Degradation

**Question**: How should system behave when resources missing/corrupted? Fail query or continue without specialisation?

**Research Findings**:
- **Fail Immediately**: Hard error on bad input, fails spec requirement (FR-004: graceful handling)
- **Graceful Degradation**: Continue with agent execution, log warning, include note in response
- **Partial Load**: Load valid resources, skip corrupted ones, continue with subset
- **Fallback Chain**: Try to load, fail gracefully, offer user options

**Decision**: **Graceful Degradation with Detailed Logging**

**Rationale**:
- Spec requirement FR-004: "gracefully handle invalid or missing staff_role parameters"
- Spec requirement FR-006: "support empty staff role directories"
- User experience: Query should complete even if specialisation unavailable
- Observability: Log warnings so operators know when resources missing
- Response transparency: Include `staff_role_context` field indicating what was applied

**Implementation**:
```python
class SpecialisationManager:
    def get_specialisation_context(
        self,
        staff_role: Optional[str]
    ) -> Optional[SpecialisationContext]:
        """Load specialisation context, gracefully handle errors."""

        if not staff_role:
            return None  # No specialisation requested

        try:
            # Validate role
            validate_staff_role(staff_role)

            # Load resources
            resources = self.loader.load_resources(staff_role)
            guide = self.loader.load_guide(staff_role)

            return SpecialisationContext(
                staff_role=staff_role,
                resources=resources,
                guide=guide,
                status="loaded"
            )

        except ValueError as e:
            # Invalid role name
            logger.warning(f"Invalid staff_role: {staff_role} - {e}")
            return SpecialisationContext(
                staff_role=staff_role,
                resources={},
                guide=None,
                status="invalid_role"
            )

        except FileNotFoundError:
            # Role directory doesn't exist yet (expected during rollout)
            logger.info(f"Resources not yet available for role: {staff_role}")
            return SpecialisationContext(
                staff_role=staff_role,
                resources={},
                guide=None,
                status="no_resources"
            )

        except Exception as e:
            # Unexpected error (corruption, permissions, etc)
            logger.error(f"Error loading specialisation for {staff_role}: {e}")
            return SpecialisationContext(
                staff_role=staff_role,
                resources={},
                guide=None,
                status="error"
            )
```

**Alternatives Evaluated**:
- ❌ Hard failures: Would break existing query processing
- ❌ Silent failures: Operators wouldn't know about missing resources

---

### 7. Response Enhancement with Role Context

**Question**: How should agents incorporate role context into responses? Append notes, modify instructions, or use as context only?

**Research Findings**:
- **Context-Only**: Pass resources as context to agent, let it decide how to use
- **Instruction Injection**: Add system prompt hint about role context
- **Response Enhancement**: Agent generates response, decorator adds role notes
- **Selective Enhancement**: Different roles get different enhancement strategies

**Decision**: **Context-Only Approach (Resources as Agent Context)**

**Rationale**:
- Maximizes agent intelligence (can use resources as appropriate for query)
- No response modification needed (agents handle integration)
- Works with all agent types (not coupled to specific prompt format)
- Spec requirement FR-007: agents "incorporate relevant role-specific resources"
- Flexible: Agents evolve their use of resources over time
- Performance: No post-processing overhead

**Implementation**:
```python
class EnhancedAgentRequest:
    """Extended AgentRequest with optional specialisation context."""

    query: str
    user_id: str
    session_id: str
    staff_role: Optional[str] = None
    specialisation_context: Optional[SpecialisationContext] = None

    def get_context_prompt(self) -> str:
        """Generate optional context to include in agent prompt."""
        if not self.specialisation_context:
            return ""

        if self.specialisation_context.status != "loaded":
            return ""

        prompt = f"\nRole Context: You are assisting {self.staff_role}.\n"

        if self.specialisation_context.guide:
            prompt += f"Available Resources:\n{self.specialisation_context.guide}\n"

        return prompt

# Agent usage:
def process_with_specialisation(request: EnhancedAgentRequest):
    context_prompt = request.get_context_prompt()

    # Include context in agent's system prompt
    full_prompt = SYSTEM_PROMPT + context_prompt + request.query

    # Agent processes with full context
    response = agent.process(full_prompt)

    # Add metadata about specialisation
    response.metadata['staff_role_context'] = request.staff_role

    return response
```

**Alternatives Evaluated**:
- ❌ Response decoration: Adds complexity, harder to validate
- ❌ Instruction injection: Couples to specific prompt format

---

## Technology Stack Summary

### Core Technologies (No New Dependencies)
- **Python 3.11+**: Already in use in Chat Routing AI
- **pathlib**: Standard library, file system operations
- **json**: Standard library, JSON resource parsing
- **logging**: Standard library, error tracking
- **enum**: Standard library, StaffRole definition

### Optional (Future, if Needed)
- **PyYAML**: For YAML resource format support (not in MVP)
- **python-dotenv**: If resource paths become configurable
- **redis**: If distributed caching needed later (not in MVP)

### Testing Stack (Existing)
- **pytest**: Already used in Chat Routing AI tests
- **unittest.mock**: Mock file system for unit tests
- **hypothesis**: Property-based testing for resource discovery

---

## Key Assumptions

1. **Static Resources**: Staff role resources change infrequently (<1 time/week), TTL-based cache sufficient
2. **Small Scale**: Resource set per role stays <1MB, in-memory caching viable
3. **Backward Compatibility**: Existing agents don't require changes, specialisation is optional extension
4. **File System Permissions**: Server has read access to `specs/003-staff-specialisations/` directory
5. **Single Instance**: Caching assumes single-instance deployment (or cache invalidation coordinated)

---

## Open Questions Resolved

| Question | Resolution | Evidence |
|----------|-----------|----------|
| New dependencies? | No - use only stdlib | pathlib, json, logging available in Python 3.11+ |
| Performance impact? | <500ms initial, <10ms cached | File I/O + Python dict lookups |
| Backward compatibility? | Yes - optional parameter | Optional staff_role doesn't break existing queries |
| Resource management? | File system + 1hr cache | Aligns with spec, simple scaling |
| Concurrent access? | Safe via filesystem + GIL | Python dict thread-safe, file reads atomic |
| Future extensibility? | Yes - pluggable parsers | Parser.PARSERS architecture allows format additions |

---

## Recommendations for Phase 1 (Design)

1. **Data Model**: Define StaffRole enum with all 5 values and descriptions
2. **Contracts**: Specify SpecialisationManager, ResourceLoader, and Agent integration interfaces
3. **Directory Structure**: Create `specs/003-staff-specialisations/staff_specialisations/` with 5 role subdirectories (empty initially)
4. **Quickstart**: Document resource format guidelines, how to add new resources, testing procedures

---

**Document Version**: 1.0
**Created**: 2025-10-23
**Phase**: Phase 0 Complete ✅
**Status**: Ready for Phase 1 Design
