# API Contracts: Staff Specialisations

**Date**: 2025-10-23
**Feature**: Staff Specialisations (003-staff-specialisations)
**Phase**: Phase 1 - API Contracts & Interfaces

## Overview

This document defines the public interfaces and contracts for the Staff Specialisations module. These contracts specify how components interact and what guarantees each component provides.

---

## 1. SpecialisationManager Contract

**Purpose**: Orchestrate specialisation context loading and management.

**Location**: `utils/ai_router/staff_specialisations/specialisation_manager.py`

### Public Interface

```python
class SpecialisationManager:
    """Manages specialisation context for queries with staff role specification."""

    def __init__(self, loader: ResourceLoader):
        """Initialize manager with resource loader.

        Args:
            loader: ResourceLoader instance for file discovery and loading
        """
        pass

    def get_specialisation_context(
        self,
        staff_role: Optional[str]
    ) -> Optional[SpecialisationContext]:
        """Load specialisation context for a staff role.

        Args:
            staff_role: Optional staff role (one of 5 defined values)
                       If None, returns None

        Returns:
            SpecialisationContext with loaded resources and metadata
            None if staff_role is None
            SpecialisationContext with empty resources if role invalid/not found

        Raises:
            None (all errors handled gracefully)

        Example:
            >>> manager = SpecialisationManager(loader)
            >>> context = manager.get_specialisation_context("person_1_managing_director")
            >>> if context.is_available():
            ...     print(f"Loaded {context.resource_count} resources")
            ... else:
            ...     print(f"Status: {context.status}")

        Guarantees:
            - Always returns SpecialisationContext or None
            - Never raises exceptions (graceful error handling)
            - Invalid roles logged as warnings
            - Missing resources logged as info messages
            - Latency <500ms (first load), <10ms (cached)
        """
        pass

    def get_available_roles(self) -> List[str]:
        """Get list of all 5 available staff roles.

        Returns:
            List of valid staff role strings:
            [
                "person_1_managing_director",
                "person_2_temp_consultant",
                "person_3_resourcer_admin_tech",
                "person_4_compliance_wellbeing",
                "person_5_finance_training"
            ]

        Example:
            >>> roles = manager.get_available_roles()
            >>> print(f"Available roles: {', '.join(roles)}")

        Guarantees:
            - Always returns exactly 5 roles
            - Order consistent across calls
            - Values match StaffRole enum
        """
        pass

    def validate_staff_role(self, role: str) -> bool:
        """Validate if a staff role value is valid.

        Args:
            role: String to validate

        Returns:
            True if role is valid, False otherwise

        Raises:
            None (never raises, returns boolean)

        Example:
            >>> if manager.validate_staff_role("person_1_managing_director"):
            ...     context = manager.get_specialisation_context(role)

        Guarantees:
            - Case-sensitive validation
            - O(1) time complexity
            - No side effects
        """
        pass

    def clear_cache(self, role: Optional[str] = None) -> None:
        """Clear resource cache (useful for testing/reloads).

        Args:
            role: Specific role to clear (None = clear all)

        Returns:
            None

        Example:
            >>> manager.clear_cache("person_1_managing_director")  # Clear one role
            >>> manager.clear_cache()  # Clear all

        Guarantees:
            - Synchronous operation
            - Safe for concurrent calls
        """
        pass
```

### Error Handling

| Scenario | Behavior | Status Code |
|----------|----------|------------|
| staff_role = None | Returns None | (no error) |
| staff_role invalid format | Returns context with status=INVALID_ROLE | (no error) |
| Role directory missing | Returns context with status=NO_RESOURCES | (no error) |
| Resource file corrupted | Logs warning, skips resource, continues | (no error) |
| File permission error | Logs error, returns context with status=ERROR | (no error) |
| Cache access error | Clears cache, reloads from disk | (no error) |

### Performance Guarantees

| Operation | Latency Target | Typical | Notes |
|-----------|---|---|---|
| get_specialisation_context (first load) | <500ms | 300-400ms | File I/O + parsing |
| get_specialisation_context (cached) | <10ms | 1-5ms | In-memory dict lookup |
| get_available_roles | <1ms | <1ms | Return static list |
| validate_staff_role | <1ms | <1ms | O(1) enum lookup |

---

## 2. ResourceLoader Contract

**Purpose**: Load resources from file system with caching and error handling.

**Location**: `utils/ai_router/staff_specialisations/resource_loader.py`

### Public Interface

```python
class ResourceLoader:
    """Load staff role resources from file system with caching."""

    def __init__(
        self,
        base_path: Path = Path("specs/003-staff-specialisations/staff_specialisations"),
        cache_ttl_seconds: int = 3600
    ):
        """Initialize loader with base path and cache TTL.

        Args:
            base_path: Directory containing role subdirectories
            cache_ttl_seconds: Cache time-to-live in seconds (default 1 hour)

        Raises:
            ValueError: If base_path doesn't exist (log and continue with None)
        """
        pass

    def discover_resources(self, role: str) -> Dict[str, Path]:
        """Discover all resource files in a role directory.

        Args:
            role: Staff role identifier (e.g., "person_1_managing_director")

        Returns:
            Dict mapping resource name to file path:
            {
                "guideline": Path(".../compliance_guidelines.md"),
                "checklist": Path(".../right_to_work_checklist.md")
            }
            Empty dict if directory doesn't exist

        Raises:
            None (all errors handled gracefully)

        Example:
            >>> loader = ResourceLoader()
            >>> resources = loader.discover_resources("person_4_compliance_wellbeing")
            >>> print(f"Found {len(resources)} resources")
            >>> for name, path in resources.items():
            ...     print(f"  - {name}: {path}")

        Guarantees:
            - Returns empty dict, never raises
            - Only discovers readable files
            - Excludes resources-guide.md from results
            - File order consistent (alphabetical by name)
            - O(N) where N = number of files in directory
        """
        pass

    def load_guide(self, role: str) -> Optional[str]:
        """Load optional resources-guide.md for navigation.

        Args:
            role: Staff role identifier

        Returns:
            Markdown content of resources-guide.md if exists
            None if file doesn't exist or error reading

        Raises:
            None (all errors handled gracefully)

        Example:
            >>> guide = loader.load_guide("person_1_managing_director")
            >>> if guide:
            ...     print(f"Guide available:\n{guide}")

        Guarantees:
            - Returns None if guide doesn't exist
            - Cached separately from other resources
            - <100ms load time (file I/O only)
        """
        pass

    def load_resource(self, path: Path) -> Resource:
        """Load and parse single resource file.

        Args:
            path: Full path to resource file

        Returns:
            Resource object with metadata and parsed content

        Raises:
            None (all errors handled gracefully)

        Example:
            >>> resource = loader.load_resource(Path(".../guideline.md"))
            >>> if resource.is_valid:
            ...     print(f"Loaded {resource.metadata.name}")
            ... else:
            ...     print(f"Error: {resource.error}")

        Guarantees:
            - Always returns Resource object (never raises)
            - Format detection automatic based on file suffix
            - resource.is_valid indicates success
            - resource.error contains error message if failed
            - Supports .md, .json, .txt formats
            - <100ms per file (even if parsing fails)
        """
        pass

    def load_resources(self, role: str) -> Dict[str, Resource]:
        """Load all resources for a role (with caching).

        Args:
            role: Staff role identifier

        Returns:
            Dict mapping resource name to Resource object:
            {
                "guideline": Resource(...),
                "checklist": Resource(...)
            }
            Empty dict if directory doesn't exist or load fails

        Raises:
            None (all errors handled gracefully)

        Example:
            >>> resources = loader.load_resources("person_1_managing_director")
            >>> for name, resource in resources.items():
            ...     if resource.is_valid:
            ...         print(f"Loaded {name}")
            ...     else:
            ...         print(f"Failed to load {name}: {resource.error}")

        Guarantees:
            - Returns cache hit if TTL not expired (<10ms)
            - Reloads from disk if TTL expired or invalidated
            - Partial success: loads valid resources, skips invalid
            - resource.error set for failed resources
            - First load <500ms for typical role directory
            - O(N*M) where N = files, M = avg file size
        """
        pass

    def invalidate_cache(self, role: Optional[str] = None) -> None:
        """Manually invalidate cache (testing/reloads).

        Args:
            role: Specific role to invalidate (None = all roles)

        Returns:
            None

        Example:
            >>> loader.invalidate_cache("person_1_managing_director")  # Clear one
            >>> loader.invalidate_cache()  # Clear all

        Guarantees:
            - Synchronous operation
            - Safe for concurrent calls
            - Next load will refresh from disk
        """
        pass
```

### Supported Formats

| Format | Extension | Parsing | Example |
|--------|-----------|---------|---------|
| Markdown | .md | Text + heading extraction | `# Title\n...` |
| JSON | .json | json.loads() + validation | `{"data": {...}}` |
| Plain Text | .txt | Raw content | `Line 1\nLine 2...` |

### Error Handling

| Scenario | Behavior | resource.is_valid | resource.error |
|----------|----------|--|--|
| File doesn't exist | Returns Resource | False | "File not found" |
| Can't read file (permissions) | Returns Resource | False | "Permission denied" |
| Invalid UTF-8 | Returns Resource | False | "Invalid UTF-8" |
| JSON parse error | Returns Resource | False | "JSON decode error: ..." |
| Unknown format | Returns Resource | False | "Unsupported format" |
| File size > 10MB | Returns Resource | False | "File too large" |
| Successful parse | Returns Resource | True | None |

---

## 3. Validator Contract

**Purpose**: Validate staff roles and resource paths.

**Location**: `utils/ai_router/staff_specialisations/validators.py`

### Public Interface

```python
def validate_staff_role(role: str) -> bool:
    """Validate if role string is a valid staff role.

    Args:
        role: String to validate (should be one of 5 defined values)

    Returns:
        True if role is valid

    Raises:
        ValueError: With helpful message listing valid roles

    Example:
        >>> try:
        ...     validate_staff_role("person_1_managing_director")  # True
        ... except ValueError as e:
        ...     print(f"Invalid: {e}")
        ... # Prints: "Invalid staff_role 'person_1_managing_director'.
        ... #           Valid values: person_1_managing_director, ..."

    Guarantees:
        - Case-sensitive (must match exactly)
        - O(1) time complexity
        - Helpful error messages with list of valid values
    """
    pass

def validate_resource_path(path: Path) -> bool:
    """Validate if resource file path is valid.

    Args:
        path: File path to validate

    Returns:
        True if path is valid resource file

    Raises:
        ValueError: If path invalid with reason

    Example:
        >>> try:
        ...     validate_resource_path(Path(".../guideline.md"))
        ... except ValueError as e:
        ...     print(f"Invalid: {e}")

    Checks:
        - File exists
        - File is readable
        - File size < 10MB
        - File format supported
        - File location under specs/003-staff-specialisations/staff_specialisations/

    Guarantees:
        - All validations synchronous
        - Raises ValueError with specific failure reason
    """
    pass

def validate_resource_content(content: str) -> bool:
    """Validate if resource content is valid UTF-8.

    Args:
        content: String content to validate

    Returns:
        True if valid UTF-8

    Raises:
        ValueError: If not valid UTF-8

    Example:
        >>> try:
        ...     validate_resource_content(b"test".decode("utf-8"))
        ... except ValueError:
        ...     print("Invalid encoding")

    Guarantees:
        - No side effects
        - O(N) where N = content length
    """
    pass
```

### Validation Rules

| Rule | Check | Valid Example | Invalid Example |
|------|-------|---|---|
| Staff role | One of 5 enum values | "person_1_managing_director" | "person_99_invalid" |
| Case sensitivity | Exact case match | "person_1_managing_director" | "Person_1_Managing_Director" |
| File exists | Must be readable file | `Path(".../guide.md")` | `Path(".../missing.md")` |
| File size | Must be ≤ 10MB | 5000 bytes | 15000000 bytes |
| File format | .md, .json, or .txt | `resource.md` | `resource.pdf` |
| UTF-8 encoding | Valid UTF-8 | "Hello 😀" | Invalid bytes |
| Location | Under staff_specialisations/ | `specs/.../role/file.md` | `/etc/passwd` |

---

## 4. ContextBuilder Contract

**Purpose**: Build agent context from specialisation resources.

**Location**: `utils/ai_router/staff_specialisations/context_builder.py`

### Public Interface

```python
def build_context_prompt(context: SpecialisationContext) -> str:
    """Build prompt context from specialisation resources.

    Args:
        context: SpecialisationContext with loaded resources

    Returns:
        String to include in agent's system prompt
        Empty string if context not available

    Example:
        >>> context = manager.get_specialisation_context("person_1_managing_director")
        >>> prompt_addition = build_context_prompt(context)
        >>> full_prompt = SYSTEM_PROMPT + prompt_addition + user_query
        >>> response = agent.process(full_prompt)

    Returns:
        - If context available: "\nRole Context: You are assisting person_1_managing_director.\n..."
        - If no resources: ""
        - If error: ""

    Guarantees:
        - Always returns string (never None)
        - Never raises exceptions
        - Includes resources-guide.md if available
        - <50ms generation time
    """
    pass

def select_relevant_resources(
    query: str,
    available_resources: Dict[str, Path],
    guide: Optional[str] = None
) -> List[str]:
    """Select resources relevant to query.

    Args:
        query: User query
        available_resources: Dict of discovered resources
        guide: Optional resources-guide.md content

    Returns:
        List of resource names to load

    Example:
        >>> resources = loader.discover_resources("person_1_managing_director")
        >>> guide = loader.load_guide("person_1_managing_director")
        >>> selected = select_relevant_resources(query, resources, guide)
        >>> loaded = {k: loader.load_resource(resources[k]) for k in selected}

    Guarantees:
        - Returned names are subset of available_resources keys
        - Empty list if no resources available
        - <100ms selection time
    """
    pass

def build_metadata(
    context: SpecialisationContext
) -> Dict[str, Any]:
    """Build metadata for agent response.

    Args:
        context: SpecialisationContext

    Returns:
        Dict to merge into response.metadata:
        {
            "staff_role_used": "person_1_managing_director",
            "specialisation_status": "loaded",
            "resources_consulted": 3,
            "resource_names": ["guide1", "guide2", "guide3"]
        }

    Example:
        >>> metadata = build_metadata(context)
        >>> response.metadata.update(metadata)

    Guarantees:
        - Always returns dict (never None)
        - Key names consistent across calls
        - <10ms generation time
    """
    pass
```

---

## 5. Data Classes Contract

**Purpose**: Define data structures for specialisation system.

**Location**: `utils/ai_router/staff_specialisations/models.py`

### StaffRole Enum Contract

```python
class StaffRole(str, Enum):
    """5 organizational roles with resource specialisations."""

    MANAGING_DIRECTOR = "person_1_managing_director"
    TEMP_CONSULTANT = "person_2_temp_consultant"
    RESOURCER_ADMIN_TECH = "person_3_resourcer_admin_tech"
    COMPLIANCE_WELLBEING = "person_4_compliance_wellbeing"
    FINANCE_TRAINING = "person_5_finance_training"

    # Guarantees:
    # - Exactly 5 values (invariant)
    # - Value format: "person_N_description" (pattern)
    # - All enum values valid directory names (char constraints)
    # - Case-sensitive usage required
```

### SpecialisationContext Dataclass Contract

```python
@dataclass
class SpecialisationContext:
    """All specialisation data for a query."""

    staff_role: Optional[str]                # Request parameter
    resources: Dict[str, Resource]           # Loaded files
    guide: Optional[str]                     # Navigation help
    status: SpecialisationStatus            # Loading status
    error_message: Optional[str] = None      # Error details
    loaded_at: float = field(default_factory=time)

    # Guarantees:
    # - Immutable after creation
    # - All fields have sensible defaults
    # - is_available() returns True only when fully loaded
    # - is_error() returns True on load failures
```

### Resource Dataclass Contract

```python
@dataclass
class Resource:
    """Parsed content of a resource file."""

    metadata: ResourceMetadata              # File info
    content: str                            # Raw content
    parsed: Dict[str, Any]                  # Parsed data
    error: Optional[str] = None             # Parse error

    # Guarantees:
    # - immutable after creation
    # - is_valid property returns True if error is None
    # - parsed format matches metadata.format
```

---

## 6. Integration Contract with Chat Routing AI

**Purpose**: Define how Staff Specialisations integrates with existing router.

### Extended AgentRequest

```python
@dataclass
class AgentRequest:
    # Existing fields (from Chat Routing AI)
    query: str
    user_id: str
    session_id: str
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    # NEW fields (Staff Specialisations)
    staff_role: Optional[str] = None                        # Defaults to None
    specialisation_context: Optional[SpecialisationContext] = None  # Defaults to None

    # Guarantees:
    # - Backward compatible (new fields optional)
    # - Existing code ignores new fields
    # - New fields populated only if staff_role specified
```

### Extended AgentResponse

```python
@dataclass
class AgentResponse:
    # Existing fields (from Chat Routing AI)
    success: bool
    content: str
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    # NEW fields (Staff Specialisations)
    staff_role_context: Optional[str] = None  # Defaults to None

    # Guarantees:
    # - Backward compatible (new field optional)
    # - Existing code doesn't break
    # - Field populated only if specialisation was applied
```

### Router Integration Points

```python
# 1. Request enrichment (in router.route_query)
if request.staff_role:
    request.specialisation_context = \
        specialisation_manager.get_specialisation_context(request.staff_role)

# 2. Agent processing (existing, unchanged)
response = await agent.process(request)

# 3. Response enrichment (in router.route_query)
if request.specialisation_context:
    response.staff_role_context = request.staff_role
    response.metadata['staff_role_used'] = request.staff_role

# Guarantees:
# - No changes to existing agent.process() signature
# - Specialisation is optional, transparent layer
# - Existing agents work without changes
# - Response metadata documents specialisation applied
```

---

## Summary: Contract Guarantees

| Component | Key Guarantees |
|-----------|---|
| **SpecialisationManager** | Never raises, always returns result, <500ms latency |
| **ResourceLoader** | Partial success OK, caching enabled, graceful degradation |
| **Validators** | Case-sensitive matching, helpful error messages |
| **ContextBuilder** | Always returns strings/dicts, never None |
| **Data Classes** | Immutable after creation, sensible defaults |
| **Integration** | 100% backward compatible, transparent extension |

---

**Document Version**: 1.0
**Created**: 2025-10-23
**Phase**: Phase 1 - API Contracts ✅
**Status**: Ready for Implementation
