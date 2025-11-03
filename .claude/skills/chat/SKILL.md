---
name: chat
description: Expert guidance on the ProActive People chat system, including agent architecture, query classification, API integration, and LLM configuration. Answers questions about how the chat interface works, agent routing, model selection, query types, and system design.
---

# Chat System Expert Skill

This skill provides comprehensive expertise on the ProActive People chat system—a production-grade multi-agent AI routing platform. Use this skill when answering questions about:

- **Chat Interface Architecture:** How the frontend chat UI works, message handling, user interactions
- **Agent System:** The 7 specialized agents, their purposes, configurations, and how they're selected
- **Query Classification:** How queries are classified using regex (frontend) and Groq LLM (AI Router)
- **API Integration:** Chat endpoints, request/response formats, error handling
- **LLM Configuration:** Model selection, temperature settings, token management, provider setup
- **Data Flow:** Complete message journey from UI through routing to LLM and back
- **Session Management:** Conversation history, context persistence, session lifecycle
- **Routing Logic:** Confidence thresholds, fallback mechanisms, timeout/retry strategies
- **System Design:** Architecture patterns, performance targets, reliability mechanisms

## Quick Reference

### The 7 Agent Types

The system routes queries to specialized agents based on semantic classification:

1. **General Chat** (P3) - Friendly fallback for casual conversation
2. **Information Retrieval** (P1) - Search/retrieve data from databases, web, industry sources
3. **Problem Solving** (P2) - Complex analysis with evidence-based recommendations
4. **Report Generation** (P3) - Create professional reports with visualizations
5. **Automation** (P2) - Design workflow automation pipelines
6. **Industry Knowledge** (P1) - UK recruitment domain expertise (GDPR, IR35, etc.)
7. **Data Operations** (P1) - Create, update, delete, schedule operations

### Key Files

**Frontend:**
- `/frontend/dashboard.jsx` - Chat UI component

**Backend API:**
- `/backend-api/server-fast.js` - Express API server with `/api/chat` endpoint
- `/backend-api/pythonRouterManager.js` - Python AI Router lifecycle management
- `/backend-api/prompts/agent-system-prompts/[agent-type].txt` - System prompts

**AI Router (Intelligence Layer):**
- `/utils/ai_router/ai_router_api.py` - FastAPI service entry point (persistent server on port 8888) ✨
- `/utils/ai_router/router.py` - Main orchestrator
- `/utils/ai_router/groq_classifier.py` - LLM-based classification (Groq)
- `/utils/ai_router/agent_registry.py` - Agent management
- `/utils/ai_router/agents/` - All 7 agent implementations

**Configuration:**
- `/config/agents.json` - Agent definitions, LLM models, timeouts, examples
- Environment variables: `GROQ_API_KEY`, `ANTHROPIC_API_KEY`

## Architecture Overview

The chat system operates in three layers:

```
React Frontend (Dashboard)
        ↓
Express.js Backend API
        ↓
Python AI Router + LLM APIs
```

### Layer 1: Frontend Implementation

**File:** `/frontend/dashboard.jsx` (628 lines, React with Tailwind CSS)

**UI Architecture:**
- **Header**: ELEPHANT branding, navigation (Dashboard/Analytics), notifications, menu
- **Connected Sources**: 5 data sources panel (Gmail, Drive, Salesforce, Excel, Local)
- **Workflows Sidebar**: 4 collapsible categories with role-specific example queries
- **Role Selector**: Dropdown for 5 roles (Managing Director, Sales, Recruiter, Admin, HR)
- **Chat Container**: Message display area (500px height) + input field
- **System Console**: Dark terminal panel (280px height) with color-coded logs

**State Management:**
```javascript
- activePage: 'dashboard' | 'analytics'
- messages: [{id, type: 'user'|'ai', text, timestamp, metadata}]
- inputMessage: string (current input)
- selectedRole: string (Managing Director|Sales|Recruiter|Admin and Resources|HR)
- expandedCategory: string | null (which workflow category is open)
- consoleLogs: [{id, level: 'info'|'success'|'warn'|'error', message, timestamp}]
```

**Message Flow:**
1. User types in input field (`inputMessage`)
2. Presses Enter or clicks Send button
3. `handleSendMessage()` executes:
   - Validates message not empty
   - Creates `{type: 'user', text, timestamp}` and adds to messages
   - Calls `classifyQuery(message)` for regex classification
   - Logs to console: classification result
   - Clears input field
   - POSTs to `http://localhost:3002/api/chat`:
     ```json
     {
       "message": "query text",
       "sessionId": "elephant-session-1",
       "useHistory": true,
       "agent": "classified-agent-type"
     }
     ```
   - Times API call for latency measurement
   - Receives response
   - Creates `{type: 'ai', text: response.message, timestamp, metadata}`
   - Logs metadata: agent, confidence, processing time, network latency

**Regex Classification (Lines 103-139):**
```javascript
classifyQuery(query):
  - /^(hi|hello|hey|good morning|...)[\s\?]*$/i → 'general-chat'
  - /^(find|search|show|list|...).*candidate|job|placement/ → 'information-retrieval'
  - /^(why|analyze|identify|find|...).*issue|problem|bottleneck/ → 'problem-solving'
  - /^(automate|workflow|set up|create|...).*workflow|process/ → 'automation'
  - /^(generate|create|make|produce|...).*report|dashboard/ → 'report-generation'
  - /^(what|tell me|explain|...).*gdpr|ir35|compliance/ → 'industry-knowledge'
  - default: 'general-chat'
```

**Workflow Categories & Examples:**
5 roles × 4 categories = 20 predefined example queries. Examples like:
- Recruiter → Lookup: "Find tech candidates with 5+ years experience"
- Recruiter → Problem Solve: "Why are we losing candidates at offer stage?"
- Sales → Lookup: "Find all active client contracts"
- Managing Director → Problem Solve: "Why is employee turnover increasing?"

**System Console Logging (Lines 93-101):**
Each log entry has: timestamp (HH:MM:SS), level, message
- INFO (blue): User query, routing info, classification
- SUCCESS (green): Agent response received
- WARN (yellow): Attempted agent, connection warnings
- ERROR (red): Routing failed, connection errors

### Layer 2: Backend API Implementation

**File:** `/backend-api/server.js` (239 lines, Express.js)

**Initialization (Lines 1-59):**
- Port: 3001 or from `BACKEND_PORT` env var
- CORS enabled
- Groq client initialized with `GROQ_API_KEY`
- System prompts loaded from `/backend-api/prompts/agent-system-prompts/[agent-type].txt`
- 6 agent types supported: general-chat, information-retrieval, problem-solving, automation, report-generation, industry-knowledge
- In-memory `conversations` Map for session storage

**Chat Endpoint (Lines 75-179):**
```javascript
POST /api/chat

Request:
{
  message: string (required, max 1000 words)
  sessionId: string (default: 'default')
  useHistory: boolean (default: true)
  agent: string (default: 'general-chat')
}

Processing (Lines 76-148):
1. Validate message not empty (400 if empty)
2. Log request with sessionId, agent, message preview
3. Get or create conversation history from Map
4. Select system prompt by agent type
5. Build messages array:
   - [{role: 'system', content: systemPrompt}]
   - [...previous history messages if useHistory=true]
   - [{role: 'user', content: message}]
6. Call Groq API with config:
   - model: 'llama-3.3-70b-versatile'
   - temperature: 0.7 (general-chat) | 0.3 (other agents)
   - max_tokens: 2000
   - top_p: 0.9
7. Extract response: completion.choices[0].message.content
8. Update history: append user + assistant messages
9. Trim history to max 20 messages (10 exchanges)

Response:
{
  success: true,
  message: "AI response text",
  metadata: {
    agent: "information-retrieval",
    model: "llama-3.3-70b-versatile",
    tokens: {prompt: 45, completion: 128, total: 173},
    processingTime: 450,
    sessionId: "elephant-session-1",
    historyLength: 12
  }
}
```

**Other Endpoints:**
- `POST /api/chat/clear` (Lines 182-195): Delete session history
- `GET /api/chat/stats` (Lines 198-209): Return session statistics
- `GET /health` (Lines 65-72): Health check

**Server Startup (Lines 222-238):**
Displays banner:
```
╔════════════════════════════════════════════════════════╗
║        🐘 ELEPHANT AI BACKEND SERVER RUNNING 🐘        ║
╚════════════════════════════════════════════════════════╝
  ✓ Server:      http://localhost:3002
  ✓ Health:      http://localhost:3002/health
  ✓ Chat API:    POST http://localhost:3002/api/chat
  ✓ GROQ Model:  llama-3.3-70b-versatile
```

### Layer 3: AI Router (Intelligent Routing)

The AI Router (Python) provides intelligent query routing:
1. Classifies queries using **GroqClassifier** (LLM-based intent analysis)
2. Looks up appropriate agent from registry
3. Executes agent with timeout/retry protection
4. Falls back to General Chat on failures
5. Logs all decisions to PostgreSQL
6. Stores session context in Redis

**Routing Method:** Uses Groq LLM (llama-3.3-70b-versatile) to analyze query intent and classify into one of 7 categories with confidence scoring and reasoning.

> **Note:** For detailed information about query classification, routing decisions, confidence thresholds, and debugging routing issues, see the **`router` skill** documentation.

## Classification System

### Frontend Layer (Regex)

Regex patterns for immediate feedback (no network latency):
- `general-chat`: Greetings (hi, hello, how are you)
- `information-retrieval`: Keywords (find, search, candidates, jobs)
- `problem-solving`: Keywords (analyze, identify, problem, issue)
- `automation`: Keywords (automate, workflow, process)
- `report-generation`: Keywords (generate, create, report, dashboard)
- `industry-knowledge`: Keywords (GDPR, IR35, compliance, regulation)
- `data-operations`: Keywords (create, update, delete, schedule)
- **Default:** Falls back to general-chat

See `references/query-classification.md` for exact regex patterns.

### AI Router Layer (GroqClassifier - LLM-Based)

For intelligent classification, the AI Router uses **GroqClassifier**:
- **Model:** llama-3.3-70b-versatile (Groq LLM)
- **Method:** LLM analyzes query intent and context
- **Output:** JSON with category, confidence, and reasoning
- **Confidence:** Returns primary category + confidence (0.0-1.0)
- **Threshold:** Routes if confidence >= 0.65; otherwise falls back to General Chat

**Example Classification:**

Query: "Find candidates with Python skills in Bristol"

```json
{
  "category": "INFORMATION_RETRIEVAL",
  "confidence": 0.92,
  "reasoning": "Query explicitly requests finding/searching for candidates with specific technical skills in a location, which is information retrieval from external sources."
}
```

**Result:** Routes to Information Retrieval Agent (confidence 92% > 65% threshold)

> **For more details on classification logic, see the `router` skill** which provides comprehensive guidance on query analysis, confidence scoring, debugging routing decisions, and testing classification.

## API Endpoint Reference

### Main Endpoint: POST /api/chat

Send chat messages and receive AI responses.

**Request:**
```json
{
  "message": "Find candidates with Python",
  "sessionId": "user-session-123",
  "useHistory": true,
  "agent": "information-retrieval"
}
```

**Response:**
```json
{
  "success": true,
  "message": "I found 47 candidates with Python skills...",
  "metadata": {
    "agent": "information-retrieval",
    "model": "llama-3.3-70b-versatile",
    "tokens": {"prompt": 45, "completion": 128, "total": 173},
    "processingTime": 450,
    "sessionId": "user-session-123",
    "historyLength": 12
  }
}
```

**Fields:**
- `message`: User query (required, max 1000 words)
- `sessionId`: Unique session identifier (required)
- `useHistory`: Include conversation history (optional, default true)
- `agent`: Force specific agent (optional; overrides auto-detection)

See `references/api-endpoints.md` for complete endpoint documentation including `/api/chat/clear`, `/api/chat/stats`, and error handling.

## Configuration (agents.json)

All agents defined in `/config/agents.json`:

```json
{
  "INFORMATION_RETRIEVAL": {
    "name": "Information Retrieval",
    "priority": 1,
    "agent_class": "utils.ai_router.agents.information_retrieval_agent:InformationRetrievalAgent",
    "llm_provider": "groq",
    "llm_model": "llama-3-70b-8192",
    "timeout_seconds": 2,
    "retry_count": 1,
    "retry_delay_ms": 500,
    "tools": ["web_search", "database_query"],
    "enabled": true,
    "example_queries": ["Find candidates with Python", "Show me active jobs in London", ...]
  }
}
```

**Key Configuration Fields:**

- `llm_provider`: "groq" or "anthropic"
- `llm_model`: Model identifier (e.g., "llama-3-70b-8192")
- `timeout_seconds`: Max agent execution time (standard: 2)
- `retry_count`: Automatic retries (standard: 1)
- `temperature`: Controls randomness (0.3=factual, 0.7=creative)
- `example_queries`: 5-10 examples for LLM classification (used by GroqClassifier)
- `enabled`: Can be toggled true/false without restart

See `references/configuration.md` for complete configuration reference.

## LLM Models

### Groq Models (Faster, Cost-Effective)

- **llama-3-70b-8192** (most common)
- **llama-3.3-70b-versatile** (latest Llama)
- Used by: Information Retrieval, Automation, Report Generation, Industry Knowledge, General Chat

### Anthropic Models (Superior Reasoning)

- **claude-3-5-sonnet-20241022** (best reasoning, used by Problem Solving)
- **claude-3-opus-20240229** (most capable but slower)
- **claude-3-haiku-20240307** (fastest)

## Performance Targets

- **Classification latency:** <500ms (GroqClassifier LLM) or <1ms (frontend regex)
- **Agent execution:** <2s (with timeout)
- **End-to-end:** <3s (95th percentile)
- **Throughput:** 1000+ req/s
- **Network latency:** ~450ms typical

## Error Handling & Fallback

### Confidence-Based Routing

```
Confidence >= 0.65  → Route to primary agent
Confidence < 0.65   → Return clarification request
                       Fall back to General Chat
```

**Note:** The confidence threshold (0.65) is configurable in GroqClassifier. See the `router` skill for threshold tuning guidance.

### Agent Failure Recovery

```
Agent fails or timeout  → Retry once (500ms delay)
Still fails             → Fallback to General Chat
                          Return friendly response
```

### Session Management

- **Storage:** Redis (via AI Router) for persistent session context
- **Fallback:** In-memory storage if Redis unavailable (development mode)
- **History:** Conversation context maintained across queries
- **Format:** Session context includes previous agent and conversation history
- **Expiration:** Configurable TTL in Redis (default: session-based)

## Common Tasks

### How to Add a New Agent

1. Create agent class in `/utils/ai_router/agents/[name]_agent.py`
2. Inherit from `BaseAgent`
3. Implement `process(request: AgentRequest) -> AgentResponse`
4. Add to `/config/agents.json` with configuration
5. Provide 5-10 diverse example queries (used by GroqClassifier for category descriptions)
6. Test classification using the `router` skill's testing tools

### How to Change an Agent's LLM Model

1. Open `/config/agents.json`
2. Find the agent
3. Change `llm_model` field to desired model
4. If using different provider, also change `llm_provider`
5. Restart backend server

### How to Disable an Agent

1. Open `/config/agents.json`
2. Find the agent
3. Set `enabled` to `false`
4. Queries won't be routed here; will use secondary/fallback
5. No server restart needed

### How to Debug Query Routing

**For detailed routing debugging, use the `router` skill** which provides comprehensive testing tools.

Quick debugging steps:
1. Check frontend console logs (classification result + regex pattern)
2. Check system console in chat UI (shows classification + confidence)
3. Check backend server logs (routing decision, agent execution)
4. Use CLI: `python -m utils.ai_router.cli "query text" --json`
5. Check latency metrics and reasoning in response metadata

### How to Improve Classification Accuracy

1. Add more example queries to `example_queries` in agents.json
2. Use specific, diverse, realistic examples
3. Include domain-specific terminology
4. Cover edge cases and variations
5. Monitor classification accuracy over time

## Reference Documents

- **information_retrieval_flow.md** - Complete NL2SQL query flow with code examples ✨ NEW
- **frontend-backend-implementation.md** - Actual code implementation details, state management, message flow
- **chat-architecture.md** - Complete system architecture and data flow
- **agent-types.md** - Detailed specifications for all 7 agents
- **api-endpoints.md** - Complete API documentation with examples
- **configuration.md** - Configuration file reference and tuning guide
- **query-classification.md** - Classification system details and patterns

**See also**:
- `INFORMATION_RETRIEVAL_FLOW_GUIDE.md` (project root) - 12-step trace from query → SQL → display
- Router skill's `complete_system_architecture.md` - Full system architecture reference

## Key Concepts

**Agent Contract:** All agents must respect 2-second timeout, handle exceptions gracefully, return AgentResponse with success/error.

**Confidence Threshold:** GroqClassifier uses 0.65 (65%) threshold; below this triggers fallback to General Chat.

**Session Continuity:** Session context stored in Redis with conversation history and previous agent context.

**Temperature Settings:** Control LLM randomness (0.3=factual, 0.7=creative); varies by agent type and task.

**Fallback Chain:** When primary agent fails, system automatically falls back to General Chat agent.

**LLM Classification:** GroqClassifier uses Groq LLM (llama-3.3-70b-versatile) to analyze query intent, providing category, confidence score, and reasoning in JSON format.

**Classification Prompt:** Uses prompts from `prompts/ai_router_classification.json` with category descriptions and examples from `config/agents.json`.

## When to Use This Skill

**Use this skill for questions about:**
- "How does the chat interface work?"
- "What agents are available and when are they used?"
- "What API endpoints are available?"
- "How do I configure an agent?"
- "How does conversation history work?"
- "What are the performance targets?"
- "How do I add a new agent?"
- "What LLM models are being used?"
- "What happens when an agent times out?"
- "What temperature settings should I use?"
- "How do I change which LLM an agent uses?"
- "How does NL2SQL work in Information Retrieval?" ✨
- "What is the exec_sql function?" ✨
- "How do queries get translated to SQL?" ✨

**Use the `router` skill for query classification and routing questions:**
- "How are queries classified and routed?"
- "How does GroqClassifier work?"
- "How do I debug routing issues?"
- "How can I improve classification accuracy?"
- "What confidence threshold should I use?"
- "How do I test query classification?"
- "Why did my query route to the wrong agent?"

This skill provides the expert knowledge to answer questions about the chat system architecture, API integration, and agent configuration. For detailed routing analysis and classification debugging, refer to the `router` skill.
