# Query Classification System

## Overview

The chat system uses a two-layer classification approach:

1. **Layer 1 (Frontend):** Fast regex pattern matching for immediate feedback
2. **Layer 2 (AI Router):** Groq LLM-based classification for intelligent routing

---

## Layer 1: Frontend Regex Classification

**Location:** `/frontend/dashboard.jsx`

**Purpose:** Quick classification for user feedback in system console (no network latency)

**Patterns:**

```javascript
const classificationPatterns = {
  "general-chat": /^(hi|hello|hey|good morning|how are you|good afternoon|good evening|hiya|yo|sup|hey there|what's up|what's good|how's it going).*/i,

  "information-retrieval": /find|search|lookup|show me|get me|list|display|who|which|where|when|query|locate|retrieve|look for|fetch|discover|identify|select|filter|extract/i,

  "problem-solving": /^(why|analyze|analyze|identify|diagnose|investigate|explain|break down|assess|evaluate|review|examine|understand|figure out|solve|troubleshoot|fix|improve|optimize|enhance).*(issue|problem|bottleneck|challenge|difficulty|concern|obstacle|barrier|hurdle)/i,

  "automation": /^(automate|set up|configure|create|build|design|implement|develop|establish|make).*( workflow|process|automation|pipeline|sequence|trigger|action|task|job|routine)/i,

  "report-generation": /^(generate|create|make|produce|build|write|prepare|compile|develop|design).*(report|dashboard|summary|analysis|visualization|chart|graph|breakdown|presentation|overview|metrics|kpi|stats|statistics)/i,

  "industry-knowledge": /gdpr|data protection|privacy|right to work|visa|immigration|ir35|offpayroll|off-payroll|employment law|employment contract|diversity|inclusion|equality|recruitment standard|recruitment process|salary benchmark|wage|compensation|notice period|contract term|leave policy|redundancy|unfair dismissal|discrimination|harassment|bullying|whistleblowing|health safety|working time|minimum wage|national insurance|tax|legal requirement|compliance|regulation|law|act|directive|uk recruitment|employment right|worker classification|agency worker|temporary worker/i,

  "data-operations": /^(create|add|new|update|modify|change|edit|delete|remove|schedule|book|arrange|send|email|generate|make|write|produce|mark|set|assign).*(record|entry|invoice|placement|job|candidate|client|contact|appointment|interview|meeting|event|document|form|file|contract|offer|email|message|reminder|notification|timesheet|report)/i
};
```

**Default:** If no pattern matches, defaults to `"general-chat"`

**Characteristics:**
- Very fast (<1ms)
- No network latency
- Immediate console feedback
- Simple keyword matching
- May have false positives/negatives

---

## Layer 2: AI Router LLM Classification (GroqClassifier)

**Location:** `/utils/ai_router/groq_classifier.py`

**Purpose:** Intelligent LLM-based intent analysis for accurate routing decisions

> **For comprehensive details on GroqClassifier, see the `router` skill.**

### How It Works

```
Step 1: Initialize GroqClassifier
├─ Model: llama-3.3-70b-versatile (Groq LLM)
├─ Confidence threshold: 0.55 (configurable)
├─ Temperature: 0.3 (factual, deterministic)
└─ Prompt template: Built from agent definitions

Step 2: Load Agent Definitions
├─ Load from config/agents.json
├─ Extract category descriptions and examples
├─ Build classification prompt with all categories
└─ Store in memory for fast prompt construction

Step 3: For Each New Query
├─ Build system prompt with category descriptions
├─ Add user query as message
├─ Call Groq LLM API:
│  ├─ Model: llama-3.3-70b-versatile
│  ├─ Temperature: 0.3
│  ├─ Max tokens: 200
│  └─ Expected: JSON response
├─ Parse JSON response:
│  └─ {"category": "INFORMATION_RETRIEVAL", "confidence": 0.92, "reasoning": "..."}
└─ Validate category and confidence

Step 4: Output RoutingDecision
├─ Primary category: from LLM response
├─ Primary confidence: 0.92 (92%)
├─ Reasoning: "Query matches information retrieval patterns (find, search, candidates, skills)"
├─ Classification latency: 100-200ms
└─ System prompt: Full prompt sent to LLM (for transparency)
```

### Example Classification

**Query:** "Find candidates with Python skills in London"

**LLM Response:**
```json
{
  "category": "INFORMATION_RETRIEVAL",
  "confidence": 0.92,
  "reasoning": "Query contains action verbs 'find' and specific search criteria (candidates, Python skills, London), clearly indicating an information retrieval request"
}
```

**RoutingDecision:**
```python
RoutingDecision(
    query_id="abc123",
    primary_category=Category.INFORMATION_RETRIEVAL,
    primary_confidence=0.92,
    reasoning="Query contains action verbs 'find' and specific search criteria...",
    classification_latency_ms=143,
    fallback_triggered=False
)
```

### Confidence Thresholds

| Confidence | Action |
|-----------|--------|
| **>= 0.55 (55%)** | Route to primary agent |
| **< 0.55** | Fallback to General Chat with warning |

**Note:** The 0.55 threshold is lower than traditional semantic similarity (0.65-0.70) because LLM classification is more accurate and includes reasoning transparency.

### Classification Latency

- **Typical:** 100-200ms per query (API call + JSON parsing)
- **On startup:** <1 second (no model loading)
- **Target:** <300ms for 95th percentile

### Why Groq LLM Classification?

**Advantages over Semantic Similarity:**
1. **Superior accuracy** - Understands context and intent, not just keywords
2. **Reasoning transparency** - Explains why it chose each category
3. **Fast startup** - No 13-second model download
4. **Low memory** - <10MB vs 500MB+ for local models
5. **Easy maintenance** - No model retraining or example encoding
6. **Flexible** - Adapts to new query patterns without retraining

**Trade-offs:**
- Slightly higher per-query latency (100-200ms vs 45-80ms)
- Requires GROQ_API_KEY environment variable
- Depends on external API (but highly reliable)

### Example Queries in agents.json

For accurate classification, each agent needs quality example queries:

```json
{
  "INFORMATION_RETRIEVAL": {
    "description": "Search and retrieve information from databases, web, and industry sources",
    "example_queries": [
      "Find candidates with Python skills",
      "Show me active jobs in London",
      "Search for placements in Q4 2024",
      "What are current salary benchmarks for software engineers?",
      "List all clients in the financial services sector",
      "Who are the top performing recruiters?",
      "Display candidates matching this job description",
      "Search for candidates with 5+ years experience",
      "Show me recruitment metrics for last quarter",
      "Find candidates willing to relocate"
    ]
  },
  "PROBLEM_SOLVING": {
    "description": "Analyze complex business problems and provide strategic recommendations",
    "example_queries": [
      "Why is our placement rate lower than industry average?",
      "How can we improve candidate retention?",
      "Analyze our recruitment bottlenecks",
      "What strategies reduce time-to-hire?",
      "Why do high-quality candidates drop out?",
      "Identify cost optimization opportunities",
      "Improve our fee recovery process",
      "How can we scale without losing quality?",
      "What's causing our lower conversion rate?",
      "Analyze competitor strategies and benchmark ourselves"
    ]
  }
}
```

**Best Practices for Example Queries:**

1. **Variety:** Include 5-10 different phrasings/contexts
2. **Specificity:** Use realistic, detailed examples
3. **Diversity:** Cover different use cases for the agent
4. **Clarity:** Make the agent's purpose obvious
5. **Avoid ambiguity:** Don't use phrases that could apply to other agents
6. **Domain terms:** Use recruitment/business terminology
7. **Length variation:** Mix short and longer queries
8. **Regular updates:** Keep examples current and relevant

### LLM Classification Example: Ambiguous Query

**Query:** "Create a report on our top Python developers"

**LLM Analysis:**
```json
{
  "category": "REPORT_GENERATION",
  "confidence": 0.88,
  "reasoning": "Primary intent is to generate a report. While the query involves retrieving developer information, the action verb 'create' and focus on 'report' clearly indicate report generation is the main goal."
}
```

**Why LLM Excels Here:**
- Understands "create a report" as primary intent
- Recognizes "top Python developers" as data to include, not the goal
- Provides reasoning that clarifies the decision
- Higher confidence than semantic similarity would give

---

## Classifier Configuration

**File:** `/utils/ai_router/groq_classifier.py`

```python
# Model settings
MODEL_NAME = "llama-3.3-70b-versatile"  # Groq LLM model
TEMPERATURE = 0.3                        # Low temp for consistency
MAX_TOKENS = 200                         # JSON response only
CONFIDENCE_THRESHOLD = 0.55              # Min routing confidence

# Classification settings
OUTPUT_FORMAT = "json"                   # Structured JSON output
INCLUDE_REASONING = True                 # Include reasoning in response
INCLUDE_SYSTEM_PROMPT = True             # Attach prompt for debugging
```

---

## Monitoring Classification

Track classification accuracy:

```python
# Metrics to monitor
- Average confidence per agent
- Classification success rate
- Fallback rate (< 0.55 confidence)
- Classification latency distribution
- Reasoning quality (manual review)

# Alerts
- Avg confidence < 0.70
- Fallback rate > 20%
- Classification latency > 300ms
- Specific agent gets routed < 5% of time
- API errors > 1%
```

---

## Testing Classification

### Unit Tests

```python
def test_information_retrieval_classification():
    query = "Find candidates with Python skills in London"
    decision = classifier.classify(query, query_id="test_1")

    assert decision.primary_category == Category.INFORMATION_RETRIEVAL
    assert decision.primary_confidence >= 0.55
    assert decision.classification_latency_ms < 300
    assert decision.reasoning is not None

def test_low_confidence_fallback():
    query = "Something unclear and vague"
    decision = classifier.classify(query, query_id="test_2")

    # Low confidence triggers fallback
    if decision.primary_confidence < 0.55:
        assert decision.fallback_triggered == True
```

### Manual Testing via CLI

```bash
python -m utils.ai_router.cli "Find candidates with Python"
# Output:
# Classification:
#   Primary:   INFORMATION_RETRIEVAL
#   Confidence: 92.0%
#
# Reasoning:
#   Query contains action verb 'find' and specific search criteria...
#
# Agent Response:
#   [Information Retrieval Agent output...]
#
# Total Latency: 1523ms
```

---

## Classification Drift & Maintenance

### Monitor for Drift

Track if classification accuracy decreases over time:

```
Week 1: 94% accuracy
Week 2: 93% accuracy
Week 3: 89% accuracy  ← Drift detected
Week 4: 85% accuracy  ← Urgent attention needed
```

**Causes:**
- Query patterns changed
- New business domains added
- Example queries became outdated
- Agent descriptions unclear

### Maintenance Actions

1. **Review low-confidence queries:** Check queries with <0.55 confidence
2. **Update example queries:** Refresh agents.json examples
3. **Improve descriptions:** Clarify agent category descriptions
4. **Add new agents:** If new query categories emerge
5. **Monitor metrics:** Daily classification accuracy tracking

### Example Maintenance Update

```json
// Before: Vague description
"description": "Search for things"

// After: Clear, specific description
"description": "Search and retrieve information from databases, web, and industry sources. Handles queries about candidates, jobs, clients, salaries, metrics, and data lookups."
```

**Result:** Classification accuracy improves from 87% → 94%

---

## Migration from Semantic Similarity (Historical)

**Previous System:** sentence-transformers with all-MiniLM-L6-v2 model
**Current System:** Groq LLM-based classification

**Benefits of Migration:**
- 53x faster startup (13s → 0.25s)
- 98% lower memory usage (500MB → <10MB)
- Superior accuracy with reasoning transparency
- No model maintenance or retraining

**See:** `.claude/session-artifacts/SEMANTIC_CLASSIFIER_REMOVAL.md` for complete migration details.
