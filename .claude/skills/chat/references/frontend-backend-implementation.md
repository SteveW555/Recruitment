# Frontend & Backend Implementation Details

## Frontend Implementation

**File:** `/frontend/dashboard.jsx`
**Size:** 628 lines, 12KB
**Framework:** React 18 with Tailwind CSS
**Dependencies:** lucide-react (icons), React hooks (useState)

### State Management

```javascript
// Main component state
const [activePage, setActivePage] = useState('dashboard');
const [messages, setMessages] = useState([...]);
const [inputMessage, setInputMessage] = useState('');
const [expandedCategory, setExpandedCategory] = useState(null);
const [selectedRole, setSelectedRole] = useState('Recruiter');
const [consoleLogs, setConsoleLogs] = useState([...]);
```

**State Variables:**
- `activePage`: Current page view (dashboard or analytics)
- `messages`: Array of message objects {id, type, text, timestamp, metadata}
- `inputMessage`: Current text in input field
- `expandedCategory`: Which workflow category is open (lookup, problem-solve, report, automation)
- `selectedRole`: Currently selected user role
- `consoleLogs`: Array of system log entries {id, level, message, timestamp}

### Message Data Structure

**User Message:**
```javascript
{
  id: number,
  type: 'user',
  text: 'user query text',
  timestamp: 'HH:MM'
}
```

**AI Response Message:**
```javascript
{
  id: number,
  type: 'ai',
  text: 'response text',
  timestamp: 'HH:MM',
  metadata: {
    agent: 'agent-type',
    confidence: 0.92,
    classification: 'information-retrieval',
    processingTime: 450,
    // ... more metadata
  }
}
```

### Query Classification Function

**Location:** Lines 103-139

```javascript
classifyQuery(query) {
  const lowerQuery = query.toLowerCase();

  // General chat - greetings
  if (/^(hi|hello|hey|good morning|good afternoon|good evening|how are you|whats up|sup|greetings)[\s\?]*$/i.test(lowerQuery))
    return 'general-chat';

  // Information retrieval - find/search + data
  if (/^(find|search|show|list|who|where|what|how many|give me|tell me).*(candidate|job|placement|open|available|contact|email|phone)/i.test(query) ||
      /^(find|search).*(with|having|that have).*(skill|experience|years|salary|location)/i.test(query))
    return 'information-retrieval';

  // Problem solving - analysis
  if (/^(why|analyze|identify|find|what.*issue|what.*problem|what.*challenge|what.*bottleneck|suggest|recommend|solve).*(is|are|we|our|the)/i.test(query))
    return 'problem-solving';

  // Automation - workflow design
  if (/^(automate|workflow|set up|create|design|build).*(workflow|automation|process|pipeline|trigger|action)/i.test(query))
    return 'automation';

  // Report generation - reporting
  if (/^(generate|create|make|produce|compile|report|summary|dashboard|analytics|metrics|performance)/i.test(query))
    return 'report-generation';

  // Industry knowledge - regulations
  if (/^(what|tell me|explain|clarify|gdpr|ir35|right-to-work|employment law|compliance|regulation|standard|best practice|guideline)/i.test(query))
    return 'industry-knowledge';

  // Default fallback
  return 'general-chat';
}
```

### Message Send Handler

**Location:** Lines 141-240 (`handleSendMessage` function)

**Execution Steps:**

1. **Validation (Line 142):**
   - Check if inputMessage is not empty

2. **Immediate UI Update (Lines 148-153):**
   - Create user message object
   - Add to messages array immediately (optimistic UI)
   - Log user query to console
   - Clear input field

3. **Classification (Lines 164-166):**
   - Call `classifyQuery(userMessage)`
   - Get agent type
   - Log classification to console

4. **API Call (Lines 161-180):**
   - Record start time with `performance.now()`
   - POST to `http://localhost:3002/api/chat` with:
     ```json
     {
       "message": userMessage,
       "sessionId": "elephant-session-1",
       "useHistory": true,
       "agent": agentType
     }
     ```

5. **Response Processing (Lines 182-212):**
   - Calculate network latency: `(endTime - startTime)`
   - Parse response JSON
   - Extract metadata fields
   - Create AI message object with metadata
   - Add to messages array
   - Log all metadata to console:
     - Agent type
     - Confidence score
     - Classification result
     - Processing time
     - Network latency
     - Success status

6. **Error Handling (Lines 213-239):**
   - On error: add error message to chat
   - Log error details to console
   - Show friendly error message to user

### Role-Based Example Queries

**Location:** Lines 29-60

**Roles:** Managing Director, Sales, Recruiter, Admin and Resources, HR

**Categories per Role:**
1. **lookup** (3 queries): Find/search/locate data
2. **problemSolve** (3 queries): Analyze/identify/improve issues
3. **report** (3 queries): Generate/create/compile reports
4. **automation** (3 queries): Auto-send/schedule/set up workflows

**Example - Recruiter Role:**
```javascript
'Recruiter': {
  lookup: [
    'Find tech candidates with 5+ years experience',
    'Search for active job openings',
    'Locate candidate interview feedback'
  ],
  problemSolve: [
    'Why are we losing candidates at offer stage?',
    'Identify recruitment bottlenecks',
    'Analyze time-to-hire trends'
  ],
  report: [
    'Generate monthly placement report',
    'Create candidate pipeline summary',
    'Compile recruiter performance metrics'
  ],
  automation: [
    'Auto-send candidate follow-up emails',
    'Schedule interview reminders',
    'Set up candidate status updates'
  ]
}
```

### Console Logging Function

**Location:** Lines 93-101 (`addLog` function)

```javascript
addLog(message, level = 'info') {
  const timestamp = new Date().toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false
  });
  setConsoleLogs(prev => [...prev, {
    id: prev.length + 1,
    level,  // 'info' | 'success' | 'warn' | 'error'
    message,
    timestamp
  }]);
}
```

**Log Levels:**
- `'info'` (blue): Classification, routing, debug info
- `'success'` (green): Successful agent responses
- `'warn'` (yellow): Warnings, fallbacks
- `'error'` (red): Errors, failures

### UI Layout

**Grid Structure (Line 320):**
```
grid grid-cols-4 gap-6
├─ Sidebar (col-span-1): Workflows
└─ Chat Container (col-span-3):
   ├─ Chat Interface (500px height)
   └─ System Console (280px height)
```

**Styling:**
- Colors: Tailwind CSS utility classes
- Rounded corners: `rounded-2xl` (16px)
- Shadows: `shadow-sm`
- Spacing: `gap-6`, `p-6`, `mb-6`
- Responsive: Grid-based layout

---

## Backend API Implementation

**File:** `/backend-api/server.js`
**Size:** 239 lines, 8KB
**Framework:** Express.js with Node.js
**Dependencies:** express, cors, dotenv, groq-sdk, fs, fileURLToPath

### Initialization

**Location:** Lines 1-59

**Configuration:**
```javascript
- PORT: process.env.BACKEND_PORT || 3001
- CORS: Enabled for all origins
- Groq Client: Initialized with GROQ_API_KEY
- System Prompts: Loaded from /backend-api/prompts/agent-system-prompts/
- Session Storage: In-memory Map() for conversations
```

**Loaded Agent Types:**
```javascript
AGENT_TYPES = [
  'general-chat',
  'information-retrieval',
  'problem-solving',
  'automation',
  'report-generation',
  'industry-knowledge'
]
```

**System Prompts Loading (Lines 35-43):**
Each agent has separate `.txt` file in `/backend-api/prompts/agent-system-prompts/`
- Loaded into `SYSTEM_PROMPTS` object
- Fallback to default general-chat prompt
- Console logs success/failure for each

### Session Management

**Location:** Line 62

```javascript
const conversations = new Map();
// Key: sessionId
// Value: Array of message objects {role, content}
```

**Message Format:**
```javascript
{
  role: 'user' | 'assistant',
  content: 'message text'
}
```

**History Trimming:**
- Max 20 messages per session (10 exchanges)
- When limit exceeded: remove oldest messages
- Prevents memory bloat

### Health Check Endpoint

**Location:** Lines 65-72

```javascript
GET /health

Response:
{
  status: 'ok',
  service: 'Elephant AI Backend',
  groq: true,  // boolean: API key present
  timestamp: '2024-10-23T14:35:22.123Z'
}
```

### Chat Endpoint

**Location:** Lines 75-179

**Request Processing:**

1. **Validation (Lines 79-83):**
   - Require non-empty message
   - Return 400 if empty

2. **Session Setup (Lines 93-96):**
   - Get existing conversation history from Map
   - Create new empty array if session doesn't exist
   - Default sessionId: 'default'

3. **System Prompt Selection (Line 99):**
   - Look up prompt by agent type
   - Fall back to default if not found

4. **Message Assembly (Lines 102-118):**
   ```javascript
   messages = [
     {role: 'system', content: systemPrompt},
     ...history (if useHistory=true),
     {role: 'user', content: message}
   ]
   ```

5. **Groq API Call (Lines 121-128):**
   ```javascript
   await groq.chat.completions.create({
     model: 'llama-3.3-70b-versatile',
     messages: messages,
     temperature: agent === 'general-chat' ? 0.7 : 0.3,
     max_tokens: 2000,
     top_p: 0.9
   })
   ```

6. **History Update (Lines 134-148):**
   - Append user message to history
   - Append assistant response to history
   - Trim to max 20 messages if exceeded
   - Keep newest messages, remove oldest

7. **Response Assembly (Lines 153-168):**
   ```javascript
   {
     success: true,
     message: assistantMessage,
     metadata: {
       agent: agentType,
       model: completion.model,
       tokens: {
         prompt: completion.usage.prompt_tokens,
         completion: completion.usage.completion_tokens,
         total: completion.usage.total_tokens
       },
       processingTime: responseTime,
       sessionId: sessionId,
       historyLength: history.length
     }
   }
   ```

### LLM Configuration

**Groq Settings:**
- **Model:** `llama-3.3-70b-versatile`
- **Temperature:**
  - 0.7 for general-chat (conversational, more creative)
  - 0.3 for other agents (factual, structured)
- **Max Tokens:** 2000 (max response length)
- **Top P:** 0.9 (nucleus sampling)

### Clear Endpoint

**Location:** Lines 182-195

```javascript
POST /api/chat/clear

Request:
{
  "sessionId": "session-id"
}

Response:
{
  success: true,
  message: "Conversation history cleared",
  sessionId: "session-id"
}
```

### Statistics Endpoint

**Location:** Lines 198-209

```javascript
GET /api/chat/stats

Response:
{
  totalSessions: 3,
  sessions: [
    {
      sessionId: "elephant-session-1",
      messageCount: 24,
      lastActivity: "2024-10-23T14:35:22.123Z"
    },
    ...
  ]
}
```

### Error Handling

**Location:** Lines 170-179, 212-219

- Try-catch on Groq API call
- 500 status on error
- Error details in response
- Middleware error handler logs unhandled errors

### Server Startup

**Location:** Lines 222-238

**Banner Display:**
```
╔════════════════════════════════════════════════════════╗
║        🐘 ELEPHANT AI BACKEND SERVER RUNNING 🐘        ║
╚════════════════════════════════════════════════════════╝
  ✓ Server:      http://localhost:3002
  ✓ Health:      http://localhost:3002/health
  ✓ Chat API:    POST http://localhost:3002/api/chat
  ✓ GROQ Model:  llama-3.3-70b-versatile
```

---

## Data Flow: Complete Journey

### Step 1: User Input
- User types in React input field
- Input stored in `inputMessage` state
- User presses Enter or clicks Send

### Step 2: Frontend Processing
- Validate message not empty
- Create user message object
- Add to `messages` state (immediate display)
- Clear `inputMessage`
- Call `classifyQuery()` → get agent type
- Log to console: user query + classification

### Step 3: API Request
- Record start time: `performance.now()`
- POST to `http://localhost:3002/api/chat`:
  ```json
  {
    "message": "user query",
    "sessionId": "elephant-session-1",
    "useHistory": true,
    "agent": "classified-agent"
  }
  ```

### Step 4: Backend Processing
- Validate request
- Log request details
- Get session history from Map
- Select system prompt by agent type
- Build messages array: [system, ...history, current]
- Record start time: `Date.now()`
- Call Groq API with LLM config

### Step 5: LLM Processing
- Groq receives request
- Llama-3.3-70b-versatile generates response
- Based on system prompt + message context
- Applied temperature setting (0.3 or 0.7)
- Max 2000 tokens output

### Step 6: Backend Response
- Extract response text
- Calculate processing time
- Update session history: add user + response
- Trim history if > 20 messages
- Return JSON with response + metadata

### Step 7: Frontend Response
- Receive and parse response
- Calculate network latency: `endTime - startTime`
- Extract metadata
- Create AI message object with metadata
- Add to `messages` state (display immediately)
- Log all metadata to console

### Step 8: User Sees Result
- Chat displays AI response
- System Console shows:
  - Agent used
  - Processing time
  - Network latency
  - Token counts
  - Classification details
- Ready for next message

---

## Key Implementation Patterns

### Optimistic UI Updates
- Frontend adds user message immediately
- Doesn't wait for API response
- Better UX: no delay in chat

### Regex-Based Classification
- Fast, no ML model needed
- Pattern matching on client-side
- No network overhead
- Fallback to general-chat

### In-Memory Session Storage
- Fast access (no database)
- Perfect for development
- Conversation lost on server restart
- Not suitable for production (use Redis/database)

### Async-Await Pattern
- `handleSendMessage()` is async
- Await Groq API response
- Non-blocking UI updates

### Error Boundaries
- Try-catch on API call
- Graceful error messages
- Users always get response
- Logs captured in console
