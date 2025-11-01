# GroqClassifier Implementation Reference

Technical deep-dive into the GroqClassifier implementation for query classification and routing.

## Architecture Overview

```
User Query
    ↓
GroqClassifier.classify()
    ↓
1. Build Classification Prompt (system + user messages)
    ↓
2. Call Groq LLM (llama-3.3-70b-versatile)
    ↓
3. Parse JSON Response
    ↓
4. Validate Category & Confidence
    ↓
5. Return RoutingDecision
```

---

## Class: GroqClassifier

**Location**: `utils/ai_router/groq_classifier.py`

### Initialization

```python
def __init__(
    self,
    config_path: str = "config/agents.json",
    confidence_threshold: float = 0.65,
    routing_model: str = "llama-3.3-70b-versatile",
    temperature: float = 0.3,
):
```

**Parameters:**
- `config_path`: Path to agent configuration file (default: `config/agents.json`)
- `confidence_threshold`: Minimum confidence for non-fallback routing (default: 0.65)
- `routing_model`: Groq model to use for classification (default: llama-3.3-70b-versatile)
- `temperature`: LLM temperature for routing decisions (default: 0.3)

**Initialization Steps:**

1. **Initialize Groq client**
   ```python
   self.groq_client = GroqClient()
   ```

2. **Load agent definitions** from `config/agents.json`
   ```python
   self._load_agent_definitions()
   ```
   - Reads JSON configuration
   - Converts to agent definition dictionaries
   - Validates Category enum values
   - Stores in `self.available_agents`

**Example `config/agents.json` structure:**
```json
{
  "INFORMATION_RETRIEVAL": {
    "description": "External information retrieval from multiple sources",
    "example_queries": [
      "What are current salary ranges for developers?",
      "Find job postings for accountants on Totaljobs"
    ],
    "provider": "groq",
    "model": "llama-3-70b-8192"
  }
}
```

---

## Core Method: classify()

```python
def classify(
    self,
    query_text: str,
    query_id: str,
    previous_agent: Optional[str] = None
) -> RoutingDecision:
```

**Parameters:**
- `query_text`: The user's query to classify
- `query_id`: Unique identifier for this query (for tracking/logging)
- `previous_agent`: Optional previous agent name for context-aware routing

**Returns:**
- `RoutingDecision` object containing:
  - `query_id`: The query identifier
  - `primary_category`: The classified Category enum
  - `primary_confidence`: Confidence score (0.0-1.0)
  - `reasoning`: Explanation of classification decision
  - `classification_latency_ms`: Time taken for classification
  - `fallback_triggered`: Boolean indicating if confidence < threshold

### Step-by-Step Process

#### Step 1: Build Classification Prompt

```python
system_prompt = self._build_classification_prompt()
```

The system prompt includes:
- **Task description**: "You are a query classification system..."
- **Category descriptions**: All 7 categories with descriptions and examples
- **Instructions**: How to analyze queries and respond
- **Response format**: JSON schema with category, confidence, reasoning
- **Guidelines**: Specific routing rules and edge cases

**Example system prompt structure:**
```
You are a query classification system for a recruitment agency AI assistant.

Your task is to analyze user queries and classify them into ONE of the following categories:

- **INFORMATION_RETRIEVAL**: External information retrieval from multiple sources
  Examples: "What are current salaries?", "Find job postings"

- **DATA_OPERATIONS**: Internal system operations and data management
  Examples: "Add candidate to database", "Update job status"

...

**Response Format (JSON only):**
{
    "category": "CATEGORY_NAME",
    "confidence": 0.85,
    "reasoning": "Brief explanation"
}

**Guidelines:**
- If unclear or casual greeting/chat, use GENERAL_CHAT
- For queries about finding information, use INFORMATION_RETRIEVAL
- For complex problem analysis, use PROBLEM_SOLVING
...
```

#### Step 2: Prepare User Message

```python
user_message = query_text
if previous_agent:
    user_message = f"[Previous agent: {previous_agent}]\n\nQuery: {query_text}"
```

**Context-aware routing:**
- If `previous_agent` is provided, it's prepended to the query
- This helps the LLM understand conversation flow
- Example: If previous agent was INFORMATION_RETRIEVAL and query is "tell me more", the LLM knows to continue with INFORMATION_RETRIEVAL

#### Step 3: Call Groq LLM

**Current Implementation (Updated):**
```python
from utils.groq.groq_client import CompletionConfig

config = CompletionConfig(
    model=self.routing_model,
    temperature=self.temperature,
    max_tokens=200
)

response = self.groq_client.complete(
    prompt=user_message,
    system_prompt=system_prompt,
    config=config
)
```

**Key parameters:**
- `model`: llama-3.3-70b-versatile (default)
- `temperature`: 0.3 (deterministic routing)
- `max_tokens`: 200 (sufficient for JSON response)

**Note**: The implementation was recently updated from `chat_completion()` to `complete()` method with `CompletionConfig`. This change aligns with the updated GroqClient API.

#### Step 4: Parse JSON Response

```python
result = self.groq_client.validate_json_response(response.content)
if result is None:
    raise ValueError("Failed to parse JSON response from Groq")
```

**Expected JSON structure:**
```json
{
    "category": "INFORMATION_RETRIEVAL",
    "confidence": 0.87,
    "reasoning": "Query asks to find external salary data, which is information retrieval"
}
```

**JSON validation:**
- Uses `groq_client.validate_json_response()` for robust parsing
- Handles malformed JSON gracefully
- Raises error if JSON is invalid

**Extract fields:**
```python
category_name = result.get("category", "GENERAL_CHAT")
confidence = float(result.get("confidence", 0.5))
reasoning = result.get("reasoning", "No reasoning provided")
```

#### Step 5: Validate Category

```python
try:
    primary_category = Category.from_string(category_name)
except ValueError:
    print(f"[WARNING] Invalid category from Groq: {category_name}, using GENERAL_CHAT")
    primary_category = Category.GENERAL_CHAT
    confidence = 0.5
    reasoning = f"Invalid category '{category_name}', defaulted to GENERAL_CHAT"
```

**Category validation:**
- Converts string to Category enum using `Category.from_string()`
- If invalid category returned by LLM, defaults to GENERAL_CHAT
- Logs warning for debugging
- Sets confidence to 0.5 for invalid categories

#### Step 6: Calculate Latency

```python
latency_ms = int((time.time() - start_time) * 1000)
```

**Latency tracking:**
- Measures classification time in milliseconds
- Starts timer at beginning of `classify()` method
- Includes prompt building, API call, and JSON parsing
- Target: <500ms for production

#### Step 7: Determine Fallback

```python
fallback_triggered = confidence < self.confidence_threshold
```

**Fallback logic:**
- If confidence < threshold (default: 0.65), fallback is triggered
- When fallback is triggered, the query may route to GENERAL_CHAT
- The RoutingDecision includes `fallback_triggered` flag for downstream handling

#### Step 8: Return RoutingDecision

```python
decision = RoutingDecision(
    query_id=query_id,
    primary_category=primary_category,
    primary_confidence=confidence,
    reasoning=reasoning,
    classification_latency_ms=latency_ms,
    fallback_triggered=fallback_triggered,
)
return decision
```

**RoutingDecision object:**
- Immutable data class containing all routing information
- Used by AIRouter to determine which agent to invoke
- Logged to database for analytics and debugging

---

## Error Handling

### Groq API Failure

```python
except Exception as e:
    latency_ms = int((time.time() - start_time) * 1000)
    print(f"[ERROR] Groq classification failed: {e}", file=sys.stderr)

    return RoutingDecision(
        query_id=query_id,
        primary_category=Category.GENERAL_CHAT,
        primary_confidence=0.5,
        reasoning=f"Classification error: {str(e)}",
        classification_latency_ms=latency_ms,
        fallback_triggered=True,
    )
```

**Fallback on error:**
- Any exception during classification triggers fallback
- Returns GENERAL_CHAT with confidence 0.5
- Includes error message in reasoning
- Sets `fallback_triggered=True`

### Common Error Scenarios

1. **Groq API timeout**
   - Cause: Network latency or Groq service issues
   - Handling: Caught by exception handler, returns GENERAL_CHAT

2. **Invalid JSON response**
   - Cause: LLM returns malformed JSON or includes markdown formatting
   - Handling: `validate_json_response()` returns None, raises ValueError

3. **Invalid category name**
   - Cause: LLM returns category name not in Category enum
   - Handling: Caught by `Category.from_string()`, defaults to GENERAL_CHAT

4. **Missing required fields**
   - Cause: LLM omits "category", "confidence", or "reasoning"
   - Handling: `.get()` methods provide defaults

---

## Helper Methods

### _load_agent_definitions()

```python
def _load_agent_definitions(self):
    """Load agent definitions from config/agents.json."""
    with open(self.config_path, "r") as f:
        config = json.load(f)

    for category_str, agent_config in config.items():
        try:
            category = Category.from_string(category_str)
            self.available_agents.append({
                "name": category.value,
                "description": agent_config.get("description", ""),
                "examples": agent_config.get("example_queries", []),
            })
        except ValueError as e:
            print(f"[WARNING] Invalid category {category_str}: {e}")
            continue
```

**Purpose:**
- Loads agent configurations from JSON file
- Converts to internal representation
- Validates category names
- Skips invalid categories with warning

### _build_classification_prompt()

```python
def _build_classification_prompt(self) -> str:
    """Build system prompt for Groq classification."""
    category_descriptions = []
    for agent in self.available_agents:
        category = Category.from_string(agent["name"])
        description = Category.get_description(category)
        examples = agent.get("examples", [])[:3]

        category_info = f"- **{agent['name']}**: {description}"
        if examples:
            category_info += f"\n  Examples: {', '.join([f'"{ex}"' for ex in examples])}"
        category_descriptions.append(category_info)

    categories_text = "\n".join(category_descriptions)

    return f"""You are a query classification system...
    {categories_text}
    ..."""
```

**Purpose:**
- Dynamically builds system prompt from loaded agent definitions
- Includes up to 3 example queries per category
- Formats categories with descriptions and examples
- Returns complete system prompt string

### get_category_examples()

```python
def get_category_examples(self, category: Category) -> List[str]:
    """Get example queries for a category."""
    for agent in self.available_agents:
        if agent["name"] == category.value:
            return agent.get("examples", [])
    return []
```

**Purpose:**
- Retrieves example queries for a specific category
- Used for testing and documentation
- Returns empty list if category not found

---

## Performance Characteristics

### Latency Breakdown

Typical classification latency: **200-500ms**

| Step | Time | Percentage |
|------|------|-----------|
| Prompt building | 5-10ms | 2-3% |
| Groq API call | 150-400ms | 75-90% |
| JSON parsing | 5-10ms | 2-3% |
| Category validation | 1-2ms | <1% |
| Total | 200-500ms | 100% |

**Optimization opportunities:**
- Groq API call is the bottleneck (75-90% of time)
- Faster model (llama-3-70b-8192) can reduce latency by 20-30%
- Prompt caching could reduce prompt building time

### Accuracy Metrics

Expected accuracy on clear queries: **>90%**

| Confidence Range | Accuracy | Action |
|-----------------|----------|--------|
| 0.85-1.0 | 95%+ | Route confidently |
| 0.65-0.84 | 85-95% | Route with monitoring |
| <0.65 | <85% | Fallback to GENERAL_CHAT |

### Token Usage

Typical token usage per classification:

| Component | Tokens |
|-----------|--------|
| System prompt | 300-400 |
| User query | 10-100 |
| LLM response | 50-150 |
| Total | 400-650 |

**Cost per classification** (llama-3.3-70b-versatile):
- Input tokens: ~400 @ $0.59/1M = $0.000236
- Output tokens: ~100 @ $0.79/1M = $0.000079
- Total per classification: ~$0.000315

---

## Integration with AIRouter

The GroqClassifier is used by AIRouter as follows:

```python
# In AIRouter.__init__
self.classifier = GroqClassifier(
    config_path="config/agents.json",
    confidence_threshold=0.65,
    routing_model="llama-3.3-70b-versatile"
)

# In AIRouter.route_query()
decision = self.classifier.classify(
    query_text=query.text,
    query_id=query.query_id,
    previous_agent=session.get("previous_agent")
)

# Use decision to select agent
if decision.fallback_triggered:
    agent = self.agent_registry.get_agent(Category.GENERAL_CHAT)
else:
    agent = self.agent_registry.get_agent(decision.primary_category)
```

---

## Configuration Best Practices

### Choosing the Right Model

| Model | Speed | Accuracy | Cost | Use Case |
|-------|-------|----------|------|----------|
| llama-3.3-70b-versatile | Medium | High | Medium | Production (default) |
| llama-3-70b-8192 | Fast | Medium | Low | High-volume, cost-sensitive |
| mixtral-8x7b-32768 | Slow | Medium | Low | Large context needs |

**Recommendation**: Use llama-3.3-70b-versatile for production

### Tuning Confidence Threshold

| Threshold | Routing Behavior | Use Case |
|-----------|-----------------|----------|
| 0.55-0.60 | Aggressive | Prefer any routing over fallback |
| 0.65 | Balanced | Production default |
| 0.70-0.75 | Conservative | High accuracy requirements |

**Recommendation**: Start with 0.65, adjust based on production metrics

### Temperature Settings

| Temperature | Behavior | Use Case |
|-------------|----------|----------|
| 0.0-0.2 | Very deterministic | Testing, reproducibility |
| 0.3 | Deterministic | Production (default) |
| 0.5-0.7 | Balanced | General use (not recommended for routing) |

**Recommendation**: Use 0.3 for production routing

---

## Testing and Validation

### Unit Testing

Test the classifier with known queries:

```python
classifier = GroqClassifier()

# Test INFORMATION_RETRIEVAL
decision = classifier.classify(
    query_text="What are current salaries for developers?",
    query_id="test_1"
)
assert decision.primary_category == Category.INFORMATION_RETRIEVAL
assert decision.primary_confidence > 0.8

# Test GENERAL_CHAT fallback
decision = classifier.classify(
    query_text="Hello",
    query_id="test_2"
)
assert decision.primary_category == Category.GENERAL_CHAT
assert decision.primary_confidence > 0.85
```

### Integration Testing

Test with AIRouter:

```python
router = AIRouter()

response = router.route_query(
    query_text="Generate a quarterly report",
    query_id="integration_test_1"
)

assert response.category == Category.REPORT_GENERATION
assert response.confidence > 0.75
```

### Load Testing

Test classification performance under load:

```bash
# Use test_routing.py with multiple queries
python scripts/test_routing.py --file test_queries.txt --concurrent 10
```

Monitor:
- Average latency
- P95 latency
- Error rate
- Groq API rate limits

---

## Debugging Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

classifier = GroqClassifier()
# Will print detailed logs of classification process
```

### Inspect RoutingDecision

```python
decision = classifier.classify("your query", "test_id")

print(f"Category: {decision.primary_category}")
print(f"Confidence: {decision.primary_confidence}")
print(f"Reasoning: {decision.reasoning}")
print(f"Latency: {decision.classification_latency_ms}ms")
print(f"Fallback: {decision.fallback_triggered}")
```

### Test Individual Components

```python
# Test prompt building
prompt = classifier._build_classification_prompt()
print(prompt)

# Test category validation
category = Category.from_string("INFORMATION_RETRIEVAL")
print(f"Valid category: {category}")

# Test example queries
examples = classifier.get_category_examples(Category.PROBLEM_SOLVING)
print(f"Examples: {examples}")
```

---

## Known Issues and Limitations

### Issue 1: LLM Returns Invalid JSON

**Symptom**: `validate_json_response()` returns None

**Cause**: LLM includes markdown code fences or explanatory text

**Solution**: The system prompt now includes "**CRITICAL: Return ONLY valid JSON (no markdown, no explanation, no extra text)**"

### Issue 2: Inconsistent Category Assignments

**Symptom**: Similar queries route to different categories

**Cause**: Temperature too high or insufficient examples

**Solution**:
- Lower temperature to 0.2-0.3
- Add more diverse examples to `config/agents.json`

### Issue 3: Slow Classification (>500ms)

**Symptom**: High latency impacting user experience

**Cause**: Groq API latency or network issues

**Solution**:
- Use faster model (llama-3-70b-8192)
- Implement caching for common queries
- Monitor Groq API status

### Issue 4: High Fallback Rate (>15%)

**Symptom**: Too many queries route to GENERAL_CHAT

**Cause**: Confidence threshold too high or queries too vague

**Solution**:
- Lower confidence threshold to 0.60
- Improve query phrasing guidance
- Add more example queries

---

## Future Enhancements

1. **Caching**: Cache classification results for identical queries
2. **Multi-category routing**: Support queries that need multiple agents
3. **Confidence calibration**: Dynamically adjust threshold based on accuracy metrics
4. **A/B testing**: Compare different models and configurations
5. **Semantic similarity fallback**: Use embeddings when Groq API fails

---

**Version**: 1.0.0
**Last Updated**: 2025-01-01
**Implementation File**: `utils/ai_router/groq_classifier.py`
