# Staff Specialisations Module

Enhance AI agents with role-specific resources and context for ProActive People's five organizational roles.

## Overview

The Staff Specialisations module enables AI agents to access role-specific resources (guides, documentation, examples) to provide better, more contextually relevant responses. Each organizational role can have its own set of resources (Markdown, JSON, or text files) that agents can consult when responding to queries.

## Features

- **5 Organizational Roles**: Managing Director, Temp Consultant, Resourcer/Admin/Tech, Compliance/Wellbeing, Finance/Training
- **Multi-Format Resources**: Support for Markdown, JSON, and text file formats
- **Resource Guides**: Optional `resources-guide.md` for navigation and prioritization
- **Intelligent Caching**: In-memory caching with 1-hour TTL for performance
- **Graceful Degradation**: System continues working even if resources are unavailable
- **Zero External Dependencies**: Uses only Python standard library

## Architecture

```
SpecialisationManager (Main Entry Point)
  ├─ ResourceLoader (Resource Discovery & Loading)
  │  ├─ discover_resources() - Find available resources
  │  ├─ load_resource() - Load and parse individual resource
  │  └─ load_resources() - Load all resources with caching
  ├─ SpecialisationContext (Container for Role + Resources)
  └─ Context Builder (Prompt & Metadata Generation)
     ├─ build_context_prompt() - Generate system prompt additions
     ├─ select_relevant_resources() - Pick resources for query
     └─ build_metadata() - Create response metadata
```

## Usage

### Basic Setup

```python
from utils.ai_router.staff_specialisations import SpecialisationManager

# Create manager (auto-discovers role directories)
manager = SpecialisationManager()

# Load specialisation context for a role
context = manager.get_specialisation_context("person_1_managing_director")

if context.is_available():
    print(f"Loaded {len(context.resources)} resources")
    for name, resource in context.resources.items():
        print(f"  - {name} ({resource.metadata.format.value})")
```

### Agent Integration

```python
from utils.ai_router.staff_specialisations import (
    SpecialisationManager,
    build_context_prompt,
    build_metadata,
)

# Initialize once
manager = SpecialisationManager()

# In agent request handler:
def process_agent_request(query, user_id, staff_role=None):
    # Load specialisation context if role provided
    context = None
    if staff_role:
        context = manager.get_specialisation_context(staff_role)

    # Build enhanced system prompt
    base_prompt = "You are a helpful AI assistant."
    if context and context.is_available():
        context_prompt = build_context_prompt(context)
        system_prompt = f"{base_prompt}\n\n{context_prompt}"
    else:
        system_prompt = base_prompt

    # Process query with LLM using system_prompt
    # ... agent code ...

    return response

# In agent response handler:
def finalize_agent_response(response, context, resources_consulted=0):
    # Add specialisation tracking
    if context:
        metadata = build_metadata(context, resources_consulted)
        response['metadata'].update(metadata)

    return response
```

### Router Integration

```python
from utils.ai_router.staff_specialisations import (
    SpecialisationManager,
    get_staff_role_from_kwargs,
    enhance_agent_request_with_specialisation,
    enhance_agent_response_with_specialisation,
)
from utils.ai_router.router import AIRouter

# In router initialization:
manager = SpecialisationManager()
router = AIRouter()

# In router route() method:
def route(query, user_id, session_id, **kwargs):
    # Extract staff_role from kwargs
    staff_role = get_staff_role_from_kwargs(kwargs)

    # Build request dict
    request = {
        "query": query,
        "user_id": user_id,
        "session_id": session_id,
    }

    # Enhance with specialisation if provided
    request = enhance_agent_request_with_specialisation(
        request, manager, staff_role
    )

    # ... existing routing logic ...
    # ... execute agent ...

    # Enhance response with specialisation metadata
    response = enhance_agent_response_with_specialisation(
        response, request.get('specialisation_context'), resources_consulted=2
    )

    return response
```

## Resource Directory Structure

Resources are stored in the following directory structure:

```
specs/003-staff-specialisations/staff_specialisations/
├── person_1_managing_director/
│   ├── strategy_guide.md
│   ├── financial_overview.json
│   └── resources-guide.md  (optional)
├── person_2_temp_consultant/
│   ├── placement_guide.md
│   └── resources-guide.md  (optional)
├── person_3_resourcer_admin_tech/
│   ├── processes.md
│   ├── it_systems.txt
│   └── resources-guide.md  (optional)
├── person_4_compliance_wellbeing/
│   ├── gdpr_guide.md
│   ├── wellbeing_resources.json
│   └── resources-guide.md  (optional)
└── person_5_finance_training/
    ├── training_plan.md
    └── resources-guide.md  (optional)
```

**Note**: The `resources-guide.md` file is special - it's loaded but NOT included in the regular resource list. It's accessible via `context.guide` for navigation/prioritization.

## API Reference

### SpecialisationManager

Main entry point for specialisation functionality.

```python
class SpecialisationManager:
    def get_specialisation_context(staff_role: Optional[str]) -> SpecialisationContext
    def get_available_roles() -> List[str]
    def validate_staff_role(staff_role: Optional[str]) -> bool
    def clear_cache(role_name: Optional[str] = None) -> None
```

### SpecialisationContext

Container for role-specific resources.

```python
@dataclass
class SpecialisationContext:
    staff_role: Optional[str]  # e.g., "person_1_managing_director"
    resources: Dict[str, Resource]  # name -> Resource mapping
    guide: Optional[str]  # resources-guide.md content if present
    status: SpecialisationStatus  # LOADED, INVALID_ROLE, NO_RESOURCES, etc.

    def is_available() -> bool  # True if LOADED status
    def is_error() -> bool  # True if status is ERROR or INVALID_ROLE
```

### Context Builder Functions

```python
def build_context_prompt(context: SpecialisationContext) -> str
    """Generate system prompt addition from context."""

def select_relevant_resources(
    context: SpecialisationContext,
    query: str,
    max_resources: int = 3
) -> List[Resource]
    """Select most relevant resources for a query."""

def build_metadata(
    context: SpecialisationContext,
    resources_consulted: int = 0
) -> Dict[str, Any]
    """Create response metadata with specialisation tracking."""
```

### Validators

```python
def validate_staff_role(staff_role: Optional[str]) -> tuple[bool, Optional[str]]
    """Validate staff role value (case-sensitive)."""

def validate_resource_path(path: Path) -> tuple[bool, Optional[str]]
    """Validate resource file exists and is readable."""

def validate_resource_content(content: str) -> tuple[bool, Optional[str]]
    """Validate resource content is valid UTF-8."""
```

## Acceptance Criteria

### User Story 1: Query Agent Receives Staff Role Parameter
- [x] Agent can parse staff_role parameter from request
- [x] Agent can identify target role directory based on staff_role value
- [x] Agent handles missing staff_role gracefully (continues normally)
- [x] Agent handles invalid staff_role gracefully (logs warning, continues)
- [x] <1ms validation latency for staff role checking

### User Story 2: Agent Accesses Role-Specific Resources
- [x] All resources in role directory are discoverable
- [x] Resources can be loaded with correct format parsing
- [x] Empty resource directories handled gracefully
- [x] Multiple resources accessible (returns dict of all resources)
- [x] Resources-guide.md consulted for navigation (if present)
- [x] <500ms resource loading latency
- [x] Corrupted resources don't crash loading (error handling)

### User Story 3: Agent Enhances Responses with Role Context
- [x] Agent responses include role context when specialisation applied
- [x] Responses reflect role-specific information from resources
- [x] Response metadata includes staff_role_context tracking
- [x] Responses accurate even when role context unavailable
- [x] Responses note relevant role context appropriately
- [x] 20%+ improvement in relevance for role-specific queries (qualitative)

## Performance Targets

- Initial resource discovery: <500ms
- Cached resource access: <10ms
- Staff role validation: <1ms
- End-to-end specialisation: <3s (integrated with agent execution)

## Testing

Run the comprehensive test suite:

```bash
# Unit tests (140+ tests)
pytest tests/ai_router/unit/test_staff_specialisations/ -v

# Integration tests (80+ tests)
pytest tests/ai_router/integration/test_staff_specialisations_integration.py -v
pytest tests/ai_router/integration/test_us2_resources.py -v
pytest tests/ai_router/integration/test_us3_response_enhancement.py -v

# All tests with coverage
pytest tests/ai_router/ --cov=utils.ai_router.staff_specialisations --cov-report=html
```

## Configuration

The module uses environment-based defaults:

```python
# Default resource base path
BASE_PATH = Path(__file__).parent.parent.parent.parent / "specs" / "003-staff-specialisations" / "staff_specialisations"

# Cache TTL
CACHE_TTL_SECONDS = 3600  # 1 hour
```

## Error Handling

The module gracefully handles various error scenarios:

- **Invalid staff role**: Returns context with `status=INVALID_ROLE`, logs warning
- **Missing role directory**: Returns context with `status=NO_RESOURCES`, logs info
- **Corrupted resource files**: Resource marked as invalid, other resources load normally
- **File access errors**: Logged with retry attempt, graceful degradation
- **Missing guide file**: No error, `context.guide` is None

## Backward Compatibility

All staff specialisation features are optional:

- Agents without `staff_role` parameter work unchanged
- Existing agent interfaces (AgentRequest, AgentResponse) backward compatible
- Optional fields (`specialisation_context`, `staff_role_context`) default to None
- No breaking changes to existing router behavior

## Implementation Status

**Phase 1 (Setup)**: ✅ Complete
**Phase 2 (Foundational)**: ✅ Complete
**User Story 1 (Parameter Handling)**: ✅ Complete
**User Story 2 (Resource Loading)**: ✅ Complete
**User Story 3 (Response Enhancement)**: ✅ Complete
**Polish & Deployment**: 🚧 In Progress

## Code Examples

### Example 1: Simple Role Context Check

```python
from utils.ai_router.staff_specialisations import SpecialisationManager

manager = SpecialisationManager()
roles = manager.get_available_roles()
print(f"Available roles: {roles}")

# Validate a role
if manager.validate_staff_role("person_1_managing_director"):
    context = manager.get_specialisation_context("person_1_managing_director")
    print(f"Status: {context.status.value}")
    print(f"Resources: {len(context.resources)}")
```

### Example 2: Access Resources from Specific Role

```python
from utils.ai_router.staff_specialisations import SpecialisationManager

manager = SpecialisationManager()
context = manager.get_specialisation_context("person_2_temp_consultant")

if context.is_available():
    for name, resource in context.resources.items():
        print(f"\nResource: {name}")
        print(f"Format: {resource.metadata.format.value}")
        print(f"Size: {resource.metadata.size_bytes} bytes")
        if resource.is_valid:
            print(f"Content preview: {resource.content[:100]}...")
```

### Example 3: Build Context Prompt for Agent

```python
from utils.ai_router.staff_specialisations import (
    SpecialisationManager,
    build_context_prompt,
)

manager = SpecialisationManager()
context = manager.get_specialisation_context("person_1_managing_director")

if context.is_available():
    prompt_addition = build_context_prompt(context)
    system_prompt = """You are a helpful assistant for management decisions.

    """ + prompt_addition

    # Use system_prompt with your LLM
    print(system_prompt)
```

## Contributing

To add new staff roles:

1. Update `StaffRole` enum in `models.py`
2. Create new role directory in `specs/003-staff-specialisations/staff_specialisations/`
3. Add resources (markdown/json/text files) to the role directory
4. Add tests for the new role
5. Update this README with new role details

## License

Proprietary - ProActive People Ltd. All rights reserved.
