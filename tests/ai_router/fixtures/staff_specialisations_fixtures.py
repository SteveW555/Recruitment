"""
Test fixtures for Staff Specialisations feature.

Provides sample role directories, test resources, and test utilities
for unit and integration testing.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Tuple

import pytest


@pytest.fixture
def temp_staff_specialisations_dir() -> Tuple[Path, Dict[str, Path]]:
    """
    Create a temporary staff specialisations directory structure with sample resources.

    Returns:
        Tuple of (root_path, role_dirs)
        - root_path: Path to temp staff_specialisations directory
        - role_dirs: Dict mapping role names to their directories

    Usage:
        ```python
        def test_something(temp_staff_specialisations_dir):
            root_path, role_dirs = temp_staff_specialisations_dir
            person_1_dir = role_dirs['person_1_managing_director']
        ```
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "staff_specialisations"
        root.mkdir()

        role_names = [
            "person_1_managing_director",
            "person_2_temp_consultant",
            "person_3_resourcer_admin_tech",
            "person_4_compliance_wellbeing",
            "person_5_finance_training",
        ]

        role_dirs = {}
        for role_name in role_names:
            role_dir = root / role_name
            role_dir.mkdir()
            role_dirs[role_name] = role_dir

        yield root, role_dirs


@pytest.fixture
def sample_markdown_resource(temp_staff_specialisations_dir) -> Path:
    """
    Create a sample markdown resource file.

    Returns:
        Path to the created markdown file
    """
    root, role_dirs = temp_staff_specialisations_dir
    person_1_dir = role_dirs["person_1_managing_director"]

    content = """# Managing Director Decision Framework

## Strategic Planning
- Consider long-term business impact
- Evaluate market trends
- Assess resource allocation

## Key Account Management
- Maintain relationships with top clients
- Monitor account profitability
- Identify upsell opportunities

## Performance Metrics
- Revenue targets
- Client retention
- Team productivity
"""

    resource_file = person_1_dir / "decision_framework.md"
    resource_file.write_text(content, encoding="utf-8")
    return resource_file


@pytest.fixture
def sample_json_resource(temp_staff_specialisations_dir) -> Path:
    """
    Create a sample JSON resource file.

    Returns:
        Path to the created JSON file
    """
    root, role_dirs = temp_staff_specialisations_dir
    person_2_dir = role_dirs["person_2_temp_consultant"]

    data = {
        "contact_centre_metrics": {
            "average_handling_time": 450,
            "first_call_resolution": 0.85,
            "customer_satisfaction": 0.92,
        },
        "temp_placement_tiers": ["entry_level", "mid_level", "senior"],
        "billing_rates": {
            "entry_level": 12.50,
            "mid_level": 15.00,
            "senior": 18.00,
        },
    }

    resource_file = person_2_dir / "metrics.json"
    resource_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return resource_file


@pytest.fixture
def sample_text_resource(temp_staff_specialisations_dir) -> Path:
    """
    Create a sample plain text resource file.

    Returns:
        Path to the created text file
    """
    root, role_dirs = temp_staff_specialisations_dir
    person_3_dir = role_dirs["person_3_resourcer_admin_tech"]

    content = """Candidate Sourcing Checklist

1. Candidate Profile Review
   - Check experience matches job requirements
   - Verify technical skills
   - Assess cultural fit

2. Database Search
   - Use relevant keywords
   - Filter by location and availability
   - Check last contact date

3. Contact and Initial Screen
   - Introduce opportunity
   - Verify interest
   - Assess availability

4. Documentation
   - Log all interactions
   - Update candidate status
   - Create placement notes
"""

    resource_file = person_3_dir / "sourcing_checklist.txt"
    resource_file.write_text(content, encoding="utf-8")
    return resource_file


@pytest.fixture
def sample_resources_guide(temp_staff_specialisations_dir) -> Path:
    """
    Create a sample resources-guide.md file in a role directory.

    Returns:
        Path to the created guide file
    """
    root, role_dirs = temp_staff_specialisations_dir
    person_4_dir = role_dirs["person_4_compliance_wellbeing"]

    content = """# Resource Guide for Compliance & Wellbeing

This directory contains resources for the Compliance Officer & Wellbeing Specialist role.

## Resources

### GDPR Compliance (gdpr_guide.md)
Use for: Right-to-work verification, data retention, GDPR compliance questions
Relevance: HIGH - Use first for any compliance questions

### DBS Procedures (dbs_procedures.json)
Use for: DBS check processes, timelines, requirements
Relevance: MEDIUM - Reference for DBS-related queries

### Wellbeing Resources (wellbeing_support.txt)
Use for: Counseling, mental health, employee support programs
Relevance: MEDIUM - Use for wellbeing-related queries

## Selection Strategy

1. Always check GDPR guide first for compliance questions
2. Use DBS procedures for background check queries
3. Reference wellbeing resources for employee support questions
"""

    guide_file = person_4_dir / "resources-guide.md"
    guide_file.write_text(content, encoding="utf-8")
    return guide_file


@pytest.fixture
def empty_role_dir(temp_staff_specialisations_dir) -> Path:
    """
    Return path to an empty role directory (no resources).

    Returns:
        Path to person_5_finance_training directory (empty)
    """
    root, role_dirs = temp_staff_specialisations_dir
    return role_dirs["person_5_finance_training"]


__all__ = [
    "temp_staff_specialisations_dir",
    "sample_markdown_resource",
    "sample_json_resource",
    "sample_text_resource",
    "sample_resources_guide",
    "empty_role_dir",
]
