# Query Classification System

## Overview

The chat system uses a two-layer classification approach:

1. **Layer 1 (Frontend):** Fast regex pattern matching for immediate feedback
2. **Layer 2 (AI Router):** Semantic similarity using ML for intelligent routing

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

## Layer 2: AI Router Semantic Classification

**Location:** `/utils/ai_router/classifier.py`

**Purpose:** Intelligent ML-based classification for accurate routing decisions

### How It Works

```
Step 1: Load Sentence Transformer Model
├─ Model: all-MiniLM-L6-v2
├─ Dimensions: 384-dimensional embeddings
└─ Pre-loaded at startup

Step 2: Pre-encode Example Queries
├─ Load example queries from config/agents.json
├─ Encode each to 384-dimensional vector
├─ Group vectors by category
└─ Store in memory for fast comparison

Step 3: For Each New Query
├─ Encode query text to 384-dimensional vector
├─ Calculate cosine similarity to all examples:
│  ├─ Similarity = dot_product(query_vec, example_vec) / (||query_vec|| * ||example_vec||)
│  └─ Result: 0.0 to 1.0 (1.0 = identical)
├─ Take max similarity per category as category score
│  └─ [GENERAL_CHAT: 0.45, INFORMATION_RETRIEVAL: 0.87, PROBLEM_SOLVING: 0.52, ...]
└─ Sort categories by confidence descending

Step 4: Output RoutingDecision
├─ Primary category: highest confidence
├─ Primary confidence: 0.87 (87%)
├─ Secondary category: 2nd highest IF > 0.5
│  └─ Otherwise: None
├─ Secondary confidence: 0.52 (52%) if included
└─ Reasoning: "Query matches information retrieval patterns (find, search, candidates, skills)"
```

### Example Classification

**Query:** "Find candidates with Python skills in London"

```
Step 1: Encode to embedding vector (384 dimensions)

Step 2: Calculate similarities
├─ GENERAL_CHAT:           0.23 (low, greeting-like language absent)
├─ INFORMATION_RETRIEVAL:  0.92 ✓ (keywords: find, candidates, skills, location)
├─ PROBLEM_SOLVING:        0.34 (not analyzing problem)
├─ REPORT_GENERATION:      0.21 (not generating report)
├─ AUTOMATION:             0.18 (not automating process)
├─ INDUSTRY_KNOWLEDGE:     0.31 (not asking about regulations)
└─ DATA_OPERATIONS:        0.29 (not creating/updating records)

Step 3: Sort by confidence
1. INFORMATION_RETRIEVAL: 0.92 ← Primary
2. PROBLEM_SOLVING:       0.34
3. INDUSTRY_KNOWLEDGE:    0.31
... (rest below 0.3)

Step 4: Create RoutingDecision
├─ Primary: INFORMATION_RETRIEVAL (92% confidence)
├─ Secondary: PROBLEM_SOLVING (34% confidence)
├─ But secondary < 0.5, so suppress it
└─ Final: Route to INFORMATION_RETRIEVAL with 92% confidence
```

### Confidence Thresholds

| Confidence | Action |
|-----------|--------|
| **>= 0.7 (70%)** | Route to primary agent |
| **0.5 - 0.7** | Suggest secondary agent, route to primary |
| **0.3 - 0.5** | Consider fallback to General Chat with clarification |
| **< 0.3** | Return clarification request, route to General Chat |

### Classification Latency

- **Typical:** 45-150ms per query
- **On startup:** ~500ms (loading model + encoding examples)
- **Per query:** ~10-50ms (query encoding + similarity calculations)
- **Target:** <100ms

### Example Queries in agents.json

For accurate classification, each agent needs quality example queries:

```json
{
  "INFORMATION_RETRIEVAL": {
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
  },
  "AUTOMATION": {
    "example_queries": [
      "Automate sending welcome emails to new candidates",
      "Create a workflow for interview scheduling",
      "Set up automated candidate nurturing sequence",
      "Design a process to notify hiring managers of new applications",
      "Build workflow for placement follow-up",
      "Automate timesheet distribution and collection",
      "Create trigger for job post distribution",
      "Design interview reminder automation",
      "Automate invoice generation",
      "Set up automated reporting"
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

### Improving Classification Accuracy

**Increase Example Quality:**
```json
// GOOD: Specific, clear intent
"Find Python developers with 5+ years in London with salary > 50k"

// BAD: Vague, could match multiple agents
"Tell me about Python"
```

**Add Domain-Specific Terms:**
```json
// GOOD: Uses recruitment vocabulary
"Search candidates matching job REF-2024-001"

// BAD: Generic language
"Find some people for a job"
```

**Expand Coverage:**
```json
// GOOD: 10 diverse examples cover edge cases
[
  "Find candidates with Python",
  "Show me active Python job posts",
  "Search for experienced Python developers",
  "List all Python contractors",
  "Display candidates matching Python job",
  ...8 more variations...
]

// BAD: Only 2 examples, limited coverage
[
  "Find Python candidates",
  "Show me Python jobs"
]
```

### Semantic Similarity Explained

The system uses cosine similarity to measure how semantically similar two text pieces are:

```python
# Two queries
query1 = "Find candidates with Python skills"
query2 = "Search for developers who know Python programming"

# Encoded to 384-dimensional vectors
vec1 = [0.32, -0.12, 0.89, ...]  # 384 values
vec2 = [0.31, -0.11, 0.88, ...]  # 384 values

# Cosine similarity
similarity = dot_product(vec1, vec2) / (magnitude(vec1) * magnitude(vec2))
# Result: 0.94 (94% similar - very close in meaning)
```

**Why It Works:**
- Captures semantic meaning, not just keywords
- "Find candidates with Python" ~ "Search for Python developers" (0.92 similarity)
- Handles synonyms: find/search, candidates/developers, skills/knowledge
- Robust to typos and variations

### Classification Example: Ambiguous Query

**Query:** "Create a report on our top Python developers"

```
Step 1: Encode query

Step 2: Calculate similarities
├─ INFORMATION_RETRIEVAL:  0.78 (find + Python developers)
├─ REPORT_GENERATION:      0.81 ✓ (create + report)
├─ DATA_OPERATIONS:        0.65 (create + report generation)
└─ Others: < 0.5

Step 3: Sort by confidence
1. REPORT_GENERATION: 0.81 ← Primary (highest)
2. INFORMATION_RETRIEVAL: 0.78 ← Secondary (> 0.7)
3. DATA_OPERATIONS: 0.65 ← Tertiary

Step 4: Create RoutingDecision
├─ Primary: REPORT_GENERATION (81% confidence)
├─ Secondary: INFORMATION_RETRIEVAL (78% confidence)
│  └─ Secondary > 0.7, so include in decision
├─ Confidence: High, clear routing to Report Generation
└─ Reasoning: Query focuses on report creation; data retrieval is secondary concern
```

**System Behavior:**
1. Routes to REPORT_GENERATION (primary)
2. Includes INFORMATION_RETRIEVAL as secondary in context
3. If Report Generation timeout/fails, fallback to Information Retrieval
4. High confidence allows immediate routing without clarification

---

## Classifier Configuration

**File:** `/utils/ai_router/classifier.py`

```python
# Model settings
MODEL_NAME = "all-MiniLM-L6-v2"      # Sentence transformer model
EMBEDDING_DIM = 384                  # Vector dimensions
BATCH_SIZE = 32                      # Encode batch size

# Similarity settings
SIMILARITY_THRESHOLD = 0.5           # Min category similarity
SECONDARY_THRESHOLD = 0.5            # Min secondary category
TOP_K_CATEGORIES = 3                 # Return top 3 categories

# Performance
CACHE_EMBEDDINGS = True              # Cache encoded examples
PRELOAD_AT_STARTUP = True            # Load model on startup
```

---

## Monitoring Classification

Track classification accuracy:

```python
# Metrics to monitor
- Average confidence per agent
- Classification success rate
- Fallback rate (< 0.7 confidence)
- Secondary category inclusion rate
- Classification latency distribution
- Confusion matrix (predicted vs actual)

# Alerts
- Avg confidence < 0.75
- Fallback rate > 20%
- Classification latency > 200ms
- Specific agent gets routed < 5% of time
```

---

## Testing Classification

### Unit Tests

```python
def test_information_retrieval_classification():
    query = "Find candidates with Python skills in London"
    decision = classifier.classify(query)
    
    assert decision.primary_category == Category.INFORMATION_RETRIEVAL
    assert decision.primary_confidence >= 0.7
    assert decision.classification_latency_ms < 100

def test_ambiguous_query_fallback():
    query = "Something unclear"
    decision = classifier.classify(query)
    
    # Low confidence triggers clarification
    assert decision.primary_confidence < 0.7
    assert decision.fallback_triggered == True
```

### Manual Testing via CLI

```bash
python utils/ai_router/cli.py "Find candidates with Python"
# Output:
# Query: Find candidates with Python
# Primary: INFORMATION_RETRIEVAL (0.92)
# Secondary: None
# Classification Time: 45ms
```

---

## Classification Drift & Maintenance

### Monitor for Drift

Track if classification accuracy decreases over time:

```
Week 1: 92% accuracy
Week 2: 91% accuracy
Week 3: 87% accuracy  ← Drift detected
Week 4: 83% accuracy  ← Urgent attention needed
```

**Causes:**
- Query patterns changed
- New business domains added
- Example queries became outdated
- LLM model degradation

### Maintenance Actions

1. **Review low-confidence queries:** Check queries with <0.7 confidence
2. **Update example queries:** Refresh agents.json examples
3. **Add new agents:** If new query categories emerge
4. **Retrain classifier:** Re-encode all examples (model reload)
5. **Monitor metrics:** Daily classification accuracy tracking

### Example Maintenance Update

```json
// Before: Only 5 examples, missing edge cases
"example_queries": [
  "Find candidates with Python",
  "Show me Python jobs",
  "Search for Python developers",
  "List Python placements",
  "Display Python positions"
]

// After: 10 diverse examples, covers edge cases
"example_queries": [
  "Find candidates with Python skills",
  "Show me active Python job posts",
  "Search for experienced Python developers in London",
  "List all Python contractors available immediately",
  "Display candidates matching Python job REF-2024-001",
  "Who has Python and Java skills?",
  "Python developers with 5+ years experience",
  "Find senior Python engineers for startup",
  "Candidates with Python and DevOps knowledge",
  "Show me all placements involving Python roles"
]
```

Result: Classification accuracy improves from 87% → 94%
