---
name: chat
description: Expert guidance on the ProActive People chat system, including agent architecture, query classification, API integration, and LLM configuration. Answers questions about how the chat interface works, agent routing, model selection, query types, and system design.
---

# Chat System Expert Skill

This skill provides comprehensive expertise on the ProActive People chat system—a production-grade multi-agent AI routing platform. Use this skill when answering questions about:

- **Chat Interface Architecture:** How the frontend chat UI works, message handling, user interactions
- **Agent System:** The 7 specialized agents, their purposes, configurations, and how they're selected
- **Query Classification:** How queries are classified using regex (frontend) and semantic ML (AI Router)
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
- `/backend-api/server.js` - Express API server with `/api/chat` endpoint
- `/backend-api/prompts/agent-system-prompts/[agent-type].txt` - System prompts

**AI Router (Intelligence Layer):**
- `/utils/ai_router/router.py` - Main orchestrator
- `/utils/ai_router/classifier.py` - Semantic classification (ML)
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

The AI Router (Python) represents the planned intelligent routing layer:
1. Classifies queries using sentence-transformers (semantic ML)
2. Looks up appropriate agent from registry
3. Executes agent with timeout/retry protection
4. Falls back to General Chat on failures
5. Logs all decisions to PostgreSQL
6. Stores session context in Redis

**Currently:** Frontend uses simple regex; backend routes based on agent parameter
**Future:** Full AI Router integration for semantic routing

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

### AI Router Layer (Semantic ML)

For intelligent classification, the AI Router uses:
- **Model:** all-MiniLM-L6-v2 sentence transformer
- **Method:** Encodes query and example queries to 384-dimensional vectors
- **Similarity:** Calculates cosine similarity to find best match
- **Confidence:** Returns primary category + confidence (0.0-1.0)
- **Threshold:** Routes if confidence >= 0.7; otherwise clarifies

Example: "Find candidates with Python"
- Information Retrieval: 0.92 ✓ (confidence 92%, route here)
- Problem Solving: 0.34
- Others: <0.3

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
- `example_queries`: 5-10 examples for semantic classification
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

- **Classification latency:** <100ms (semantic) or <1ms (regex)
- **Agent execution:** <2s (with timeout)
- **End-to-end:** <3s (95th percentile)
- **Throughput:** 1000+ req/s
- **Network latency:** ~450ms typical

## Error Handling & Fallback

### Confidence-Based Routing

```
Confidence >= 0.7  → Route to primary agent
Confidence < 0.7   → Return clarification request
                      Fall back to General Chat
```

### Agent Failure Recovery

```
Agent fails or timeout  → Retry once (500ms delay)
Still fails             → Fallback to General Chat
                          Return friendly response
```

### Session Management

- **In-Memory:** Conversations Map on backend (persists while server running)
- **Storage:** Max 20 messages per session (trimmed oldest)
- **Format:** `{role: "user"|"assistant", content: "text"}`
- **Expiration:** Manually cleared with `/api/chat/clear` endpoint

## Common Tasks

### How to Add a New Agent

1. Create agent class in `/utils/ai_router/agents/[name]_agent.py`
2. Inherit from `BaseAgent`
3. Implement `process(request: AgentRequest) -> AgentResponse`
4. Add to `/config/agents.json` with configuration
5. Create system prompt at `/backend-api/prompts/agent-system-prompts/[name].txt`
6. Provide 5-10 example queries for semantic classification

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

1. Check frontend console logs (classification result + regex pattern)
2. Check system console in chat UI (shows classification + confidence)
3. Check backend server logs (routing decision, agent execution)
4. Use CLI: `python utils/ai_router/cli.py "query text"`
5. Check latency metrics in response metadata

### How to Improve Classification Accuracy

1. Add more example queries to `example_queries` in agents.json
2. Use specific, diverse, realistic examples
3. Include domain-specific terminology
4. Cover edge cases and variations
5. Monitor classification accuracy over time

## Reference Documents

- **frontend-backend-implementation.md** - Actual code implementation details, state management, message flow
- **chat-architecture.md** - Complete system architecture and data flow
- **agent-types.md** - Detailed specifications for all 7 agents
- **api-endpoints.md** - Complete API documentation with examples
- **configuration.md** - Configuration file reference and tuning guide
- **query-classification.md** - Classification system details and patterns

## Key Concepts

**Agent Contract:** All agents must respect 2-second timeout, handle exceptions gracefully, return AgentResponse with success/error.

**Confidence Threshold:** Routing decisions use 0.7 (70%) threshold; below this triggers clarification or fallback.

**Session Continuity:** Each session maintains message history up to 20 messages (10 exchanges); older messages trimmed.

**Temperature Settings:** Control LLM randomness (0.3=factual, 0.7=creative); varies by agent type and task.

**Fallback Chain:** When primary agent fails, system automatically falls back to General Chat agent.

**Semantic Classification:** Uses sentence embeddings to find similar queries in agent examples; captures meaning beyond keywords.

## When to Use This Skill

Ask questions about:
- "How does the chat interface work?"
- "What agents are available and when are they used?"
- "How are queries classified and routed?"
- "What API endpoints are available?"
- "How do I configure an agent?"
- "How does conversation history work?"
- "What are the performance targets?"
- "How do I add a new agent?"
- "What LLM models are being used?"
- "How does semantic classification work?"
- "What happens when an agent times out?"
- "How do I debug routing issues?"
- "How can I improve classification accuracy?"
- "What temperature settings should I use?"
- "How do I change which LLM an agent uses?"

This skill provides the expert knowledge to answer any question about how the chat system works.
