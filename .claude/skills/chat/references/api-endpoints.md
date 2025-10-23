# Chat System API Reference

## Base URL
```
http://localhost:3002
```

## Authentication
Currently no authentication required (development mode). Production should implement JWT bearer token authentication.

---

## Endpoints

### 1. POST /api/chat

Main endpoint for sending chat messages and receiving AI responses.

#### Request

```http
POST /api/chat HTTP/1.1
Host: localhost:3002
Content-Type: application/json

{
  "message": "Find candidates with Python",
  "sessionId": "elephant-session-1",
  "useHistory": true,
  "agent": "information-retrieval"
}
```

**Request Body Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `message` | string | Yes | User query text (max 1000 words) |
| `sessionId` | string | Yes | Unique session identifier (UUID format) |
| `useHistory` | boolean | No | Include conversation history in context (default: true) |
| `agent` | string | No | Force specific agent type (optional; overrides auto-detection) |

**Agent Type Values:**
- `"general-chat"`
- `"information-retrieval"`
- `"problem-solving"`
- `"report-generation"`
- `"automation"`
- `"industry-knowledge"`
- `"data-operations"`

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "I found 47 candidates with Python skills in the London area...",
  "metadata": {
    "agent": "information-retrieval",
    "model": "llama-3.3-70b-versatile",
    "tokens": {
      "prompt": 45,
      "completion": 128,
      "total": 173
    },
    "processingTime": 450,
    "sessionId": "elephant-session-1",
    "historyLength": 12
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the request was successful |
| `message` | string | The AI-generated response text |
| `metadata` | object | Response metadata (see below) |

**Metadata Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `agent` | string | Which agent handled the query |
| `model` | string | LLM model used |
| `tokens.prompt` | number | Tokens in prompt (input) |
| `tokens.completion` | number | Tokens in completion (output) |
| `tokens.total` | number | Total tokens used |
| `processingTime` | number | Milliseconds from request to response |
| `sessionId` | string | Session identifier |
| `historyLength` | number | Number of messages in conversation history |

#### Response Examples

**Success - Information Retrieval:**
```json
{
  "success": true,
  "message": "Found 47 candidates:\n- John Smith (Python, 5 yrs)\n- Jane Doe (Python, 3 yrs)...",
  "metadata": {
    "agent": "information-retrieval",
    "model": "llama-3.3-70b-versatile",
    "tokens": {"prompt": 45, "completion": 128, "total": 173},
    "processingTime": 450,
    "sessionId": "elephant-session-1",
    "historyLength": 12
  }
}
```

**Success - Problem Solving:**
```json
{
  "success": true,
  "message": "## Problem Analysis\n\n### Root Causes\n1. High candidate dropout (45%) vs industry avg (25%)...",
  "metadata": {
    "agent": "problem-solving",
    "model": "claude-3-5-sonnet-20241022",
    "tokens": {"prompt": 120, "completion": 456, "total": 576},
    "processingTime": 1200,
    "sessionId": "elephant-session-1",
    "historyLength": 8
  }
}
```

**Success - General Chat (Fallback):**
```json
{
  "success": true,
  "message": "Hello! I'm here to help with your recruitment queries. I can assist with finding candidates, scheduling interviews, analyzing market trends, and much more.",
  "metadata": {
    "agent": "general-chat",
    "model": "llama-3-70b-8192",
    "tokens": {"prompt": 20, "completion": 45, "total": 65},
    "processingTime": 150,
    "sessionId": "elephant-session-1",
    "historyLength": 2
  }
}
```

**Error - Empty Message:**
```json
{
  "success": false,
  "message": null,
  "error": "Message cannot be empty"
}
```

**Error - Invalid Session:**
```json
{
  "success": false,
  "message": null,
  "error": "Invalid sessionId format"
}
```

**Error - Timeout:**
```json
{
  "success": false,
  "message": "I encountered a technical issue processing your request. Let me try a simpler approach.",
  "metadata": {
    "agent": "general-chat",
    "fallbackReason": "timeout",
    "sessionId": "elephant-session-1"
  }
}
```

#### HTTP Status Codes

| Status | Meaning | When Returned |
|--------|---------|---------------|
| `200 OK` | Request successful | All successful requests and agent timeouts (fallback used) |
| `400 Bad Request` | Invalid input | Empty message, invalid sessionId format |
| `500 Internal Server Error` | Server error | Unexpected errors in backend processing |

#### Usage Example (JavaScript)

```javascript
const response = await fetch('http://localhost:3002/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: "Find candidates with Python",
    sessionId: "user-session-123",
    useHistory: true
  })
});

const data = await response.json();
if (data.success) {
  console.log('AI Response:', data.message);
  console.log('Processing Time:', data.metadata.processingTime, 'ms');
} else {
  console.error('Error:', data.error);
}
```

#### Usage Example (Python)

```python
import requests
import json

url = "http://localhost:3002/api/chat"
payload = {
    "message": "Find candidates with Python",
    "sessionId": "user-session-123",
    "useHistory": True
}

response = requests.post(url, json=payload)
data = response.json()

if data['success']:
    print(f"Response: {data['message']}")
    print(f"Time: {data['metadata']['processingTime']}ms")
else:
    print(f"Error: {data.get('error')}")
```

---

### 2. POST /api/chat/clear

Clears the conversation history for a specific session.

#### Request

```http
POST /api/chat/clear HTTP/1.1
Host: localhost:3002
Content-Type: application/json

{
  "sessionId": "elephant-session-1"
}
```

**Request Body Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sessionId` | string | Yes | Session to clear |

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Session cleared successfully"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation was successful |
| `message` | string | Confirmation message |

#### Error Response

```json
{
  "success": false,
  "error": "Session not found"
}
```

#### Usage Example

```javascript
const response = await fetch('http://localhost:3002/api/chat/clear', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ sessionId: "user-session-123" })
});

const data = await response.json();
console.log(data.message); // "Session cleared successfully"
```

---

### 3. GET /api/chat/stats

Returns statistics about active chat sessions.

#### Request

```http
GET /api/chat/stats HTTP/1.1
Host: localhost:3002
```

No request body required.

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "activeSessions": 5,
    "totalMessages": 47,
    "avgMessagesPerSession": 9.4,
    "averageLatency": 450,
    "topAgents": {
      "information-retrieval": 12,
      "problem-solving": 8,
      "general-chat": 27,
      "report-generation": 0,
      "automation": 0,
      "industry-knowledge": 0,
      "data-operations": 0
    },
    "sessions": [
      {
        "sessionId": "elephant-session-1",
        "messageCount": 12,
        "lastActivity": "2024-10-23T14:35:22Z",
        "createdAt": "2024-10-23T14:25:10Z"
      },
      {
        "sessionId": "zebra-session-2",
        "messageCount": 8,
        "lastActivity": "2024-10-23T14:30:15Z",
        "createdAt": "2024-10-23T14:20:45Z"
      }
    ]
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the request was successful |
| `data` | object | Statistics data (see below) |

**Data Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `activeSessions` | number | Number of active sessions |
| `totalMessages` | number | Total messages across all sessions |
| `avgMessagesPerSession` | number | Average messages per session |
| `averageLatency` | number | Average response time in milliseconds |
| `topAgents` | object | Count of messages routed to each agent |
| `sessions` | array | Details of each active session |

**Session Details:**

| Field | Type | Description |
|-------|------|-------------|
| `sessionId` | string | Session identifier |
| `messageCount` | number | Messages in this session |
| `lastActivity` | string | ISO timestamp of last message |
| `createdAt` | string | ISO timestamp of session creation |

#### Usage Example

```javascript
const response = await fetch('http://localhost:3002/api/chat/stats');
const data = await response.json();

console.log(`Active Sessions: ${data.data.activeSessions}`);
console.log(`Avg Latency: ${data.data.averageLatency}ms`);
console.log('Agent Usage:', data.data.topAgents);
```

---

### 4. GET /health

Health check endpoint for system status.

#### Request

```http
GET /health HTTP/1.1
Host: localhost:3002
```

No request body required.

#### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "healthy",
  "timestamp": "2024-10-23T14:35:22Z",
  "api": "online",
  "groqApiKey": "configured"
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Overall health ("healthy" or "unhealthy") |
| `timestamp` | string | Server timestamp (ISO format) |
| `api` | string | API status ("online" or "offline") |
| `groqApiKey` | string | API key status ("configured" or "missing") |

#### Error Response

```json
{
  "status": "unhealthy",
  "api": "offline",
  "groqApiKey": "missing",
  "error": "Missing GROQ_API_KEY environment variable"
}
```

#### Usage Example

```javascript
const response = await fetch('http://localhost:3002/health');
const data = await response.json();

if (data.status === 'healthy') {
  console.log('System is healthy');
} else {
  console.error('System unhealthy:', data.error);
}
```

---

## Common Patterns

### Multi-Turn Conversation

To maintain conversation history across multiple messages:

```javascript
const sessionId = generateUUID(); // Create once per session

// Message 1
const response1 = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "Find candidates with Python",
    sessionId: sessionId,
    useHistory: true
  })
});

// Message 2 - uses history from message 1
const response2 = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "Filter by London location",
    sessionId: sessionId,
    useHistory: true  // Includes message 1 and response 1 in context
  })
});

// Message 3 - uses full history
const response3 = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "Sort by experience level",
    sessionId: sessionId,
    useHistory: true  // Includes messages 1-2 and responses 1-2
  })
});
```

### Force Specific Agent

```javascript
// Force a query to use Problem Solving agent
const response = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "How can we improve placement rates?",
    sessionId: sessionId,
    agent: "problem-solving"  // Force this agent
  })
});
```

### Start Fresh Session

```javascript
const response = await fetch('/api/chat/clear', {
  method: 'POST',
  body: JSON.stringify({
    sessionId: sessionId
  })
});

// Now send new message without previous history
const newResponse = await fetch('/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    message: "New topic",
    sessionId: sessionId,
    useHistory: false  // No history to include anyway
  })
});
```

### Monitoring

```javascript
setInterval(async () => {
  const stats = await fetch('/api/chat/stats').then(r => r.json());
  console.log(`Active sessions: ${stats.data.activeSessions}`);
  console.log(`Avg response time: ${stats.data.averageLatency}ms`);
}, 5000);
```

---

## Error Handling

### Common Errors

**400 Bad Request - Empty Message**
```json
{
  "success": false,
  "error": "Message cannot be empty"
}
```
**Solution:** Validate message is not empty before sending

**400 Bad Request - Invalid SessionId**
```json
{
  "success": false,
  "error": "Invalid sessionId format"
}
```
**Solution:** Use UUID v4 format for sessionId

**500 Internal Server Error**
```json
{
  "success": false,
  "error": "Internal server error"
}
```
**Solution:** Check server logs; may indicate Groq API unavailability

**Timeout (Returns 200 with fallback)**
```json
{
  "success": true,
  "message": "I encountered a technical issue. Please try again.",
  "metadata": {
    "agent": "general-chat",
    "fallbackReason": "timeout"
  }
}
```
**Solution:** System automatically fell back to General Chat. Longer queries may timeout - try breaking into smaller queries.

### Retry Strategy

```javascript
async function chatWithRetry(message, sessionId, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message, sessionId })
      });
      
      const data = await response.json();
      if (response.ok || data.success) {
        return data;
      }
      
      // Exponential backoff
      const delay = Math.pow(2, attempt - 1) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    } catch (error) {
      if (attempt === maxRetries) throw error;
    }
  }
}
```

---

## Rate Limiting

Currently no rate limiting implemented. Production should implement:
- Per-session limits: 100 requests/minute
- Per-IP limits: 1000 requests/minute
- Burst allowance: 10 requests/10 seconds

---

## CORS

Frontend and backend should be on same domain or CORS configured:

```javascript
// Backend configuration (Express)
const cors = require('cors');
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001'],
  credentials: true
}));
```
