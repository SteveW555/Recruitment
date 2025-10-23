# Quickstart Guide: Staff Specialisations

**Date**: 2025-10-23
**Feature**: Staff Specialisations (003-staff-specialisations)
**Phase**: Phase 1 - Quickstart & Implementation Guide

## Overview

This quickstart guide provides developers with everything needed to implement, test, and deploy the Staff Specialisations feature. Staff Specialisations extends the Chat Routing AI system by allowing agents to access role-specific resources and provide tailored responses for each of the 5 ProActive People organizational roles.

---

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Project Structure](#project-structure)
3. [Core Implementation](#core-implementation)
4. [Testing Strategy](#testing-strategy)
5. [Resource Management](#resource-management)
6. [Integration Steps](#integration-steps)
7. [Deployment](#deployment)
8. [Troubleshooting](#troubleshooting)

---

## Environment Setup

### Prerequisites

- Python 3.11 or later (already used by Chat Routing AI)
- Git (for version control)
- Access to ProActive People repository
- Existing Chat Routing AI infrastructure set up

### No New Dependencies Required

Staff Specialisations uses only Python standard library:
- `pathlib`: File system operations
- `json`: JSON resource parsing
- `enum`: StaffRole definition
- `logging`: Error tracking
- `dataclasses`: Data models
- `time`: Cache TTL tracking

### Installation

1. **Clone the repository** (if not already done):
```bash
git clone https://github.com/proactivepeople/recruitment-automation-system.git
cd recruitment-automation-system
```

2. **Check Python version**:
```bash
python --version  # Should be 3.11 or later
```

3. **No pip install needed** - Staff Specialisations uses only stdlib

### Directory Structure Verification

Verify that the staff specialisations directories exist:

```bash
ls -la Staff\ Specialisation\ Resources/

# Expected output:
# drwxr-xr-x  person_1_managing_director/
# drwxr-xr-x  person_2_temp_consultant/
# drwxr-xr-x  person_3_resourcer_admin_tech/
# drwxr-xr-x  person_4_compliance_wellbeing/
# drwxr-xr-x  person_5_finance_training/
```

---

## Project Structure

### Implementation Modules

```
utils/ai_router/staff_specialisations/          # NEW MODULE
├── __init__.py                                  # Package initialization
├── specialisation_manager.py                   # Main orchestrator
├── resource_loader.py                          # File discovery & loading
├── models.py                                   # Data classes (StaffRole, Resource, etc)
├── validators.py                               # Validation logic
└── context_builder.py                          # Response enhancement logic

tests/ai_router/
├── unit/test_staff_specialisations/
│   ├── test_resource_loader.py                 # Unit tests for file loading
│   ├── test_validators.py                      # Unit tests for validation
│   ├── test_context_builder.py                 # Unit tests for response building
│   └── test_specialisation_manager.py          # Unit tests for orchestration
├── integration/
│   └── test_staff_specialisations_integration.py  # End-to-end tests
└── fixtures/
    └── staff_specialisations_fixtures.py       # Shared test fixtures
```

### Resource Directories

```
Staff Specialisation Resources/

person_1_managing_director/
├── resources-guide.md              # Optional navigation guide
├── decision_framework.md            # Example: decision-making guide
├── account_strategy_template.md     # Example: strategy template
└── fee_benchmarks.json             # Example: benchmark data

person_2_temp_consultant/
├── resources-guide.md
├── temp_placement_guide.md
└── contact_centre_metrics.json

person_3_resourcer_admin_tech/
├── resources-guide.md
└── sourcing_best_practices.md

person_4_compliance_wellbeing/
├── resources-guide.md
├── right_to_work_checklist.md
└── compliance_requirements.json

person_5_finance_training/
├── resources-guide.md
├── payroll_procedures.md
└── training_roi_framework.json
```

---

## Core Implementation

### Phase 1: Data Models (models.py)

```python
# specs/003-staff-specialisations/data-model.md provides full details
# Key classes to implement:

1. StaffRole(Enum) - 5 defined roles
2. ResourceFormat(Enum) - markdown, json, text
3. ResourceMetadata - file metadata
4. Resource - parsed file content
5. SpecialisationContext - all resources for a query
```

### Phase 2: Validators (validators.py)

```python
def validate_staff_role(role: str) -> bool:
    """Validate staff role is one of 5 defined values."""
    # Check against StaffRole enum

def validate_resource_path(path: Path) -> bool:
    """Validate resource file is readable and under correct directory."""
    # Check: path exists, is file, size < 10MB, readable

def validate_resource_content(content: str) -> bool:
    """Validate resource content is valid UTF-8."""
    # Try decoding as UTF-8, raise if invalid
```

### Phase 3: Resource Loader (resource_loader.py)

```python
class ResourceLoader:
    """Load resources from file system with caching."""

    def __init__(self, base_path: Path, cache_ttl_seconds: int = 3600):
        self.base_path = base_path
        self.cache_ttl = cache_ttl_seconds
        self.cache = {}  # {role: (timestamp, resources_dict)}

    def discover_resources(self, role: str) -> Dict[str, Path]:
        """Find all resource files in a role directory."""
        # Glob pattern: {base_path}/{role}/*.{md,json,txt}

    def load_guide(self, role: str) -> Optional[str]:
        """Load optional resources-guide.md."""
        # Read file if exists, return None otherwise

    def load_resource(self, path: Path) -> Resource:
        """Parse single resource file based on format."""
        # Detect format from suffix, parse accordingly

    def load_resources(self, role: str) -> Dict[str, Resource]:
        """Load all resources for a role (with caching)."""
        # Check cache TTL, load from disk if expired
```

### Phase 4: Specialisation Manager (specialisation_manager.py)

```python
class SpecialisationManager:
    """Orchestrate specialisation context loading."""

    def __init__(self, loader: ResourceLoader):
        self.loader = loader

    def get_specialisation_context(
        self,
        staff_role: Optional[str]
    ) -> Optional[SpecialisationContext]:
        """Load all specialisation data for a query."""
        # 1. Validate staff_role
        # 2. Load resources
        # 3. Load guide
        # 4. Return SpecialisationContext with status

    def get_available_roles(self) -> List[str]:
        """List all 5 available roles."""
        # Return [r.value for r in StaffRole]
```

### Phase 5: Agent Integration

```python
# In existing agent code (router.py, agent base class):

async def process_with_specialisation(request: AgentRequest) -> AgentResponse:
    """Enhanced agent processing with staff specialisation."""

    # 1. Get specialisation context
    spec_context = specialisation_mgr.get_specialisation_context(
        request.staff_role
    )
    request.specialisation_context = spec_context

    # 2. Add context to prompt (if available)
    context_prompt = ""
    if spec_context and spec_context.is_available():
        context_prompt = build_context_prompt(spec_context)

    # 3. Process query with context
    response = await agent.process(request)

    # 4. Add metadata
    if spec_context:
        response.staff_role_context = request.staff_role
        response.metadata['staff_role_used'] = request.staff_role
        response.metadata['specialisation_status'] = spec_context.status.value

    return response
```

---

## Testing Strategy

### Unit Tests (test_*.py files)

**Test Resource Loader**:
```python
def test_discover_resources_empty_directory():
    """Test discovering resources in empty role directory."""
    # Setup: empty role dir
    # Call: discover_resources(role)
    # Expect: empty dict

def test_load_resource_markdown():
    """Test loading and parsing markdown resource."""
    # Setup: markdown file in role dir
    # Call: load_resource(path)
    # Expect: Resource with parsed["format"]="markdown"

def test_load_resource_json():
    """Test loading and parsing JSON resource."""
    # Setup: json file in role dir
    # Call: load_resource(path)
    # Expect: Resource with parsed["data"] = parsed JSON

def test_cache_ttl_expiration():
    """Test cache invalidation after TTL."""
    # Setup: Load resources (cache miss)
    # Call: load_resources(role) -> cached
    # Advance time past TTL
    # Call: load_resources(role) -> reload from disk

def test_invalid_resource_format():
    """Test handling of unsupported file format."""
    # Setup: .pdf file in role dir
    # Call: load_resource(path)
    # Expect: ValueError or graceful skip
```

**Test Validators**:
```python
def test_validate_staff_role_valid():
    """Test validation passes for valid role."""
    # Call: validate_staff_role("person_1_managing_director")
    # Expect: True

def test_validate_staff_role_case_sensitive():
    """Test validation is case-sensitive."""
    # Call: validate_staff_role("Person_1_Managing_Director")
    # Expect: ValueError

def test_validate_staff_role_invalid():
    """Test validation fails for unknown role."""
    # Call: validate_staff_role("person_99_invalid")
    # Expect: ValueError with list of valid values

def test_validate_resource_size_limit():
    """Test resource size validation (max 10MB)."""
    # Call: validate_resource_path(path_to_11mb_file)
    # Expect: ValueError
```

**Test Context Builder**:
```python
def test_build_context_prompt_with_guide():
    """Test prompt building with resources-guide.md."""
    # Setup: SpecialisationContext with guide
    # Call: build_context_prompt(context)
    # Expect: prompt includes guide content

def test_build_context_prompt_empty():
    """Test prompt building with no resources."""
    # Setup: SpecialisationContext with no resources
    # Call: build_context_prompt(context)
    # Expect: empty string or minimal prompt
```

### Integration Tests (test_*_integration.py)

```python
def test_end_to_end_with_staff_role():
    """Test full flow: request → specialisation → response."""
    # Setup: Agent with staff_role parameter
    # Call: process_with_specialisation(request)
    # Expect: response includes staff_role_context

def test_backward_compatibility_without_staff_role():
    """Test queries without staff_role still work."""
    # Setup: AgentRequest without staff_role
    # Call: process_with_specialisation(request)
    # Expect: response works normally (staff_role_context = None)

def test_graceful_degradation_invalid_role():
    """Test invalid staff_role doesn't crash."""
    # Setup: request with staff_role="invalid"
    # Call: process_with_specialisation(request)
    # Expect: response succeeds without specialisation

def test_multiple_resources_loaded():
    """Test loading all resources from a role directory."""
    # Setup: 3 resources in person_1_managing_director/
    # Call: get_specialisation_context("person_1_managing_director")
    # Expect: context.resources has 3 items
```

### Running Tests

```bash
# All tests
pytest tests/ai_router/

# Specific test file
pytest tests/ai_router/unit/test_staff_specialisations/test_resource_loader.py

# With coverage
pytest tests/ai_router/ --cov=utils/ai_router/staff_specialisations/

# Integration tests only
pytest tests/ai_router/integration/test_staff_specialisations_integration.py

# Verbose output
pytest -v tests/ai_router/unit/test_staff_specialisations/
```

---

## Resource Management

### Adding New Resources

1. **Create resource file** in appropriate role directory:
```bash
cd Staff\ Specialisation\ Resources/person_1_managing_director/
echo "# My Resource" > my_resource.md
```

2. **Create optional resources-guide.md** for navigation:
```markdown
# Resources Guide - Managing Director

## Available Resources

### my_resource.md
Description of what this resource contains and when to use it.

### account_strategy_template.md
Template for developing account strategies.

### fee_benchmarks.json
Industry fee benchmarks for different placement types.
```

3. **Verify discovery** (optional):
```python
from utils.ai_router.staff_specialisations import ResourceLoader
loader = ResourceLoader()
resources = loader.discover_resources("person_1_managing_director")
print(resources)  # Should include new file
```

4. **Commit to git**:
```bash
git add Staff\ Specialisation\ Resources/
git commit -m "docs: Add new resources for managing director role"
```

### Resource Format Guidelines

**Markdown Resources**:
```markdown
# Resource Title

## Section 1
Content...

## Section 2
More content...

### Subsection
Details...
```

**JSON Resources**:
```json
{
  "metadata": {
    "type": "benchmarks",
    "version": "1.0",
    "last_updated": "2025-10-23"
  },
  "data": {
    "placement_fees": {
      "permanent_perm": "15-22%",
      "temporary": "35-42%"
    }
  }
}
```

**Plain Text Resources**:
```
Simple text content
Line by line information
No special formatting
```

---

## Integration Steps

### Step 1: Add Module to AI Router

```python
# In utils/ai_router/__init__.py

from .staff_specialisations import (
    SpecialisationManager,
    ResourceLoader,
    StaffRole,
    SpecialisationContext,
)

__all__ = [
    "SpecialisationManager",
    "ResourceLoader",
    "StaffRole",
    "SpecialisationContext",
]
```

### Step 2: Extend AgentRequest

```python
# In utils/ai_router/models/agent_request.py

@dataclass
class AgentRequest:
    # ... existing fields ...
    staff_role: Optional[str] = None
    specialisation_context: Optional[SpecialisationContext] = None
```

### Step 3: Extend AgentResponse

```python
# In utils/ai_router/models/agent_response.py

@dataclass
class AgentResponse:
    # ... existing fields ...
    staff_role_context: Optional[str] = None
```

### Step 4: Initialize Manager in Router

```python
# In utils/ai_router/router.py

class AIRouter:
    def __init__(self, config: Dict[str, Any]):
        # ... existing initialization ...

        # NEW: Initialize specialisation
        self.resource_loader = ResourceLoader(
            base_path=Path("Staff Specialisation Resources")
        )
        self.specialisation_manager = SpecialisationManager(
            self.resource_loader
        )
```

### Step 5: Use in Routing Logic

```python
# In utils/ai_router/router.py

async def route_query(self, request: AgentRequest) -> AgentResponse:
    # ... existing routing logic ...

    # NEW: Load specialisation if requested
    if request.staff_role:
        request.specialisation_context = \
            self.specialisation_manager.get_specialisation_context(
                request.staff_role
            )

    # ... continue with agent execution ...
    response = await agent.process(request)

    # NEW: Add specialisation metadata to response
    if request.specialisation_context:
        response.staff_role_context = request.staff_role

    return response
```

---

## Deployment

### Pre-Deployment Checklist

- [ ] All unit tests pass (pytest tests/ai_router/unit/)
- [ ] All integration tests pass (pytest tests/ai_router/integration/)
- [ ] Code coverage ≥90%
- [ ] Documentation updated (README, docstrings)
- [ ] No new external dependencies
- [ ] Backward compatibility verified (queries without staff_role work)
- [ ] Performance validated (<500ms resource loading)
- [ ] Error handling tested (invalid roles, missing files, corrupted resources)

### Deployment Steps

1. **Create feature branch** (if not already done):
```bash
git checkout -b 003-staff-specialisations
```

2. **Implement all modules** (see Core Implementation above)

3. **Run full test suite**:
```bash
pytest tests/ai_router/ -v --cov=utils/ai_router/staff_specialisations/
```

4. **Create pull request**:
```bash
git add .
git commit -m "feat: Implement Staff Specialisations module

- Add StaffRole enum with 5 organizational roles
- Implement ResourceLoader with file discovery and caching
- Add SpecialisationManager for context orchestration
- Extend AgentRequest/AgentResponse with staff_role fields
- Add comprehensive unit and integration tests
- Maintain backward compatibility with existing agents
"

git push origin 003-staff-specialisations
# Create PR against master branch
```

5. **Code review** (merge when approved)

6. **Deploy to staging**:
```bash
# Run acceptance tests against staging
pytest tests/ai_router/integration/
```

7. **Deploy to production**:
```bash
# Run production validation
# Monitor error logs for first hour
# Verify <500ms latency targets met
```

### Rollback Plan

If issues found in production:

1. **Immediate**: Disable staff_role parameter acceptance
```python
# In router.py, temporarily:
request.staff_role = None
```

2. **Short-term**: Revert to previous version
```bash
git revert <commit-hash>
git push
```

3. **Root cause analysis**: Review error logs, fix issues
4. **Re-deploy**: After validation

---

## Troubleshooting

### Common Issues

**Issue: "ModuleNotFoundError: No module named 'staff_specialisations'"**

**Solution**: Check that utils/ai_router/staff_specialisations/__init__.py exists

```bash
ls -la utils/ai_router/staff_specialisations/__init__.py
```

---

**Issue: "Invalid staff_role 'person_1_managing_director' - case mismatch"**

**Solution**: Staff role parameter is case-sensitive. Use exact values:

```python
# WRONG (will fail):
request.staff_role = "Person_1_Managing_Director"

# CORRECT:
request.staff_role = "person_1_managing_director"
```

**Issue: "Resource directory not found" warning but query still works**

**Solution**: This is expected if role directory exists but is empty. No action needed.

```
INFO: Resources not yet available for role: person_1_managing_director
# This is fine - agent continues without specialisation
```

---

**Issue: "Resource file is corrupted or unreadable"**

**Solution**: Check file encoding and permissions:

```bash
# Verify UTF-8 encoding
file -b specs/003-staff-specialisations/staff_specialisations/*/resource.md

# Fix permissions
chmod 644 specs/003-staff-specialisations/staff_specialisations/*/\*.md
```

---

**Issue: Cache not updating after adding new resource**

**Solution**: Cache has 1-hour TTL. Either:

1. Wait 1 hour for automatic refresh
2. Restart application to clear cache
3. Access cache directly to invalidate:
```python
specialisation_manager.resource_loader.invalidate("person_1_managing_director")
```

---

### Performance Troubleshooting

**Latency target: <500ms for resource loading**

Monitor with metrics:
```python
import time

start = time.time()
context = specialisation_manager.get_specialisation_context("person_1_managing_director")
elapsed = (time.time() - start) * 1000
print(f"Resource loading: {elapsed:.1f}ms")
```

If exceeding target:
- Check file count in role directory (should be <20)
- Verify disk I/O performance
- Check if cache is working (repeated calls should be <10ms)

---

## Summary

Staff Specialisations is a lightweight extension to Chat Routing AI that:

✅ Requires no new external dependencies
✅ Maintains backward compatibility
✅ Gracefully handles missing/invalid resources
✅ Achieves <500ms resource loading latency
✅ Integrates cleanly with existing agents

**Next Steps**:
1. Review all implementation modules
2. Run complete test suite
3. Deploy to staging
4. Add initial resources (later phase)
5. Monitor production metrics

---

**Document Version**: 1.0
**Created**: 2025-10-23
**Phase**: Phase 1 - Quickstart ✅
**Status**: Ready for Implementation
