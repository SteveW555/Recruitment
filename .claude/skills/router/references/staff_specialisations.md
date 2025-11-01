# Staff Specialisations Integration

Guide for integrating staff role context into AI Router query classification and routing.

## Overview

The AI Router supports staff role context to provide specialized routing based on the user's role within ProActive People. Each staff role has access to role-specific resources and may receive tailored routing decisions.

---

## Staff Roles

From `docs_project/Domain/STAFF_ROLES_AND_STRUCTURE.md`, ProActive People has 5 defined staff roles:

### 1. person_1_managing_director

**Primary Responsibilities:**
- Strategic oversight and high-level decision-making
- Business development and client relationships
- Company performance and growth strategy

**Typical Queries:**
- Executive reports and dashboards
- Strategic problem-solving
- High-level performance analytics
- Industry trends and competitive analysis

**Routing Preferences:**
| Category | Priority | Use Cases |
|----------|----------|-----------|
| REPORT_GENERATION | High | Executive dashboards, quarterly reports |
| PROBLEM_SOLVING | High | Strategic analysis, growth optimization |
| INFORMATION_RETRIEVAL | Medium | Market research, competitive intelligence |
| INDUSTRY_KNOWLEDGE | Medium | Industry trends, regulatory updates |

**Example Queries:**
- "Generate an executive dashboard showing Q4 performance across all divisions"
- "Analyze why our tech division revenue declined and recommend strategic solutions"
- "What are the current market trends in UK tech recruitment?"

---

### 2. person_2_temp_consultant

**Primary Responsibilities:**
- Temporary and contract placement management
- Candidate sourcing and screening
- Client relationship management for temp roles

**Typical Queries:**
- Candidate searches and availability
- Temp placement tracking
- Timesheet and hours management
- Client-specific temporary needs

**Routing Preferences:**
| Category | Priority | Use Cases |
|----------|----------|-----------|
| INFORMATION_RETRIEVAL | High | Candidate searches, availability checks |
| DATA_OPERATIONS | High | Update candidate status, placement records |
| AUTOMATION | Medium | Timesheet workflows, placement notifications |
| INDUSTRY_KNOWLEDGE | Medium | IR35 regulations, temp employment law |

**Example Queries:**
- "Find available temporary candidates for a 3-month admin role starting next week"
- "Update the status of temp placement #12345 to 'Extended'"
- "Design a workflow to automatically send weekly timesheet reminders to temp candidates"
- "What are the IR35 requirements for this contractor placement?"

---

### 3. person_3_resourcer_admin_tech

**Primary Responsibilities:**
- Administrative support and system operations
- Technical support for recruitment systems
- Data entry and database management

**Typical Queries:**
- System operations and database management
- Data imports/exports
- Technical troubleshooting
- System automation

**Routing Preferences:**
| Category | Priority | Use Cases |
|----------|----------|-----------|
| DATA_OPERATIONS | Very High | CRUD operations, data management |
| AUTOMATION | High | Workflow design, system integration |
| INFORMATION_RETRIEVAL | Medium | System data lookups |
| PROBLEM_SOLVING | Low | Technical issue analysis |

**Example Queries:**
- "Import candidate data from CSV file to database"
- "List all candidates who haven't been contacted in 30 days"
- "Design a workflow to sync Bullhorn data to our database every hour"
- "Why is the candidate import failing for records with special characters?"

---

### 4. person_4_compliance_wellbeing

**Primary Responsibilities:**
- GDPR compliance and data protection
- Regulatory compliance (IR35, right-to-work)
- Employee wellbeing and support
- Audit and policy enforcement

**Typical Queries:**
- GDPR compliance checks
- Regulatory guidance
- Compliance reporting
- Policy interpretation

**Routing Preferences:**
| Category | Priority | Use Cases |
|----------|----------|-----------|
| INDUSTRY_KNOWLEDGE | Very High | GDPR, IR35, employment law, compliance |
| REPORT_GENERATION | High | Compliance audit reports, GDPR reports |
| DATA_OPERATIONS | Medium | Candidate consent management, data deletion |
| PROBLEM_SOLVING | Medium | Compliance issue analysis |

**Example Queries:**
- "What are the GDPR requirements for storing candidate data for 12 months?"
- "Generate a compliance audit report showing all GDPR consent statuses"
- "Delete all candidate records older than 6 years as per our retention policy"
- "Analyze why we received GDPR complaints and recommend corrective actions"

**Special Routing Rules:**
- Queries from this role mentioning "GDPR", "IR35", "compliance", "regulations" → Strong boost to INDUSTRY_KNOWLEDGE
- Confidence boost: +0.1 for INDUSTRY_KNOWLEDGE category

---

### 5. person_5_finance_training

**Primary Responsibilities:**
- Financial operations and invoicing
- Commission calculations
- Training coordination and development
- Budget management

**Typical Queries:**
- Invoice generation
- Commission reports
- Financial analysis
- Training schedules

**Routing Preferences:**
| Category | Priority | Use Cases |
|----------|----------|-----------|
| REPORT_GENERATION | High | Financial reports, commission statements |
| DATA_OPERATIONS | High | Invoice creation, payment tracking |
| INFORMATION_RETRIEVAL | Medium | Financial data lookups |
| AUTOMATION | Medium | Invoicing workflows, payment reminders |

**Example Queries:**
- "Generate monthly commission report for all consultants"
- "Create invoice for client Acme Corp for 3 placements in December"
- "Show me all unpaid invoices older than 30 days"
- "Design a workflow to automatically send payment reminders for overdue invoices"

---

## Staff Specialisation Resources

Each staff role has a dedicated directory with role-specific resources:

```
staff_specialisations/
├── person_1_managing_director/
│   └── (strategic resources)
├── person_2_temp_consultant/
│   └── (temp placement resources)
├── person_3_resourcer_admin_tech/
│   └── (system/admin resources)
├── person_4_compliance_wellbeing/
│   └── (compliance resources)
└── person_5_finance_training/
    └── (finance resources)
```

**Resource types:**
- Industry best practices
- Template documents
- Regulatory guidelines
- Role-specific knowledge bases

---

## Routing with Staff Context

### Basic Usage

When a query includes staff role context:

```python
decision = classifier.classify(
    query_text="What are the GDPR requirements?",
    query_id="query_123",
    staff_role="person_4_compliance_wellbeing"  # Optional
)
```

### Routing Adjustments

When staff_role is provided, the router can:

1. **Boost category confidence** based on role preferences
2. **Access role-specific resources** from staff_specialisations/{role}/
3. **Prioritize categories** relevant to the role
4. **Apply role-specific routing rules**

**Example routing adjustment:**

```python
# Query: "What are the compliance requirements?"
# Without staff_role:
#   - INDUSTRY_KNOWLEDGE: 0.75 confidence

# With staff_role="person_4_compliance_wellbeing":
#   - INDUSTRY_KNOWLEDGE: 0.85 confidence (+0.10 boost)
#   - Reasoning includes: "Query from compliance role, boosting INDUSTRY_KNOWLEDGE"
```

---

## Configuration

### Staff Role Routing Configuration

In `config/agents.json`, you can configure staff role routing preferences:

```json
{
  "staff_role_preferences": {
    "person_1_managing_director": {
      "boost_categories": {
        "REPORT_GENERATION": 0.08,
        "PROBLEM_SOLVING": 0.08
      },
      "min_confidence_override": {
        "REPORT_GENERATION": 0.60
      }
    },
    "person_2_temp_consultant": {
      "boost_categories": {
        "INFORMATION_RETRIEVAL": 0.05,
        "DATA_OPERATIONS": 0.05
      }
    },
    "person_3_resourcer_admin_tech": {
      "boost_categories": {
        "DATA_OPERATIONS": 0.10,
        "AUTOMATION": 0.08
      }
    },
    "person_4_compliance_wellbeing": {
      "boost_categories": {
        "INDUSTRY_KNOWLEDGE": 0.10
      },
      "min_confidence_override": {
        "INDUSTRY_KNOWLEDGE": 0.55
      }
    },
    "person_5_finance_training": {
      "boost_categories": {
        "REPORT_GENERATION": 0.08,
        "DATA_OPERATIONS": 0.05
      }
    }
  }
}
```

**Fields:**
- `boost_categories`: Confidence boost (+0.0 to +0.15) for preferred categories
- `min_confidence_override`: Lower confidence threshold for specific categories

---

## Implementation

### GroqClassifier with Staff Context

**Updated classify() method signature:**
```python
def classify(
    self,
    query_text: str,
    query_id: str,
    previous_agent: Optional[str] = None,
    staff_role: Optional[str] = None  # NEW
) -> RoutingDecision:
```

**Implementation:**
```python
def classify(self, query_text, query_id, previous_agent=None, staff_role=None):
    # Build base classification prompt
    system_prompt = self._build_classification_prompt()

    # Add staff role context to user message
    user_message = query_text
    if staff_role:
        user_message = f"[Staff role: {staff_role}]\n{user_message}"
    if previous_agent:
        user_message = f"[Previous agent: {previous_agent}]\n{user_message}"

    # Call Groq for classification
    response = self.groq_client.complete(...)

    # Parse response
    result = self.groq_client.validate_json_response(response.content)
    category = Category.from_string(result["category"])
    confidence = result["confidence"]

    # Apply staff role boost
    if staff_role:
        boost = self._get_category_boost(staff_role, category)
        original_confidence = confidence
        confidence = min(1.0, confidence + boost)

        if boost > 0:
            result["reasoning"] += f" [Staff role {staff_role} boosted confidence by {boost:.2f}]"

    return RoutingDecision(...)
```

### Agent with Staff Resources

When an agent is invoked with staff role context:

```python
class IndustryKnowledgeAgent(BaseAgent):
    async def execute(self, query_text: str, staff_role: Optional[str] = None):
        # Load role-specific resources
        resources = []
        if staff_role:
            resources = self._load_staff_resources(staff_role)

        # Include resources in agent context
        context = f"""
        Role-specific resources:
        {chr(10).join(resources)}

        User query: {query_text}
        """

        # Process with LLM
        response = await self.llm.complete(context)
        return response

    def _load_staff_resources(self, staff_role: str) -> List[str]:
        resource_dir = f"staff_specialisations/{staff_role}/"
        if not os.path.exists(resource_dir):
            return []

        # Load all .md files from staff role directory
        resources = []
        for file in glob.glob(f"{resource_dir}/*.md"):
            with open(file, "r") as f:
                resources.append(f.read())

        return resources
```

---

## Use Cases

### Use Case 1: Compliance Query from Compliance Role

**Scenario:**
- User: person_4_compliance_wellbeing
- Query: "What are the data retention requirements?"

**Without staff context:**
```python
decision = classifier.classify(
    query_text="What are the data retention requirements?",
    query_id="q1"
)
# Result:
# - Category: INDUSTRY_KNOWLEDGE
# - Confidence: 0.78
```

**With staff context:**
```python
decision = classifier.classify(
    query_text="What are the data retention requirements?",
    query_id="q1",
    staff_role="person_4_compliance_wellbeing"
)
# Result:
# - Category: INDUSTRY_KNOWLEDGE
# - Confidence: 0.88 (+0.10 boost)
# - Reasoning: "Query about regulatory requirements. Staff role person_4_compliance_wellbeing boosted confidence by 0.10"
# - Agent accesses: staff_specialisations/person_4_compliance_wellbeing/gdpr_guidelines.md
```

### Use Case 2: Data Operation from Admin Role

**Scenario:**
- User: person_3_resourcer_admin_tech
- Query: "update candidate status"

**Without staff context:**
```python
decision = classifier.classify(
    query_text="update candidate status",
    query_id="q2"
)
# Result:
# - Category: DATA_OPERATIONS
# - Confidence: 0.72
```

**With staff context:**
```python
decision = classifier.classify(
    query_text="update candidate status",
    query_id="q2",
    staff_role="person_3_resourcer_admin_tech"
)
# Result:
# - Category: DATA_OPERATIONS
# - Confidence: 0.82 (+0.10 boost)
# - Reasoning: "CRUD operation on internal data. Staff role person_3_resourcer_admin_tech boosted confidence by 0.10"
```

### Use Case 3: Ambiguous Query with Role Context

**Scenario:**
- User: person_1_managing_director
- Query: "show me performance" (ambiguous)

**Without staff context:**
```python
decision = classifier.classify(
    query_text="show me performance",
    query_id="q3"
)
# Result:
# - Category: GENERAL_CHAT (fallback)
# - Confidence: 0.52 (below threshold)
# - Fallback: True
```

**With staff context:**
```python
decision = classifier.classify(
    query_text="show me performance",
    query_id="q3",
    staff_role="person_1_managing_director"
)
# Result:
# - Category: REPORT_GENERATION
# - Confidence: 0.60 (0.52 + 0.08 boost, meets min_confidence_override of 0.60)
# - Fallback: False
# - Reasoning: "Managing Director typically needs performance reports. Staff role person_1_managing_director boosted confidence by 0.08"
```

---

## Testing Staff Role Routing

### Test Script Usage

```bash
# Test with staff role context
python scripts/test_routing.py "What are GDPR requirements?" --staff-role person_4_compliance_wellbeing

# Compare routing with and without staff role
python scripts/test_routing.py "update data" --compare-staff-roles

# Test all queries from a staff role perspective
python scripts/test_routing.py --file queries.txt --staff-role person_2_temp_consultant
```

### Expected Behavior Validation

**Test cases:**

1. **Compliance query from compliance role** → INDUSTRY_KNOWLEDGE with boosted confidence
2. **Data operation from admin role** → DATA_OPERATIONS with boosted confidence
3. **Report request from managing director** → REPORT_GENERATION with boosted confidence
4. **Ambiguous query with role context** → Appropriate category (not GENERAL_CHAT)
5. **Off-topic query with role context** → GENERAL_CHAT (role doesn't override clear off-topic)

---

## Best Practices

1. **Always provide staff_role when available**
   - Improves routing accuracy
   - Enables access to role-specific resources
   - Reduces fallback rate

2. **Maintain role-specific resources**
   - Keep staff_specialisations/ directories updated
   - Add new resources as roles evolve
   - Document resource purpose and usage

3. **Monitor role-specific metrics**
   - Track routing accuracy by staff role
   - Identify role-specific misclassifications
   - Adjust boost values based on data

4. **Don't over-boost**
   - Keep boost values ≤0.15
   - Over-boosting can cause misclassifications
   - Use min_confidence_override sparingly

5. **Test role-specific routing**
   - Validate boost configurations
   - Test representative queries for each role
   - Ensure fallback still works for truly ambiguous queries

---

## Future Enhancements

1. **Dynamic role learning**
   - Learn role preferences from usage patterns
   - Auto-adjust boost values based on accuracy metrics

2. **Role-based agent selection**
   - Different agent implementations for different roles
   - Example: Compliance role gets extra GDPR validation in responses

3. **Multi-role queries**
   - Support queries from users with multiple roles
   - Combine routing preferences from multiple roles

4. **Role-based response formatting**
   - Tailor response detail level to role
   - MD gets executive summaries, Admin gets detailed data

---

**Version**: 1.0.0
**Last Updated**: 2025-01-01
**Staff Roles Reference**: `docs_project/Domain/STAFF_ROLES_AND_STRUCTURE.md`
