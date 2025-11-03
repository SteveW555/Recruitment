---
name: router
description: Expert in AI Router query classification and routing for recruitment automation. Specializes in analyzing queries, predicting routing decisions, debugging classification issues, and configuring the 7-category routing system (Information Retrieval, Data Operations, Problem Solving, Report Generation, Automation, Industry Knowledge, General Chat). Use this skill when debugging routing behavior, testing query classification, explaining category selection, or configuring routing parameters.
---

# AI Router Query Classification Expert

## Purpose

This skill provides expert guidance on the AI Router system's query classification and routing mechanism. It enables systematic analysis of user queries, prediction of routing decisions, debugging of unexpected classifications, and configuration of routing parameters.

The AI Router uses a 7-category classification system powered by Groq LLM (llama-3.3-70b-versatile) to intelligently route user queries to specialized agents.

## When to Use This Skill

Use this skill when:

- **Analyzing queries**: Determining which category a query should route to
- **Debugging routing**: Understanding why queries route to unexpected categories
- **Testing classification**: Validating routing decisions before deployment
- **Configuring the router**: Adjusting confidence thresholds, models, or category definitions
- **Improving query phrasing**: Optimizing queries for accurate classification
- **Understanding the system**: Learning how the routing system works
- **Staff specialization integration**: Routing queries with staff role context

## Core Concepts

### The 7 Categories

The router classifies all queries into one of seven predefined categories:

1. **INFORMATION_RETRIEVAL** (Priority: P1)
   - External information lookup from multiple sources
   - Examples: job boards, salaries, candidate searches, market trends

2. **DATA_OPERATIONS** (Priority: P1)
   - Internal system operations and data management
   - Examples: CRUD operations, database queries, system updates

3. **PROBLEM_SOLVING** (Priority: P2)
   - Complex business analysis with multi-step recommendations
   - Examples: root cause analysis, strategic planning, optimization

4. **REPORT_GENERATION** (Priority: P3)
   - Structured reports with visualizations and insights
   - Examples: dashboards, charts, performance reports, summaries

5. **AUTOMATION** (Priority: P2)
   - Workflow pipeline design and specifications
   - Examples: n8n workflows, Zapier integrations, process automation

6. **INDUSTRY_KNOWLEDGE** (Priority: P1)
   - UK recruitment domain expertise and compliance
   - Examples: GDPR, IR35, right-to-work, employment law

7. **GENERAL_CHAT** (Priority: P3)
   - Casual conversation and greetings
   - Examples: hellos, jokes, off-topic questions, fallback

### Classification Process

The GroqClassifier follows this process:

1. **Load agent definitions** from `config/agents.json`
2. **Build classification prompt** with category descriptions and examples
3. **Call Groq LLM** (llama-3.3-70b-versatile) with system + user prompts
4. **Parse JSON response** containing category, confidence, and reasoning
5. **Validate category** and convert to Category enum
6. **Check confidence threshold** (default: 0.55) to determine fallback
7. **Return RoutingDecision** with classification results and latency

### Key Configuration Parameters

- **confidence_threshold**: Minimum confidence for routing (default: 0.55)
- **routing_model**: Groq LLM model for classification (default: llama-3.3-70b-versatile)
- **temperature**: Temperature for routing decisions (default: 0.3)
- **max_tokens**: Maximum tokens for classification response (default: 200)

## How to Use This Skill

### Analyzing Queries

To analyze a query and predict its routing:

1. **Identify the intent**: What is the user trying to accomplish?
2. **Match against categories**: Which category's description best fits?
3. **Check example queries**: Does the query resemble existing examples?
4. **Consider staff context**: Is there a staff_role that provides additional context?
5. **Estimate confidence**: How clear is the intent? (Clear = 0.8+, Ambiguous = 0.5-0.7)

Example analysis workflow:

```
Query: "What are the current GDPR requirements for storing candidate data?"

Step 1: Intent - User wants regulatory compliance information
Step 2: Match - INDUSTRY_KNOWLEDGE (UK recruitment domain expertise)
Step 3: Examples - Similar to "What are the GDPR requirements?"
Step 4: Staff context - None provided
Step 5: Confidence - 0.92 (very clear regulatory query)

Expected routing: INDUSTRY_KNOWLEDGE (confidence: 0.92)
```

### Debugging Routing Issues

When queries route to unexpected categories:

1. **Review the query text**: Is the intent ambiguous?
2. **Check confidence score**: Low confidence (<0.65) triggers fallback to GENERAL_CHAT
3. **Examine the reasoning**: What did the classifier consider?
4. **Compare with examples**: Are example queries clear enough in `config/agents.json`?
5. **Test variations**: Try rephrasing the query for clarity
6. **Review staff context**: Does the staff_role affect routing?

Common issues and solutions:

- **Routes to GENERAL_CHAT unexpectedly**: Query may be too vague or confidence too low
  - Solution: Add more specific keywords or improve example queries

- **Confuses INFORMATION_RETRIEVAL and DATA_OPERATIONS**: Both involve data lookup
  - Solution: INFORMATION_RETRIEVAL = external sources, DATA_OPERATIONS = internal system

- **Low confidence on valid queries**: Category examples may be insufficient
  - Solution: Add more diverse example queries to `config/agents.json`

### Testing Classification

To test the router classification system, use the testing script:

```bash
# Test a single query
python .claude/skills/router/scripts/test_routing.py "What are the current salary ranges for developers?"

# Test with previous agent context
python .claude/skills/router/scripts/test_routing.py "Tell me more" --previous-agent INFORMATION_RETRIEVAL

# Test multiple queries from file
python .claude/skills/router/scripts/test_routing.py --file test_queries.txt
```

The script will output:
- Predicted category
- Confidence score
- Reasoning
- Classification latency
- Fallback status

### Configuring the Router

To adjust router behavior, modify these settings:

**Confidence Threshold** (in router initialization):
```python
# Lower threshold = more aggressive routing (may misclassify)
classifier = GroqClassifier(confidence_threshold=0.55)

# Higher threshold = more conservative (more fallback to GENERAL_CHAT)
classifier = GroqClassifier(confidence_threshold=0.75)
```

**Model Selection**:
```python
# Faster, less accurate
classifier = GroqClassifier(routing_model="llama-3-70b-8192")

# Slower, more accurate (default)
classifier = GroqClassifier(routing_model="llama-3.3-70b-versatile")
```

**Temperature**:
```python
# More deterministic (default)
classifier = GroqClassifier(temperature=0.3)

# More creative/varied (not recommended for routing)
classifier = GroqClassifier(temperature=0.7)
```

### Improving Query Phrasing

To optimize queries for accurate classification:

1. **Be specific**: "What's the salary?" → "What are current market salaries for Java developers in Bristol?"
2. **Use category keywords**: Include terms that appear in category descriptions
3. **Provide context**: Mention the business domain (recruitment, compliance, etc.)
4. **Avoid ambiguity**: "Get me data" is unclear; "Show me candidate pipeline report" is clear

**Examples of good query phrasing:**

| Category | Poor Query | Good Query |
|----------|-----------|------------|
| INFORMATION_RETRIEVAL | "salary info" | "What are current salary ranges for senior developers in London?" |
| DATA_OPERATIONS | "show data" | "List all active candidates in the database for the Java Developer role" |
| PROBLEM_SOLVING | "help with issue" | "Analyze why our placement rate dropped 15% this quarter and recommend solutions" |
| REPORT_GENERATION | "make report" | "Generate a quarterly performance report with placement metrics and trend charts" |
| AUTOMATION | "automate something" | "Design a workflow to automatically post jobs to Indeed and Totaljobs when approved" |
| INDUSTRY_KNOWLEDGE | "legal stuff" | "What are the IR35 off-payroll working regulations for contractor placements?" |
| GENERAL_CHAT | [Good as-is] | "Hello! How are you today?" |

### Staff Specialization Integration

The router supports staff role context for specialized routing:

**Available staff roles** (from `STAFF_ROLES_AND_STRUCTURE.md`):
1. `person_1_managing_director` - Strategic oversight, high-level decisions
2. `person_2_temp_consultant` - Temporary placement focus
3. `person_3_resourcer_admin_tech` - Administrative and technical support
4. `person_4_compliance_wellbeing` - Compliance, GDPR, employee wellbeing
5. `person_5_finance_training` - Finance, invoicing, training coordination

When a query includes staff role context, the router can:
- Access role-specific resources from `staff_specialisations/{role}/`
- Prioritize category interpretations relevant to that role
- Provide role-tailored responses

Example with staff context:
```python
decision = classifier.classify(
    query_text="What's our current compliance status?",
    query_id="query_123",
    staff_role="person_4_compliance_wellbeing"
)
# Expected: Routes to INDUSTRY_KNOWLEDGE with compliance-specific resources
```

## Reference Files

This skill includes detailed reference documentation:

- **`references/complete_system_architecture.md`**: Full system architecture, end-to-end flow, file locations, performance metrics ✨ NEW
- **`references/category_definitions.md`**: Complete category descriptions, decision trees, and extensive examples
- **`references/groq_classifier_implementation.md`**: Technical implementation details of the GroqClassifier
- **`references/configuration_guide.md`**: Comprehensive configuration and tuning guide
- **`references/staff_specialisations.md`**: Staff role integration and routing patterns

Load these references when:
- Need complete system architecture and flow → `complete_system_architecture.md` ⭐
- Need detailed technical implementation details → `groq_classifier_implementation.md`
- Need comprehensive category examples → `category_definitions.md`
- Configuring advanced routing parameters → `configuration_guide.md`
- Working with staff-role-specific routing → `staff_specialisations.md`

**See also**: `INFORMATION_RETRIEVAL_FLOW_GUIDE.md` (project root) for complete 12-step trace with code examples

## Scripts

### `scripts/test_routing.py`

Test query classification without running the full AI Router server.

**Usage:**
```bash
# Single query test
python scripts/test_routing.py "your query here"

# With previous agent context
python scripts/test_routing.py "follow-up query" --previous-agent INFORMATION_RETRIEVAL

# Batch test from file
python scripts/test_routing.py --file queries.txt

# Custom configuration
python scripts/test_routing.py "query" --threshold 0.7 --model llama-3-70b-8192
```

**Output:**
- Category prediction
- Confidence score (0.0-1.0)
- Reasoning explanation
- Classification latency (ms)
- Fallback status (triggered if confidence < threshold)

## Best Practices

1. **Always check confidence scores**: Low confidence (<0.65) indicates ambiguity
2. **Provide context in queries**: More context = better classification
3. **Use staff roles when relevant**: Staff context improves routing accuracy
4. **Monitor classification latency**: Target <500ms for production
5. **Regularly update example queries**: Keep `config/agents.json` current with real-world queries
6. **Test before deployment**: Validate routing decisions with `test_routing.py`
7. **Document routing issues**: Track misclassifications to improve the system

## Troubleshooting

**Problem**: All queries route to GENERAL_CHAT
- **Cause**: Groq API failure or invalid response
- **Solution**: Check Groq API key and connectivity, review error logs

**Problem**: Inconsistent routing for similar queries
- **Cause**: Temperature too high or insufficient example queries
- **Solution**: Lower temperature to 0.2-0.3, add more examples to config

**Problem**: Slow classification (>500ms)
- **Cause**: Model too large or network latency
- **Solution**: Use faster model (llama-3-70b-8192) or optimize prompt

**Problem**: Confuses related categories
- **Cause**: Category descriptions too similar
- **Solution**: Clarify category distinctions in classification prompt, add decision tree

## Example Workflows

### Workflow 1: Debugging a Misclassified Query

```
1. Run: python scripts/test_routing.py "the misclassified query"
2. Review: Check the predicted category and reasoning
3. Compare: Read category_definitions.md to understand expected category
4. Identify: Is the issue with query phrasing or category examples?
5. Fix: Either rephrase query or update config/agents.json examples
6. Validate: Re-test the query to confirm correct routing
```

### Workflow 2: Configuring for a New Use Case

```
1. Review: Read configuration_guide.md for available parameters
2. Test baseline: Run test_routing.py with default settings
3. Adjust: Modify confidence_threshold or temperature based on results
4. Validate: Test with representative queries from the new use case
5. Monitor: Track classification latency and accuracy over time
6. Iterate: Fine-tune parameters based on production data
```

### Workflow 3: Adding Staff Role Context

```
1. Identify: Determine which staff role is relevant
2. Review: Check staff_specialisations/ for available resources
3. Route: Pass staff_role parameter to classifier.classify()
4. Test: Verify routing uses role-specific context
5. Document: Update staff_specialisations.md with routing patterns
```

## Performance Targets

- **Classification latency**: <500ms (95th percentile)
- **Confidence threshold**: 0.65 (balance accuracy vs coverage)
- **Accuracy**: >90% on clear queries
- **Fallback rate**: <10% (queries routed to GENERAL_CHAT)

---

**Skill Version**: 1.0.0
**Last Updated**: 2025-01-01
**Maintained By**: ProActive People Development Team
