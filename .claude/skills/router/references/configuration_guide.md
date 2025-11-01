# Configuration Guide for AI Router

Comprehensive guide for configuring and tuning the AI Router classification system.

## Configuration Files

### 1. config/agents.json

Main configuration file for all agents and their routing parameters.

**Structure:**
```json
{
  "CATEGORY_NAME": {
    "description": "Category description",
    "example_queries": ["query1", "query2", "query3"],
    "provider": "groq" or "anthropic",
    "model": "model-name",
    "temperature": 0.3,
    "max_tokens": 1000,
    "timeout_seconds": 2,
    "class_path": "utils.ai_router.agents.agent_module.AgentClass"
  }
}
```

**Example configuration:**
```json
{
  "INFORMATION_RETRIEVAL": {
    "description": "External information retrieval from multiple sources",
    "example_queries": [
      "What are current salary ranges for developers?",
      "Find job postings for accountants on Totaljobs",
      "What's the market demand for cloud architects?"
    ],
    "provider": "groq",
    "model": "llama-3-70b-8192",
    "temperature": 0.3,
    "max_tokens": 1000,
    "timeout_seconds": 2,
    "class_path": "utils.ai_router.agents.information_retrieval_agent.InformationRetrievalAgent"
  }
}
```

**Key fields:**

- **description**: Used in classification prompt to help LLM understand category
- **example_queries**: Included in classification prompt (up to 3 examples shown)
- **provider**: "groq" or "anthropic" (determines which LLM API to use)
- **model**: Model identifier for the provider
- **temperature**: LLM temperature for agent responses (0.0-1.0)
- **max_tokens**: Maximum tokens for agent responses
- **timeout_seconds**: Agent execution timeout
- **class_path**: Python import path to agent class

### 2. GroqClassifier Initialization Parameters

**In code:**
```python
classifier = GroqClassifier(
    config_path="config/agents.json",
    confidence_threshold=0.65,
    routing_model="llama-3.3-70b-versatile",
    temperature=0.3
)
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| config_path | str | "config/agents.json" | Path to agent config file |
| confidence_threshold | float | 0.65 | Minimum confidence for routing |
| routing_model | str | "llama-3.3-70b-versatile" | Groq model for classification |
| temperature | float | 0.3 | Temperature for routing decisions |

---

## Parameter Tuning Guide

### Confidence Threshold

Controls when queries fallback to GENERAL_CHAT.

**Default**: 0.65

**How it works:**
- If LLM returns confidence < threshold → Fallback to GENERAL_CHAT
- If LLM returns confidence ≥ threshold → Route to classified category

**Tuning guidelines:**

| Threshold | Behavior | Use Case |
|-----------|----------|----------|
| 0.50-0.55 | Very aggressive | Maximize routing, accept more errors |
| 0.60 | Aggressive | Prefer routing over fallback |
| 0.65 | Balanced | **Production default** |
| 0.70 | Conservative | Prioritize accuracy |
| 0.75-0.80 | Very conservative | Critical accuracy requirements |

**Metrics to monitor:**

```python
# Track fallback rate
fallback_rate = (queries_to_general_chat / total_queries) * 100

# Target: 5-15% fallback rate
if fallback_rate < 5%:
    # Consider raising threshold (may have misclassifications)
elif fallback_rate > 15%:
    # Consider lowering threshold (too many fallbacks)
```

**Example adjustment:**
```python
# If fallback rate is 20% (too high)
classifier = GroqClassifier(confidence_threshold=0.60)  # Lower from 0.65

# If fallback rate is 3% and seeing misclassifications
classifier = GroqClassifier(confidence_threshold=0.70)  # Raise from 0.65
```

---

### Routing Model Selection

Determines which Groq model is used for classification.

**Available models:**

| Model | Latency | Accuracy | Cost | Context |
|-------|---------|----------|------|---------|
| llama-3.3-70b-versatile | 200-500ms | High | Medium | 128K |
| llama-3-70b-8192 | 150-400ms | Medium | Low | 8K |
| mixtral-8x7b-32768 | 300-700ms | Medium | Low | 32K |

**Default**: llama-3.3-70b-versatile

**Selection criteria:**

1. **Production (default)**: llama-3.3-70b-versatile
   - Best balance of speed, accuracy, and cost
   - Recommended for most use cases

2. **High-volume / Cost-sensitive**: llama-3-70b-8192
   - 20-30% faster than versatile
   - Lower cost
   - Slightly lower accuracy acceptable

3. **Large context needs**: mixtral-8x7b-32768
   - If classification prompt + query exceeds 8K tokens
   - Rare for routing use cases

**Example:**
```python
# Production default
classifier = GroqClassifier(routing_model="llama-3.3-70b-versatile")

# Cost-optimized
classifier = GroqClassifier(routing_model="llama-3-70b-8192")

# Large context
classifier = GroqClassifier(routing_model="mixtral-8x7b-32768")
```

---

### Temperature

Controls randomness in LLM routing decisions.

**Default**: 0.3

**Range**: 0.0 - 1.0

**Guidelines:**

| Temperature | Behavior | Use Case |
|-------------|----------|----------|
| 0.0 | Fully deterministic | Testing, reproducibility |
| 0.1-0.2 | Highly deterministic | Production with strict consistency |
| 0.3 | Deterministic with slight variation | **Production default** |
| 0.4-0.5 | Balanced | Not recommended for routing |
| 0.6-1.0 | Creative/varied | **Never use for routing** |

**Recommendation**: Keep at 0.3 for production routing

Lower temperatures (0.0-0.2) can be used for testing to ensure fully deterministic results.

**Example:**
```python
# Production default (recommended)
classifier = GroqClassifier(temperature=0.3)

# Testing/reproducibility
classifier = GroqClassifier(temperature=0.0)

# NOT recommended for routing
classifier = GroqClassifier(temperature=0.7)  # ❌ Too random
```

---

## Agent-Specific Configuration

Each agent in `config/agents.json` has its own LLM configuration.

### Provider Selection

**Groq (Fast & Cost-Effective)**
- Use for: High-volume queries, fast responses
- Models: llama-3-70b-8192, llama-3.3-70b-versatile
- Cost: ~$0.50-0.79/1M tokens

**Anthropic (High-Quality Reasoning)**
- Use for: Complex analysis, strategic recommendations
- Models: claude-3-5-sonnet-20241022
- Cost: ~$3.00-15.00/1M tokens

**Configuration:**
```json
{
  "INFORMATION_RETRIEVAL": {
    "provider": "groq",
    "model": "llama-3-70b-8192"
  },
  "PROBLEM_SOLVING": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022"
  }
}
```

### Temperature by Category

Different categories may need different temperatures:

| Category | Temperature | Rationale |
|----------|-------------|-----------|
| INFORMATION_RETRIEVAL | 0.3 | Factual accuracy |
| DATA_OPERATIONS | 0.1 | Deterministic operations |
| PROBLEM_SOLVING | 0.4 | Creative analysis |
| REPORT_GENERATION | 0.3 | Structured output |
| AUTOMATION | 0.2 | Precise workflow specs |
| INDUSTRY_KNOWLEDGE | 0.2 | Regulatory accuracy |
| GENERAL_CHAT | 0.7 | Conversational variety |

**Configuration:**
```json
{
  "INDUSTRY_KNOWLEDGE": {
    "temperature": 0.2,
    "model": "llama-3.3-70b-versatile"
  },
  "GENERAL_CHAT": {
    "temperature": 0.7,
    "model": "llama-3-70b-8192"
  }
}
```

### Max Tokens by Category

Different categories generate different response lengths:

| Category | Max Tokens | Typical Response Length |
|----------|-----------|------------------------|
| INFORMATION_RETRIEVAL | 1000 | 300-800 words |
| DATA_OPERATIONS | 500 | 100-300 words |
| PROBLEM_SOLVING | 2000 | 800-1500 words |
| REPORT_GENERATION | 3000 | 1000-2500 words |
| AUTOMATION | 1500 | 500-1200 words |
| INDUSTRY_KNOWLEDGE | 1500 | 500-1200 words |
| GENERAL_CHAT | 300 | 50-200 words |

**Configuration:**
```json
{
  "REPORT_GENERATION": {
    "max_tokens": 3000
  },
  "GENERAL_CHAT": {
    "max_tokens": 300
  }
}
```

---

## Example Query Optimization

The quality of `example_queries` directly impacts classification accuracy.

### Best Practices

1. **Include 5-10 diverse examples per category**
   ```json
   "example_queries": [
     "What are current salary ranges for developers?",
     "Find job postings for accountants on Totaljobs",
     "What's the market demand for cloud architects?",
     "Show me all active job boards for tech recruitment",
     "What are typical interview questions for sales roles?"
   ]
   ```

2. **Cover different query styles**
   - Questions: "What are...", "How do I...", "Where can I find..."
   - Commands: "Find...", "Show me...", "Get..."
   - Statements: "I need...", "Looking for..."

3. **Include edge cases**
   ```json
   "example_queries": [
     "salary info for developers",  // Short, informal
     "What are the current market salary ranges for senior Java developers in the London area?",  // Long, formal
     "dev salaries?"  // Very short
   ]
   ```

4. **Update regularly with production queries**
   - Monitor misclassifications in production
   - Add real-world queries that were initially misclassified
   - Remove examples that don't represent typical usage

### Example Update Workflow

```bash
# 1. Identify misclassified queries from logs
SELECT query_text, predicted_category, actual_category
FROM routing_logs
WHERE predicted_category != actual_category
LIMIT 20;

# 2. Update config/agents.json with corrected examples
# Add misclassified queries to the correct category's example_queries

# 3. Test with updated configuration
python scripts/test_routing.py --file misclassified_queries.txt

# 4. Deploy updated configuration
# Restart AI Router server or hot-reload configuration
```

---

## Performance Tuning

### Latency Optimization

**Target**: <500ms classification latency (95th percentile)

**Optimization strategies:**

1. **Use faster model**
   ```python
   classifier = GroqClassifier(routing_model="llama-3-70b-8192")
   # 20-30% faster than llama-3.3-70b-versatile
   ```

2. **Reduce max_tokens**
   ```json
   {
     "temperature": 0.3,
     "max_tokens": 150  // Reduced from 200 for faster responses
   }
   ```

3. **Optimize prompt length**
   - Limit example_queries to 3 per category
   - Keep category descriptions concise

4. **Implement caching**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def cached_classify(query_text: str, query_id: str):
       return classifier.classify(query_text, query_id)
   ```

### Accuracy Monitoring

**Target**: >90% accuracy on clear queries

**Metrics to track:**

```python
# Classification accuracy
accuracy = correct_classifications / total_classifications

# Confidence distribution
avg_confidence_by_category = {
    category: mean(confidences)
    for category, confidences in category_confidences.items()
}

# Fallback rate
fallback_rate = fallback_count / total_queries

# Misclassification patterns
misclassifications_by_pair = {
    (predicted, actual): count
    for predicted, actual, count in misclassification_data
}
```

**Example monitoring dashboard:**
```
Overall Accuracy: 92.5%
Fallback Rate: 8.2%

By Category:
- INFORMATION_RETRIEVAL: 94% accuracy, avg confidence 0.87
- PROBLEM_SOLVING: 89% accuracy, avg confidence 0.81
- GENERAL_CHAT: 96% accuracy, avg confidence 0.92

Common Misclassifications:
- INFORMATION_RETRIEVAL → DATA_OPERATIONS: 12 cases
- AUTOMATION → PROBLEM_SOLVING: 8 cases
```

---

## Environment-Specific Configurations

### Development

```python
# Development configuration (fast iteration)
classifier = GroqClassifier(
    config_path="config/agents.dev.json",
    confidence_threshold=0.60,  # Lower threshold for more routing
    routing_model="llama-3-70b-8192",  # Faster model
    temperature=0.0  # Fully deterministic for testing
)
```

### Staging

```python
# Staging configuration (production-like)
classifier = GroqClassifier(
    config_path="config/agents.staging.json",
    confidence_threshold=0.65,  # Production setting
    routing_model="llama-3.3-70b-versatile",  # Production model
    temperature=0.3  # Production setting
)
```

### Production

```python
# Production configuration (optimized)
classifier = GroqClassifier(
    config_path="config/agents.json",
    confidence_threshold=0.65,
    routing_model="llama-3.3-70b-versatile",
    temperature=0.3
)
```

---

## Advanced Configuration

### Multi-Agent Routing

For complex queries that may need multiple agents:

```json
{
  "REPORT_GENERATION": {
    "allow_sub_agents": true,
    "sub_agent_categories": [
      "INFORMATION_RETRIEVAL",
      "DATA_OPERATIONS"
    ]
  }
}
```

This allows the Report Generation agent to call Information Retrieval and Data Operations agents as needed.

### Dynamic Confidence Thresholds

Adjust confidence threshold based on category:

```json
{
  "INFORMATION_RETRIEVAL": {
    "min_confidence": 0.70
  },
  "GENERAL_CHAT": {
    "min_confidence": 0.50
  }
}
```

**Implementation:**
```python
def should_route(decision: RoutingDecision, category_config: dict) -> bool:
    min_confidence = category_config.get("min_confidence", 0.65)
    return decision.primary_confidence >= min_confidence
```

### Fallback Chains

Configure fallback behavior when primary agent fails:

```json
{
  "INFORMATION_RETRIEVAL": {
    "fallback_chain": ["DATA_OPERATIONS", "GENERAL_CHAT"]
  }
}
```

### Staff Role Configuration

Configure staff-role-specific routing adjustments:

```json
{
  "staff_roles": {
    "person_4_compliance_wellbeing": {
      "boost_categories": ["INDUSTRY_KNOWLEDGE"],
      "boost_amount": 0.1
    }
  }
}
```

This boosts INDUSTRY_KNOWLEDGE confidence by 0.1 when queries come from the compliance role.

---

## Configuration Validation

Before deploying configuration changes, validate:

### 1. JSON Schema Validation

```bash
python scripts/validate_config.py config/agents.json
```

Checks:
- Valid JSON syntax
- Required fields present
- Valid category names
- Valid provider/model combinations

### 2. Example Query Testing

```bash
python scripts/test_routing.py --config config/agents.json --validate-examples
```

Tests that each category's example queries route correctly to that category.

### 3. Production Query Testing

```bash
python scripts/test_routing.py --config config/agents.json --file production_queries.txt
```

Tests configuration against real production queries.

---

## Troubleshooting Configuration Issues

### Issue: All queries route to GENERAL_CHAT

**Possible causes:**
1. Confidence threshold too high
2. Example queries not representative
3. Groq API failure

**Solutions:**
```python
# 1. Lower threshold
classifier = GroqClassifier(confidence_threshold=0.55)

# 2. Add more diverse examples to config/agents.json

# 3. Check Groq API status and logs
```

### Issue: Inconsistent routing for similar queries

**Possible causes:**
1. Temperature too high
2. Insufficient example queries
3. Category descriptions ambiguous

**Solutions:**
```python
# 1. Lower temperature
classifier = GroqClassifier(temperature=0.2)

# 2. Add 5+ diverse examples per category

# 3. Clarify category descriptions in config/agents.json
```

### Issue: High latency (>500ms)

**Possible causes:**
1. Model too large
2. Prompt too long
3. Network issues

**Solutions:**
```python
# 1. Use faster model
classifier = GroqClassifier(routing_model="llama-3-70b-8192")

# 2. Reduce example queries to 3 per category

# 3. Check Groq API latency and network
```

---

## Configuration Migration Guide

### Updating from Semantic Classifier to Groq Classifier

If migrating from semantic similarity classifier:

1. **Backup existing configuration**
   ```bash
   cp config/agents.json config/agents.backup.json
   ```

2. **Add example queries** to each category
   ```json
   {
     "INFORMATION_RETRIEVAL": {
       "example_queries": [
         "What are current salaries?",
         "Find job postings"
       ]
     }
   }
   ```

3. **Test both classifiers** side-by-side
   ```bash
   python scripts/compare_classifiers.py --semantic --groq
   ```

4. **Gradually roll out Groq classifier**
   - Start with 10% of traffic
   - Monitor accuracy and latency
   - Increase to 50%, then 100%

---

## Configuration Best Practices Checklist

- [ ] Use llama-3.3-70b-versatile for production routing
- [ ] Set confidence_threshold to 0.65 (adjust based on metrics)
- [ ] Set temperature to 0.3 for routing decisions
- [ ] Include 5-10 diverse example queries per category
- [ ] Configure appropriate max_tokens per category
- [ ] Use Groq for high-volume categories, Anthropic for complex reasoning
- [ ] Validate configuration before deployment
- [ ] Monitor accuracy, latency, and fallback rate
- [ ] Update example queries based on production data
- [ ] Test configuration changes in staging first

---

**Version**: 1.0.0
**Last Updated**: 2025-01-01
