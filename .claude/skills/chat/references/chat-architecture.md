# Chat System Architecture

## Overview

The chat system is a sophisticated multi-agent AI routing platform designed for intelligent query classification and specialized agent execution. It consists of three main layers:

```
React Frontend (Dashboard)
        ↓
Express.js Backend API (Node.js)
        ↓
Python AI Router
    ├─ Semantic Classifier
    ├─ Agent Registry
    └─ 7 Specialized Agents
        └─ LLM APIs (Groq/Anthropic)
```

## Layer 1: Frontend Chat Interface

**Location:** `/frontend/dashboard.jsx` (628 lines, React with Tailwind CSS)

**File Size:** 12KB
**Dependencies:** lucide-react icons, React hooks (useState)

### UI Components Architecture

**Header (Lines 245-282):**
- ELEPHANT logo with branding
- Navigation tabs (Dashboard, Analytics)
- Notification bell with indicator
- Account/Support/Menu buttons

**Connected Sources Panel (Lines 286-317):**
- 5 data source cards: Gmail, Google Drive, Salesforce, Excel, Local Computer
- Each card shows: icon, name, count, status indicator
- "Add New Source" button

**Workflows Sidebar (Lines 322-376):**
- 4 expandable categories (Lookup, Problem Solve, Report, Automation)
- Each category has 3 role-specific example queries
- Toggle expansion to show/hide examples
- Color-coded category icons and backgrounds
- "Add Workflow" button

**Chat Interface (Lines 381-440):**
- Container height: 500px
- Header: "AI Assistant" title + Role selector
- Messages area: scrollable, timestamped, user/AI alternating
- Input area: text field + attachment button + send button

**System Console (Lines 443-476):**
- Container height: 280px
- Dark terminal-style background
- Color-coded log levels (info/success/warn/error)
- Timestamp, level badge, message
- Clear button to reset logs
- Auto-scrolls to latest entries

**Analytics Page (Lines 482-624):**
- 4 metrics cards (Total Queries, Time Saved, Active Users, Automations Run)
- Most Used Workflows chart
- Data Source Usage chart
- ROI Metrics dashboard

### Message Flow

```
User Input
    ↓
Validate (not empty)
    ↓
Display immediately in chat
    ↓
classifyQuery() - regex pattern matching
    ↓
POST to /api/chat endpoint
    ↓
Display AI response
    ↓
Log metrics to console
    ↓
Ready for next message
```

### Frontend Classification (Layer 1)

Uses regex patterns for immediate feedback:

```javascript
- General Chat: /^(hi|hello|hey|good morning|how are you).*/i
- Information Retrieval: /find|search.*candidate|job|placement/i
- Problem Solving: /^(why|analyze|identify).*issue|problem|bottleneck/i
- Automation: /^(automate|workflow|set up).*process|pipeline/i
- Report Generation: /^(generate|create|make|produce).*report|dashboard/i
- Industry Knowledge: /gdpr|ir35|right-to-work|compliance|regulation/i
- Default: general-chat
```

## Layer 2: Backend API

**Location:** `/backend-api/server-fast.js`  
**Port:** 3001 or 3002

### Main Endpoint: POST /api/chat

**Request:**
```json
{
  "message": "user query text",
  "sessionId": "session-uuid",
  "useHistory": true,
  "agent": "agent-type"
}
```

**Response:**
```json
{
  "success": true,
  "message": "LLM response text",
  "metadata": {
    "agent": "information-retrieval",
    "model": "llama-3.3-70b-versatile",
    "tokens": {
      "prompt": 45,
      "completion": 128,
      "total": 173
    },
    "processingTime": 450,
    "sessionId": "session-uuid",
    "historyLength": 12
  }
}
```

### Processing Pipeline

1. Receive POST request with message, sessionId, agent type
2. Validate message not empty
3. Get/create session conversation history (in-memory Map)
4. Select system prompt based on agent type (from `/backend-api/prompts/agent-system-prompts/[agent-type].txt`)
5. Build messages array: [system prompt, previous messages (if useHistory=true), current message]
6. Call Groq API with configuration
7. Receive response from LLM
8. Update conversation history (trim to max 20 messages)
9. Return response with metadata

### LLM Configuration

- **Provider:** Groq
- **Model:** llama-3.3-70b-versatile (default)
- **Temperature:** 0.7 (general chat), 0.3 (structured tasks)
- **Max Tokens:** 2000
- **Top P:** 0.9
- **API Key:** GROQ_API_KEY environment variable

### Other Endpoints

- **GET /health** - System status and API key availability
- **POST /api/chat/clear** - Clear conversation history for session
- **GET /api/chat/stats** - Statistics on active sessions

## Layer 3: AI Router System

**Location:** `/utils/ai_router/`

This is the intelligent routing layer (not currently used by frontend but represents planned architecture).

### Components

1. **Classifier** (`classifier.py`)
   - Semantic classification using sentence-transformers (all-MiniLM-L6-v2)
   - Encodes queries to embeddings
   - Calculates cosine similarity with category examples
   - Returns primary + secondary classifications with confidence

2. **Agent Registry** (`agent_registry.py`)
   - Loads agent configurations from `config/agents.json`
   - Dynamically imports agent classes using Python's importlib
   - Provides get_agent(category) method

3. **Router** (`router.py`)
   - Main orchestrator for routing decisions
   - Handles classification, agent selection, execution, error handling
   - Manages timeout/retry logic (2s timeout, 1 retry)
   - Fallback to General Chat on failure

4. **Storage**
   - **Session Store** (Redis): Stores SessionContext objects with TTL
   - **Log Repository** (PostgreSQL): Logs all routing decisions and metrics

### Router Flow

```
Input Query
    ↓
Create Query object
    ↓
Load session context (Redis)
    ↓
Classify query (semantic)
    ↓
Check confidence >= 0.7
    ├─ NO: Return clarification
    └─ YES: Continue
    ↓
Get agent from registry
    ↓
Execute agent (2s timeout, 1 retry)
    ├─ SUCCESS: Continue
    └─ FAILURE: Fallback to General Chat
    ↓
Save session context (Redis)
    ↓
Log decision (PostgreSQL)
    ↓
Return result with full metadata
```

## Data Models

### Query
```python
@dataclass
class Query:
    id: str                     # UUID
    text: str                   # Query content (max 1000 words)
    user_id: str                # User identifier
    session_id: str             # Session UUID
    timestamp: datetime         # When received
    word_count: int             # Auto-calculated
    truncated: bool             # If > 1000 words
    context_messages: List      # Previous messages
```

### RoutingDecision
```python
@dataclass
class RoutingDecision:
    id: str                         # UUID
    query_id: str                   # Associated query
    primary_category: Category      # Classification result
    primary_confidence: float       # 0.0-1.0
    secondary_category: Category    # Optional secondary match
    secondary_confidence: float     # Secondary confidence
    reasoning: str                  # Why this category
    classification_latency_ms: int  # Processing time
    fallback_triggered: bool        # Confidence < 0.7
    user_override: bool             # User override
    timestamp: datetime             # Decision time
```

### SessionContext
```python
@dataclass
class SessionContext:
    session_id: str                 # UUID
    user_id: str                    # User ID
    created_at: datetime            # Session start
    last_activity_at: datetime      # Last query time
    expires_at: datetime            # Auto-calculated (30 min)
    message_history: List[Dict]     # Max 50 messages
    routing_history: List[str]      # Max 50 decisions
    user_preferences: Dict          # Persistent prefs
    metadata: Dict                  # Additional context
    
    # TTL expires after 30 minutes of inactivity
```

## Complete Message Flow

### Step-by-Step Journey

```
STEP 1: USER INPUT
Input: "Find candidates with Python"
Location: React input field

STEP 2: FRONTEND PROCESSING
├─ Validate message (not empty)
├─ Display in chat immediately
├─ classifyQuery() → regex matching
├─ Result: "information-retrieval"
└─ Log: "User query: Find candidates..."

STEP 3: API CALL
POST http://localhost:3002/api/chat
Body: {
  message: "Find candidates with Python",
  sessionId: "elephant-session-1",
  useHistory: true,
  agent: "information-retrieval"
}

STEP 4: BACKEND RECEIVES
├─ Extract message + sessionId + agent type
├─ Check if sessionId exists
├─ Get or create: conversations[sessionId]
└─ Load conversation history

STEP 5: SYSTEM PROMPT SELECTION
├─ Load: /backend-api/prompts/agent-system-prompts/information-retrieval.txt
└─ Example: "You are information retrieval specialist..."

STEP 6: MESSAGE ARRAY ASSEMBLY
Build array for Groq API:
[
  {role: "system", content: "You are information retrieval..."},
  {role: "user", content: "Previous message from history"},
  {role: "assistant", content: "Previous response from history"},
  ...more history (max 10 exchanges)...,
  {role: "user", content: "Find candidates with Python"}
]

STEP 7: LLM CALL
Start timer
Call Groq API with:
├─ model: "llama-3.3-70b-versatile"
├─ messages: [array from step 6]
├─ temperature: 0.3
├─ max_tokens: 2000
└─ top_p: 0.9

STEP 8: RESPONSE PROCESSING
├─ Extract completion text
├─ Example: "I found 47 candidates with Python skills..."
└─ Calculate latency

STEP 9: HISTORY UPDATE
Update conversations[sessionId]:
├─ Push user message
├─ Push assistant response
└─ Trim history if > 20 messages

STEP 10: RESPONSE ASSEMBLY
Return JSON:
{
  success: true,
  message: "I found 47 candidates...",
  metadata: {
    agent: "information-retrieval",
    model: "llama-3.3-70b-versatile",
    tokens: {prompt: 45, completion: 128, total: 173},
    processingTime: 450,
    sessionId: "elephant-session-1",
    historyLength: 12
  }
}

STEP 11: FRONTEND RECEIVES
├─ Parse JSON
└─ Check success: true

STEP 12: DISPLAY IN CHAT
├─ Add AI message to array
├─ Set text to response
├─ Set timestamp
└─ Render in chat UI

STEP 13: CONSOLE LOGGING
├─ Log: "Agent: information-retrieval"
├─ Log: "Processing time: 450ms"
├─ Log: "Tokens: 173 total"
└─ Log: "Agent response received" (green success)

STEP 14: READY FOR NEXT MESSAGE
└─ Input field cleared and focused
```

## Session Management

### Session Creation
- Triggered by first message in frontend
- SessionId generated as UUID
- Stored in in-memory Map on backend
- Also stored in Redis (AI Router layer)

### Session Persistence
- Messages stored in order
- Trimmed to max 20 messages (10 exchanges)
- Each message: `{role: "user"|"assistant", content: "text"}`
- Older messages removed when limit exceeded

### Session Expiration
- In-memory: Persists while server running
- Redis: TTL of 30 minutes from last activity
- Manual clear: POST /api/chat/clear

## Performance Targets

- **Classification:** <100ms (semantic)
- **Agent execution:** <2s (with timeout)
- **End-to-end:** <3s (95th percentile)
- **Throughput:** 1000+ requests/second
- **Network latency:** ~450ms typical

## Error Handling & Fallback

### Confidence-Based Routing
```
Confidence >= 0.7 → Route to primary agent
Confidence < 0.7 → Return clarification request
```

### Agent Failure Fallback
```
Primary agent fails → Use General Chat agent
                    → Return friendly response
                    → Log failure to PostgreSQL
```

### Timeout Handling
```
Agent exceeds 2s → Retry once (500ms delay)
Still exceeds    → Return error + fallback
Always log       → PostgreSQL metrics
```

## Key Files & Locations

**Frontend:**
- `/frontend/dashboard.jsx` - Main chat UI component

**Backend:**
- `/backend-api/server-fast.js` - Express API server
- `/backend-api/prompts/agent-system-prompts/` - System prompts per agent

**AI Router Core:**
- `/utils/ai_router/router.py` - Main orchestrator
- `/utils/ai_router/classifier.py` - Semantic classification
- `/utils/ai_router/agent_registry.py` - Agent management
- `/utils/ai_router/cli.py` - CLI testing interface

**Models:**
- `/utils/ai_router/models/` - All data model definitions

**Agents:**
- `/utils/ai_router/agents/base_agent.py` - Abstract base class
- `/utils/ai_router/agents/[agent_type]_agent.py` - 7 agent implementations

**Storage:**
- `/utils/ai_router/storage/session_store.py` - Redis backend
- `/utils/ai_router/storage/log_repository.py` - PostgreSQL backend

**Configuration:**
- `/config/agents.json` - All agent configurations
