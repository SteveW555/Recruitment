# Staff Specialisations Feature - Specification

## Overview

The Staff Specialisations feature enables intelligent agents to be specialized for specific roles within the ProActive People organization. Each agent can receive an optional `staff_role` parameter that directs it to role-specific resources, allowing it to provide more contextually relevant and tailored assistance.

## Feature Structure

```
specs/003-staff-specialisations/
├── README.md (this file)
├── spec.md (comprehensive feature specification)
├── checklists/
│   └── requirements.md (quality validation checklist)

Staff Specialisation Resources/ (role resource directories)
├── person_1_managing_director/
├── person_2_temp_consultant/
├── person_3_resourcer_admin_tech/
├── person_4_compliance_wellbeing/
└── person_5_finance_training/
```

## The 5 Staff Roles

1. **Person 1 - Managing Director & Permanent Sales**
   - Responsibilities: Strategy, high-value permanent placements, key account management
   - Directory: `person_1_managing_director/`

2. **Person 2 - Temp Consultant & Contact Centre Specialist**
   - Responsibilities: High-volume temporary placements, contact centre consultancy, timesheet management
   - Directory: `person_2_temp_consultant/`

3. **Person 3 - Resourcer, Admin & Tech**
   - Responsibilities: Candidate sourcing, general administration, technology/systems management
   - Directory: `person_3_resourcer_admin_tech/`

4. **Person 4 - Compliance Officer & Wellbeing Specialist**
   - Responsibilities: Right-to-work verification, DBS checks, GDPR compliance, wellbeing support
   - Directory: `person_4_compliance_wellbeing/`

5. **Person 5 - Finance, Training & Assessment**
   - Responsibilities: Invoicing, payroll processing, training delivery, assessment coordination
   - Directory: `person_5_finance_training/`

## How It Works

### For Agents

When an agent receives a query with a `staff_role` parameter:

1. **Validation**: The agent validates the staff_role against the 5 defined roles
2. **Localization**: The agent locates the corresponding directory in `Staff Specialisation Resources/`
3. **Loading**: The agent loads any available resources from that directory
4. **Enhancement**: The agent incorporates role-specific context into its response
5. **Graceful Degradation**: If the staff_role is invalid or resources are missing, the agent continues normally

### For Users/Developers

To use staff specialisations:

```
Query Agent with parameters:
{
  "query": "How should I approach this complex hiring challenge?",
  "staff_role": "person_1_managing_director"
}

Agent returns:
{
  "response": "...[response incorporating managing director context]...",
  "staff_role_context": "person_1_managing_director"
}
```

## Resource Directories

Each staff role directory is initially empty and ready for resources to be added. Resources can include:

- **Guidelines**: Role-specific decision-making frameworks
- **Templates**: Documents, forms, or communication templates
- **Domain Knowledge**: Curated information relevant to the role
- **Training Materials**: Procedures, checklists, best practices
- **Reference Documents**: Industry standards, compliance guides

Resources can be in any format (markdown, text, JSON, etc.) that agents can parse.

## Key Features

✅ **Optional Parameters**: Queries work with or without staff_role specification
✅ **Graceful Errors**: Invalid staff roles don't crash the system
✅ **Empty Directories**: Works normally when directories have no resources
✅ **Extensible**: New resources can be added without code changes
✅ **Non-Blocking**: Resource loading is fast (<500ms target)
✅ **Concurrent Access**: Multiple agents can access resources simultaneously

## Success Criteria

- 100% query routing accuracy with valid staff roles
- <500ms resource retrieval latency
- Graceful handling of invalid staff roles
- No performance degradation without staff_role parameter
- 20%+ improvement in response relevance for role-specialized queries
- 100% of resources are relevant to the assigned role

## Next Steps

1. **Review the Specification**
   - Read `spec.md` for detailed requirements
   - Review acceptance scenarios and edge cases

2. **Proceed to Planning**
   - Use `/speckit.plan` to create implementation architecture
   - Generate tasks and timeline

3. **Add Resources**
   - Once code is implemented, add role-specific resources to directories
   - Example: training materials, guidelines, templates in each role directory

4. **Integration**
   - Integrate staff_specialisations into the chat routing AI system
   - Test with all 5 staff roles
   - Monitor performance and relevance improvements

## Related Documents

- **Staff Roles Definition**: `docs_project/Domain/STAFF_ROLES_AND_STRUCTURE.md`
- **Chat Routing AI**: `specs/002-chat-routing-ai/` (Parent system)
- **Specification**: `spec.md` (Full requirements)
- **Quality Checklist**: `checklists/requirements.md` (Validation results)

## Version History

| Version | Date | Status | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-23 | Draft | Initial specification created |

---

**Feature Branch**: `003-staff-specialisations`
**Created**: 2025-10-23
**Status**: Specification Complete ✅
