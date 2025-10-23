# Chat System Configuration Reference

## Configuration Files

### Main Agent Configuration: /config/agents.json

This JSON file defines all 7 agents, their LLM models, tools, timeouts, and example queries.

**Structure:**
```json
{
  "GENERAL_CHAT": {
    "name": "General Chat",
    "priority": 3,
    "description": "Friendly conversation fallback",
    "agent_class": "utils.ai_router.agents.general_chat_agent:GeneralChatAgent",
    "llm_provider": "groq",
    "llm_model": "llama-3-70b-8192",
    "timeout_seconds": 2,
    "retry_count": 1,
    "retry_delay_ms": 500,
    "tools": [],
    "resources": {},
    "system_prompt": "You are a friendly conversational assistant...",
    "enabled": true,
    "example_queries": [
      "Hi there, how are you?",
      "Tell me a joke",
      "What's the weather like?"
    ]
  },
  "INFORMATION_RETRIEVAL": {
    "name": "Information Retrieval",
    "priority": 1,
    "description": "Search and retrieve data",
    "agent_class": "utils.ai_router.agents.information_retrieval_agent:InformationRetrievalAgent",
    "llm_provider": "groq",
    "llm_model": "llama-3-70b-8192",
    "timeout_seconds": 2,
    "retry_count": 1,
    "retry_delay_ms": 500,
    "tools": ["web_search", "database_query"],
    "resources": {},
    "system_prompt": "You are information retrieval specialist...",
    "enabled": true,
    "example_queries": [
      "Find candidates with Python skills",
      "Show me active jobs in London",
      "What are average salaries for software engineers?"
    ]
  },
  // ... 5 more agents
}
```

## Configuration Fields Explained

### name
- **Type:** String
- **Purpose:** Display name for the agent
- **Example:** "Information Retrieval"
- **Used in:** Logs, API responses, UI display

### priority
- **Type:** Integer (1-3)
- **Purpose:** Relative importance for routing decisions
- **Values:**
  - `1`: P1 MVP agents (Information Retrieval, Industry Knowledge, Data Operations)
  - `2`: P2 agents (Problem Solving, Automation)
  - `3`: P3 agents (General Chat, Report Generation)
- **Used in:** Agent selection when confidence is borderline

### description
- **Type:** String
- **Purpose:** Human-readable description of agent purpose
- **Example:** "Search and retrieve data from databases, web, and industry sources"
- **Used in:** Documentation, CLI help text

### agent_class
- **Type:** String (Python module path + class name)
- **Format:** `"module.path.to.module:ClassName"`
- **Example:** `"utils.ai_router.agents.information_retrieval_agent:InformationRetrievalAgent"`
- **Used in:** Dynamic class loading via Python's importlib
- **Rules:**
  - Module path must be importable from project root
  - Class must exist and inherit from BaseAgent
  - Class must implement process() and get_category() methods

### llm_provider
- **Type:** String (enum)
- **Values:**
  - `"groq"` - Groq API (faster, more cost-effective)
  - `"anthropic"` - Anthropic Claude API (superior reasoning)
- **Example:** `"groq"`
- **Used in:** LLM initialization and API call routing

### llm_model
- **Type:** String (model identifier)
- **Groq Models:**
  - `"llama-3-70b-8192"` - 70B parameter model (most common)
  - `"llama-3.3-70b-versatile"` - Latest Llama 3.3
  - Other available Groq models
- **Anthropic Models:**
  - `"claude-3-5-sonnet-20241022"` - Latest Sonnet (used for Problem Solving)
  - `"claude-3-opus-20240229"` - Most capable but slower
  - `"claude-3-haiku-20240307"` - Fastest but least capable
- **Example:** `"llama-3-70b-8192"`
- **Used in:** LLM API calls, determines response quality/speed

### timeout_seconds
- **Type:** Integer
- **Purpose:** Maximum execution time for this agent
- **Standard Value:** `2`
- **Used in:** Timeout protection; if exceeded, triggers retry or fallback
- **Behavior:**
  - Agent execution starts
  - If execution takes > timeout_seconds, interrupt agent
  - Retry once with retry_delay_ms delay
  - If still exceeds, fallback to General Chat

### retry_count
- **Type:** Integer
- **Purpose:** Number of automatic retries on failure
- **Standard Value:** `1`
- **Used in:** Error recovery strategy
- **Behavior:**
  - First attempt: agent execution
  - Timeout or error: retry_delay_ms delay
  - Second attempt: agent execution
  - Still fails: fallback or error response

### retry_delay_ms
- **Type:** Integer (milliseconds)
- **Purpose:** Delay before retry attempt
- **Standard Value:** `500` (0.5 seconds)
- **Used in:** Rate limiting and temporary failure recovery
- **Behavior:**
  - On timeout/error, wait retry_delay_ms milliseconds
  - Then attempt retry
  - Total delay = retry_delay_ms per retry

### tools
- **Type:** Array of Strings
- **Purpose:** List of tools this agent can access
- **Examples:**
  - `[]` - No tools (General Chat)
  - `["web_search", "database_query"]` - Information Retrieval
  - `["workflow_builder"]` - Automation
- **Used in:** Agent initialization and capability description
- **Tool Types:**
  - `"web_search"` - Internet search
  - `"database_query"` - Internal database access
  - `"workflow_builder"` - Automation design
  - `"data_visualization"` - Chart/report suggestions
  - `"crud_operations"` - Create/Update/Delete operations
  - `"industry_research"` - Domain knowledge lookup

### resources
- **Type:** Object/Dictionary
- **Purpose:** Additional resources for agent use
- **Examples:**
  ```json
  {
    "sources_file": "sources_validated_summaries.md",
    "templates": ["template1.txt", "template2.txt"]
  }
  ```
- **Used in:** Agent-specific configuration and resource loading
- **Industry Knowledge Agent Example:**
  ```json
  "resources": {
    "sources_file": "docs/knowledge/sources_validated_summaries.md",
    "domains": [
      "gdpr", "ir35", "right-to-work", "employment-law",
      "diversity", "recruitment-standards", "salary-benchmarks"
    ]
  }
  ```

### system_prompt
- **Type:** String or Path to file
- **Purpose:** LLM system prompt defining agent personality and behavior
- **Can be:**
  - Inline string (short prompts)
  - Path to file in `/backend-api/prompts/agent-system-prompts/[agent-type].txt`
  - Template with variables
- **Used in:** LLM message assembly; first message in messages array
- **Example for Information Retrieval:**
  ```
  "You are an expert information retrieval specialist for a UK recruitment agency.
   Your role is to search for and aggregate information from multiple sources.
   Always cite your sources and provide structured, actionable results."
  ```

### enabled
- **Type:** Boolean
- **Purpose:** Enable/disable agent at runtime
- **Values:**
  - `true` - Agent is active and can be routed to
  - `false` - Agent is disabled; queries won't be routed here
- **Used in:** Agent registry availability checks
- **Runtime Control:** Can be toggled without server restart

### example_queries
- **Type:** Array of Strings
- **Purpose:** Example queries for semantic classification training
- **Min. Required:** 5-10 examples per agent
- **Used in:** Semantic classifier (converts to embeddings, calculates similarity)
- **Importance:** More and better examples = more accurate routing
- **Example for Problem Solving:**
  ```json
  [
    "How can we reduce candidate dropout rate by 20%?",
    "Why is our placement rate lower than industry average?",
    "What strategies improve time-to-hire for technical roles?",
    "How do we scale our recruiting without losing quality?",
    "Analyze our fee recovery challenges"
  ]
  ```

## Backend API Environment Variables

### Required Variables

**GROQ_API_KEY**
- **Purpose:** Groq API authentication
- **Format:** API key string
- **Used in:** All Groq model calls
- **Set in:** `.env` file or system environment
- **Example:** `GROQ_API_KEY=gsk_xxx...`

**ANTHROPIC_API_KEY** (if using Claude)
- **Purpose:** Anthropic API authentication
- **Format:** API key string
- **Used in:** Problem Solving Agent (Claude calls)
- **Set in:** `.env` file or system environment
- **Example:** `ANTHROPIC_API_KEY=sk-ant-xxx...`

### Optional Variables

**PORT**
- **Purpose:** Express server port
- **Default:** `3001` or `3002`
- **Set in:** `.env` file or system environment
- **Example:** `PORT=3002`

**NODE_ENV**
- **Purpose:** Environment mode
- **Values:** `development`, `production`
- **Default:** `development`
- **Affects:** Logging level, error details

**REDIS_URL** (AI Router only)
- **Purpose:** Redis connection string
- **Format:** `redis://host:port`
- **Default:** `redis://localhost:6379`
- **Used in:** Session storage

**DATABASE_URL** (AI Router only)
- **Purpose:** PostgreSQL connection string
- **Format:** `postgresql://user:password@host:port/database`
- **Used in:** Decision logging and analytics

## Backend LLM Configuration

Located in `/backend-api/server.js`

### Groq Configuration
```javascript
const client = new Groq({
  apiKey: process.env.GROQ_API_KEY
});

const groqSettings = {
  temperature: 0.7,      // Varies by agent type
  max_tokens: 2000,      // Max response length
  top_p: 0.9,            // Nucleus sampling
  model: "llama-3.3-70b-versatile"
};
```

**Temperature Settings:**
- `0.3` - Structured tasks (Information Retrieval, Report Generation, Automation)
- `0.7` - General chat (General Chat)
- `0.5` - Balanced reasoning (Problem Solving)

**max_tokens Settings:**
- `1000` - Short responses (General Chat)
- `1500` - Medium responses (Industry Knowledge, Data Operations)
- `2000` - Long responses (Information Retrieval, Problem Solving, Report Generation, Automation)

## Frontend Configuration

Located in `/frontend/dashboard.jsx`

### API Endpoint
```javascript
const API_BASE_URL = "http://localhost:3002"; // Backend API
const CHAT_ENDPOINT = "/api/chat";
const CLEAR_ENDPOINT = "/api/chat/clear";
const STATS_ENDPOINT = "/api/chat/stats";
```

### Role-Based Query Examples

Each role has role-specific example queries that populate the sidebar:

```javascript
const roleQueries = {
  "Managing Director": [
    "Analyze our quarterly performance trends",
    "What's the profitability impact of our recent placements?",
    // ... more director-level queries
  ],
  "Sales": [
    "Find candidates with sales experience",
    "Show me active jobs matching our client needs",
    // ... more sales queries
  ],
  "Recruiter": [
    "Find candidates with specific skills",
    "Schedule interviews for shortlisted candidates",
    // ... more recruiter queries
  ],
  // ... other roles
};
```

### Classification Patterns

Frontend regex patterns for immediate classification feedback:

```javascript
const classificationPatterns = {
  "general-chat": /^(hi|hello|hey|good morning|how are you).*/i,
  "information-retrieval": /find|search.*candidate|job|placement/i,
  "problem-solving": /^(why|analyze|identify).*issue|problem|bottleneck/i,
  "automation": /^(automate|workflow|set up).*process|pipeline/i,
  "report-generation": /^(generate|create|make|produce).*report|dashboard/i,
  "industry-knowledge": /gdpr|ir35|right-to-work|compliance|regulation/i
};
```

## AI Router Configuration

Located in `/utils/ai_router/`

### Router Settings

```python
# router.py configuration
CONFIDENCE_THRESHOLD = 0.7      # Min confidence to route
AGENT_TIMEOUT_SECONDS = 2.0     # Max agent execution time
MAX_RETRIES = 1                 # Automatic retry count
RETRY_DELAY_MS = 500            # Delay between retries
FALLBACK_AGENT = "GENERAL_CHAT" # Fallback when uncertain
```

### Classifier Settings

```python
# classifier.py configuration
MODEL = "all-MiniLM-L6-v2"      # Sentence transformer model
SIMILARITY_THRESHOLD = 0.5      # Min similarity for match
TOP_K_CATEGORIES = 2            # Return top 2 categories
ENCODING_BATCH_SIZE = 32        # Batch size for encoding
```

### Session Store Settings

```python
# storage/session_store.py configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
SESSION_TTL_MINUTES = 30        # Auto-expire after 30 min
MAX_MESSAGES_PER_SESSION = 50   # Max message history
```

### Log Repository Settings

```python
# storage/log_repository.py configuration
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "recruitment_ai"
BATCH_SIZE = 100                # Batch logs before write
RETENTION_DAYS = 30             # Delete logs older than 30 days
```

## Modifying Configuration

### Change an Agent's LLM Model

1. Open `/config/agents.json`
2. Find the agent (e.g., "INFORMATION_RETRIEVAL")
3. Change `llm_model` field:
   ```json
   "llm_model": "llama-3.3-70b-versatile"
   ```
4. If using different provider, also change `llm_provider`
5. Restart backend server

### Disable an Agent

1. Open `/config/agents.json`
2. Find the agent
3. Change `enabled` to `false`:
   ```json
   "enabled": false
   ```
4. Queries won't be routed to this agent; will use secondary or fallback
5. No server restart needed (checked at runtime)

### Add Agent Example Queries

1. Open `/config/agents.json`
2. Find the agent
3. Add to `example_queries` array:
   ```json
   "example_queries": [
     "Existing query 1",
     "Existing query 2",
     "New query to add"
   ]
   ```
4. More examples = better semantic classification
5. No server restart needed

### Update Agent System Prompt

**Option 1: Inline (short prompts)**
1. Open `/config/agents.json`
2. Change `system_prompt` field directly

**Option 2: External file (long prompts)**
1. Create/edit `/backend-api/prompts/agent-system-prompts/[agent-type].txt`
2. In `/config/agents.json`, reference the file path
3. Backend loads file at runtime

### Change Temperature Settings

1. Open `/backend-api/server.js`
2. Find the agent's configuration
3. Change `temperature` value:
   - Lower (0.3) = more factual/structured
   - Higher (0.7) = more creative/conversational
4. Restart backend server

## Performance Tuning

### Reduce Latency

1. **Reduce max_tokens:** Smaller responses = faster LLM calls
2. **Lower temperature:** Can marginally speed up generation
3. **Optimize system prompt:** Shorter prompts = faster processing
4. **Switch to faster model:** e.g., Groq llama-3-70b vs Claude Opus

### Increase Accuracy

1. **Add more example queries:** Better classifier training
2. **Increase max_tokens:** More room for detailed responses
3. **Lower temperature:** For factual tasks (structured data)
4. **Improve system prompt:** More detailed instructions

### Improve Reliability

1. **Increase retry_count:** More retry attempts on failure
2. **Increase timeout_seconds:** More time for agent execution
3. **Enable error logging:** Log all failures to PostgreSQL
4. **Monitor confidence scores:** Track classification quality

## Configuration Validation

Before deploying:

1. **Check API keys:** Ensure GROQ_API_KEY and ANTHROPIC_API_KEY set
2. **Validate agents.json:** Ensure proper JSON format
3. **Check agent_class paths:** Verify all classes exist and importable
4. **Review example_queries:** Ensure 5-10 per agent
5. **Test agent execution:** Use CLI to test routing
6. **Monitor logs:** Check for errors in startup

## Configuration Best Practices

1. **Keep agents.json in version control:** Track configuration changes
2. **Use environment variables:** Don't hardcode API keys
3. **Document custom agents:** Add comments explaining purpose
4. **Test configuration changes:** Use CLI before deploying
5. **Monitor performance metrics:** Track latency and success rates
6. **Review example queries regularly:** Keep examples current and relevant
7. **Back up configuration:** Before major changes
