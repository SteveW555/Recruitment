# Data Model: Staff Specialisations

**Date**: 2025-10-23
**Feature**: Staff Specialisations (003-staff-specialisations)
**Phase**: Phase 1 - Design & Data Model

## Overview

Staff Specialisations extends the Chat Routing AI data model with role-specific resource containers and context. The data model includes:

1. **StaffRole Enum**: Define 5 organizational roles
2. **Resource Model**: Represent individual resource files
3. **SpecialisationContext**: Container for loaded resources and metadata
4. **AgentRequest Extensions**: Optional staff_role parameter
5. **AgentResponse Extensions**: Optional staff_role_context tracking

---

## Core Entities

### 1. StaffRole (Enum)

**Purpose**: Define the 5 authorized staff roles that can have specialisation resources.

**Definition**:
```python
from enum import Enum

class StaffRole(str, Enum):
    """5 ProActive People organizational roles with resource specialisations."""

    MANAGING_DIRECTOR = "person_1_managing_director"
    TEMP_CONSULTANT = "person_2_temp_consultant"
    RESOURCER_ADMIN_TECH = "person_3_resourcer_admin_tech"
    COMPLIANCE_WELLBEING = "person_4_compliance_wellbeing"
    FINANCE_TRAINING = "person_5_finance_training"
```

**Attributes**:
| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| value | str | "person_1_managing_director" | Case-sensitive, immutable |
| name | str | "MANAGING_DIRECTOR" | Python enum name (auto) |

**Validation Rules**:
- Must be one of 5 defined values
- Case-sensitive matching required (validated at runtime)
- No abbreviations or variations allowed

**Relationships**:
- Has-many: ResourceMetadata (each role has 0+ resources)
- Links-to: Directory in `Staff Specialisation Resources/{role}/`

**State Transitions**: None (static enum, values never change)

---

### 2. ResourceMetadata

**Purpose**: Represent metadata about a single resource file (path, type, format, etc).

**Definition**:
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from enum import Enum

class ResourceFormat(str, Enum):
    """Supported resource file formats."""
    MARKDOWN = "markdown"  # .md files
    JSON = "json"          # .json files
    TEXT = "text"          # .txt files
    GUIDE = "guide"        # resources-guide.md (special)

@dataclass
class ResourceMetadata:
    """Metadata about a role resource file."""

    name: str                    # Resource identifier (filename without ext)
    path: Path                   # Full file path
    format: ResourceFormat       # File format
    size_bytes: int             # File size
    is_guide: bool = False      # True if resources-guide.md
    created_at: float           # Unix timestamp
    updated_at: float           # Unix timestamp
    checksum: str = ""          # SHA-256 for change detection (optional)

    @property
    def relative_path(self) -> str:
        """Path relative to repo root for logging."""
        return str(self.path.relative_to(Path.cwd()))
```

**Attributes**:
| Attribute | Type | Example | Constraints |
|-----------|------|---------|-----------|
| name | str | "compliance_guidelines" | 1-100 chars, alphanumeric + underscore |
| path | Path | Path("specs/.../person_4_compliance_wellbeing/compliance_guidelines.md") | Must be readable |
| format | ResourceFormat | ResourceFormat.MARKDOWN | One of enum values |
| size_bytes | int | 4592 | 0 to 10MB |
| is_guide | bool | False | True only for resources-guide.md |
| created_at | float | 1698000000.5 | Unix timestamp |
| updated_at | float | 1698100000.5 | Unix timestamp, >= created_at |
| checksum | str | "a1b2c3d4..." | SHA-256 hex string (optional, for cache validation) |

**Validation Rules**:
- path must exist and be readable
- size_bytes must be ≤ 10MB
- updated_at ≥ created_at
- name must not contain path separators
- format must be one of supported formats

**Relationships**:
- Belongs-to: StaffRole (via directory structure)
- Loaded-by: ResourceLoader
- Cached-by: CachedResourceLoader

**Lifecycle**:
```
Created (file added to git)
  ↓
Discovered (resource loader scans directory)
  ↓
Loaded (parsed and cached)
  ↓
Used (agent consults resource)
  ↓
Evicted (cache TTL expired)
```

---

### 3. Resource

**Purpose**: Represent the parsed content of a resource file.

**Definition**:
```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Resource:
    """Parsed content of a resource file."""

    metadata: ResourceMetadata  # File metadata
    content: str               # Raw file content
    parsed: Dict[str, Any]     # Format-specific parsed data
    error: Optional[str] = None # Parse error if any

    @property
    def is_valid(self) -> bool:
        """True if resource loaded successfully."""
        return self.error is None
```

**Attributes**:
| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| metadata | ResourceMetadata | See above | File metadata |
| content | str | "# Compliance Guidelines\n..." | Raw file text |
| parsed | Dict[str, Any] | {"format": "markdown", "content": "..."} | Format-dependent |
| error | Optional[str] | "JSON decode error: ..." | None if valid |

**Parsed Content Formats**:

**Markdown Resources**:
```python
parsed = {
    "format": "markdown",
    "content": "# Title\nBody...",  # Full raw content
    "headings": ["Title", "Section 1", "Section 2"],  # Extracted headings
}
```

**JSON Resources**:
```python
parsed = {
    "format": "json",
    "data": {...}  # Parsed JSON object
}
```

**Plain Text Resources**:
```python
parsed = {
    "format": "text",
    "content": "Raw text content...",
    "lines": ["line1", "line2", ...]
}
```

**Validation Rules**:
- content must be valid UTF-8
- parsed must match format specification
- error should be set if parsing fails
- is_valid determines usability

---

### 4. SpecialisationContext

**Purpose**: Container for all specialisation information for a single query.

**Definition**:
```python
from typing import Optional, Dict
from enum import Enum

class SpecialisationStatus(str, Enum):
    """Status of specialisation context loading."""
    LOADED = "loaded"                # Successfully loaded
    INVALID_ROLE = "invalid_role"    # Staff role not found
    NO_RESOURCES = "no_resources"    # Role exists but no resources yet
    ERROR = "error"                  # Loading error
    NOT_REQUESTED = "not_requested"  # No staff_role parameter

@dataclass
class SpecialisationContext:
    """All specialisation information for a query."""

    staff_role: Optional[str]                    # Requested role
    resources: Dict[str, Resource]               # Loaded resources
    guide: Optional[str]                         # resources-guide.md content
    status: SpecialisationStatus = SpecialisationStatus.LOADED
    error_message: Optional[str] = None          # If status=ERROR
    loaded_at: float = field(default_factory=time)  # Timestamp
    resource_count: int = field(init=False)      # Convenience field

    def __post_init__(self):
        """Calculate derived fields."""
        self.resource_count = len(self.resources)

    def is_available(self) -> bool:
        """True if specialisation context is usable."""
        return self.status == SpecialisationStatus.LOADED and len(self.resources) > 0

    def is_error(self) -> bool:
        """True if loading failed."""
        return self.status in (SpecialisationStatus.ERROR, SpecialisationStatus.INVALID_ROLE)
```

**Attributes**:
| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| staff_role | Optional[str] | "person_1_managing_director" | Request parameter |
| resources | Dict[str, Resource] | {"compliance_guide": Resource(...)} | Loaded files |
| guide | Optional[str] | "# Resource Guide\n..." | Helper for agent |
| status | SpecialisationStatus | SpecialisationStatus.LOADED | Loading status |
| error_message | Optional[str] | "Role not found" | Error details if any |
| loaded_at | float | 1698000000.5 | When loaded |
| resource_count | int | 3 | Number of resources loaded |

**Derived Properties**:
- `is_available()`: True if loaded with resources
- `is_error()`: True if loading failed
- `resource_count`: Auto-calculated from resources dict

**Validation Rules**:
- If status=LOADED, resources must not be empty
- If status=ERROR, error_message must be set
- If status != LOADED, resources must be empty dict
- loaded_at must be recent (within last hour)

**Relationships**:
- Created-by: SpecialisationManager
- Used-by: Agent (for context)
- Included-in: AgentRequest

**Lifecycle**:
```
Request with staff_role
  ↓
SpecialisationManager loads context
  ↓
Returns SpecialisationContext (loaded/empty/error)
  ↓
Agent uses resources from context
  ↓
Response includes staff_role_context field
```

---

### 5. Extended AgentRequest

**Purpose**: ChatRouting AI AgentRequest extended with optional staff_role parameter.

**Current Definition** (from Chat Routing AI):
```python
@dataclass
class AgentRequest:
    query: str                              # User query
    user_id: str                            # User identifier
    session_id: str                         # Session identifier
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
```

**Extended Definition** (with Staff Specialisations):
```python
@dataclass
class AgentRequest:
    query: str                              # User query
    user_id: str                            # User identifier
    session_id: str                         # Session identifier
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    staff_role: Optional[str] = None        # NEW: Optional staff specialisation
    specialisation_context: Optional[SpecialisationContext] = None  # NEW: Loaded resources

    def has_specialisation(self) -> bool:
        """True if this request has specialisation context."""
        return (
            self.staff_role is not None
            and self.specialisation_context is not None
            and self.specialisation_context.is_available()
        )
```

**New Attributes**:
| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| staff_role | Optional[str] | "person_2_temp_consultant" | Request parameter, optional |
| specialisation_context | Optional[SpecialisationContext] | SpecialisationContext(...) | Populated by manager |

**Backward Compatibility**:
- staff_role defaults to None (optional)
- specialisation_context defaults to None (optional)
- Existing agents ignore these fields
- No breaking changes to existing code

---

### 6. Extended AgentResponse

**Purpose**: ChatRouting AI AgentResponse extended with staff_role_context tracking.

**Current Definition** (from Chat Routing AI):
```python
@dataclass
class AgentResponse:
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

**Extended Definition** (with Staff Specialisations):
```python
@dataclass
class AgentResponse:
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    staff_role_context: Optional[str] = None  # NEW: Which role was used

    def __post_init__(self):
        """Initialize metadata if None."""
        if self.metadata is None:
            self.metadata = {}
```

**New Attributes**:
| Attribute | Type | Example | Notes |
|-----------|------|---------|-------|
| staff_role_context | Optional[str] | "person_1_managing_director" | Tracking field |

**Metadata Fields Added**:
```python
metadata = {
    # Existing fields from Chat Routing AI
    "agent_latency_ms": 450,
    "routing_confidence": 0.92,

    # NEW: Staff Specialisations
    "staff_role_used": "person_2_temp_consultant",
    "specialisation_status": "loaded",
    "resources_consulted": 3,
}
```

**Backward Compatibility**:
- staff_role_context defaults to None (optional)
- Existing agents don't populate this field
- No breaking changes to existing code

---

## Data Relationships & Constraints

### Dependency Graph

```
StaffRole (enum, 5 values)
  ↓
  ├─→ ResourceMetadata (0+ per role)
  │     ↓
  │     └─→ Resource (parsed content)
  │
  └─→ Directory in Staff Specialisation Resources/{role}/

SpecialisationContext
  ├─→ staff_role: References one StaffRole value
  ├─→ resources: Dict of Resource objects
  └─→ guide: Content from resources-guide.md

AgentRequest
  ├─→ staff_role: Optional, references StaffRole if present
  └─→ specialisation_context: SpecialisationContext (if staff_role specified)

AgentResponse
  └─→ staff_role_context: References StaffRole value (if specialisation applied)
```

### Cardinality

| Relationship | Cardinality | Example |
|---|---|---|
| StaffRole to ResourceMetadata | 1 : 0..N | Person_1 has 0 to many resources |
| SpecialisationContext to Resource | 1 : 0..N | Context loads 0 to many resources |
| AgentRequest to StaffRole | 0..1 : 0..N | Request targets at most one role |
| AgentRequest to SpecialisationContext | 0..1 : 1 | Request has at most one context |

---

## State Transitions

### SpecialisationContext Lifecycle

```
NOT_REQUESTED (no staff_role parameter)
  ↓ (agent sets staff_role parameter)
  ↓
INVALID_ROLE (staff_role not in enum)
  └─→ (retry with valid role)
  ↓
NO_RESOURCES (role dir doesn't exist yet)
  └─→ (wait for resources to be added)
  ↓
LOADED (resources available)
  └─→ (agent uses resources)
  ↓
EXPIRED (cache TTL exceeded)
  └─→ (reload from disk)
  ↓
ERROR (file access/parse error)
  └─→ (agent continues without specialisation)
```

### Resource Lifecycle

```
File Created (added to Staff Specialisation Resources/{role}/)
  ↓
Discovered (resource loader scans directory)
  ↓
Loaded (parsed and cached in-memory)
  ↓
Used (agent consults resource)
  ↓
Evicted (cache TTL = 1 hour)
  ↓
File Modified (file on disk changed)
  └─→ (re-scan and reload on next query)
```

---

## Validation Rules Summary

| Entity | Field | Rule | Example |
|--------|-------|------|---------|
| StaffRole | value | One of 5 enum values | "person_1_managing_director" |
| ResourceMetadata | name | 1-100 chars, alphanumeric | "guidelines" |
| ResourceMetadata | path | Must be readable | Path("...") |
| ResourceMetadata | size_bytes | 0 to 10MB | 4592 |
| Resource | content | Valid UTF-8 | "# Title\n..." |
| Resource | parsed | Format-specific | JSON, markdown, text |
| SpecialisationContext | status | One of enum values | LOADED, ERROR, etc. |
| SpecialisationContext | resources | Dict of Resource | {} or {"name": Resource(...)} |
| AgentRequest | staff_role | None or valid enum value | "person_2_temp_consultant" |
| AgentResponse | staff_role_context | None or valid enum value | "person_1_managing_director" |

---

## Implementation Notes

### File-Based Storage Pattern

```
Staff Specialisation Resources/
├── person_1_managing_director/
│   ├── resources-guide.md                (Optional, special)
│   ├── decision_framework.md
│   ├── account_strategy.json
│   └── fee_benchmarks.json
│
├── person_2_temp_consultant/
│   ├── resources-guide.md
│   ├── temp_placement_guide.md
│   └── contact_centre_metrics.json
│
└── person_5_finance_training/
    ├── resources-guide.md
    ├── payroll_procedures.md
    └── training_templates.json
```

### Enum Usage in Code

```python
# Validation
if staff_role in StaffRole._value2member_map_:  # O(1) lookup
    role = StaffRole(staff_role)
else:
    raise ValueError(f"Invalid role: {staff_role}")

# Iteration
for role in StaffRole:
    print(f"Role: {role.value}")  # person_1_managing_director, etc.

# Directory mapping
role_dir = f"Staff Specialisation Resources/{staff_role}"
```

---

## Diagram: Data Model Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        STAFF SPECIALISATIONS DATA MODEL         │
└─────────────────────────────────────────────────────────────────┘

                        StaffRole (Enum)
                              │
                    ┌─────────┼─────────┐
                    │         │         │
          Person_1_MD   Person_2_Temp  ... Person_5_Finance
                    │         │         │
                    └────┬────┴────┬────┘
                         │        │
                   ┌─────▼────────▼──────┐
                   │ ResourceMetadata[]  │
                   │ (discovered files)  │
                   └─────┬────────┬──────┘
                         │        │
                    ┌────▼────┐┌──▼─────┐
                    │Resource ││ Guide  │
                    │(parsed) ││(text)  │
                    └────┬────┘└──┬─────┘
                         │       │
                    ┌────▼───────▼──────┐
                    │SpecialisationCtx  │
                    │ (all resources)    │
                    └─────┬──────────────┘
                          │
                    ┌─────▼────────────┐
                    │  AgentRequest    │
                    │ (+ staff_role)   │
                    └─────┬────────────┘
                          │ (agent processes)
                    ┌─────▼──────────────┐
                    │  AgentResponse     │
                    │ (+ staff_role_ctx) │
                    └────────────────────┘
```

---

**Document Version**: 1.0
**Created**: 2025-10-23
**Phase**: Phase 1 - Data Model ✅
**Status**: Ready for API Contract Design
