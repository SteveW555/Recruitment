# Router Skill - AI Query Classification Expert

Expert skill for AI Router query classification and routing in the ProActive People recruitment automation system.

## Overview

This skill provides comprehensive guidance on:
- Understanding the 7-category routing system
- Analyzing and predicting query routing decisions
- Debugging classification issues
- Configuring routing parameters
- Testing classification with staff role context

## Quick Start

### Using the Skill

Simply invoke the skill when you need help with routing:

```
User: "Why is this query routing to GENERAL_CHAT instead of INFORMATION_RETRIEVAL?"
```

The skill will help you:
1. Analyze the query intent
2. Explain the routing decision
3. Suggest improvements to query phrasing
4. Adjust configuration if needed

### Testing Classification

Use the test script to validate routing:

```bash
# Single query test
python .claude/skills/router/scripts/test_routing.py "What are current salaries for developers?"

# Batch test
python .claude/skills/router/scripts/test_routing.py --file .claude/skills/router/scripts/example_queries.txt

# With staff role context
python .claude/skills/router/scripts/test_routing.py "What are GDPR requirements?" --staff-role person_4_compliance_wellbeing
```

## The 7 Categories

1. **INFORMATION_RETRIEVAL** - External data lookup (salaries, job boards, market trends)
2. **DATA_OPERATIONS** - Internal CRUD operations on system data
3. **PROBLEM_SOLVING** - Complex analysis with strategic recommendations
4. **REPORT_GENERATION** - Structured reports with visualizations
5. **AUTOMATION** - Workflow pipeline design (n8n, Zapier, etc.)
6. **INDUSTRY_KNOWLEDGE** - UK recruitment regulations and best practices
7. **GENERAL_CHAT** - Casual conversation and fallback

## Documentation Structure

```
router/
├── SKILL.md                                    # Main skill instructions
├── README.md                                   # This file
├── references/                                 # Detailed reference docs
│   ├── category_definitions.md                # Complete category guide
│   ├── groq_classifier_implementation.md      # Technical implementation
│   ├── configuration_guide.md                 # Configuration tuning
│   └── staff_specialisations.md               # Staff role integration
└── scripts/
    ├── test_routing.py                        # Classification testing tool
    └── example_queries.txt                    # Sample test queries
```

## Common Use Cases

### Debugging Misclassifications

```
User: "Query 'get me data' is routing to GENERAL_CHAT but I expected DATA_OPERATIONS"
```

The skill will:
1. Analyze the query ("get me data" is too vague)
2. Explain why it routed to GENERAL_CHAT (confidence <0.65)
3. Suggest rephrasing: "List all candidates in the database for the Java Developer role"

### Configuring for New Requirements

```
User: "We need more queries to route to INDUSTRY_KNOWLEDGE. How do I adjust the configuration?"
```

The skill will:
1. Review current threshold and boost settings
2. Suggest lowering confidence_threshold or adding category boost
3. Provide configuration examples
4. Recommend testing approach

### Understanding Category Selection

```
User: "When should I use INFORMATION_RETRIEVAL vs DATA_OPERATIONS?"
```

The skill will:
1. Explain the key difference (external vs internal data)
2. Provide decision tree
3. Show example queries for each
4. Highlight common confusions

## Key Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| confidence_threshold | 0.65 | Minimum confidence for routing |
| routing_model | llama-3.3-70b-versatile | Groq model for classification |
| temperature | 0.3 | Temperature for routing decisions |

## Performance Targets

- **Classification latency**: <500ms (95th percentile)
- **Accuracy**: >90% on clear queries
- **Fallback rate**: 5-15% (queries routed to GENERAL_CHAT)

## Reference Documentation

For deep dives, load the reference files:

- **[category_definitions.md](references/category_definitions.md)** - Comprehensive category guide with 50+ examples, decision trees, and edge cases
- **[groq_classifier_implementation.md](references/groq_classifier_implementation.md)** - Technical implementation details, error handling, performance metrics
- **[configuration_guide.md](references/configuration_guide.md)** - Complete configuration tuning guide with examples
- **[staff_specialisations.md](references/staff_specialisations.md)** - Staff role integration and routing patterns

## Testing

Run the example queries to validate your routing configuration:

```bash
python scripts/test_routing.py --file scripts/example_queries.txt
```

Expected output:
- Category predictions for each query
- Confidence scores
- Reasoning explanations
- Classification latency
- Summary statistics

## Support

For questions or issues with routing:
1. Use this skill for guidance
2. Review the reference documentation
3. Test with `scripts/test_routing.py`
4. Check `utils/ai_router/groq_classifier.py` implementation

## Version

**Version**: 1.0.0
**Last Updated**: 2025-01-01
**Maintained By**: ProActive People Development Team
