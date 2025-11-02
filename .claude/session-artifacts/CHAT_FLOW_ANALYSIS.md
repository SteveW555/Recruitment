# Chat Message Flow Analysis

## Complete Call Chain: Send Button → Backend API Endpoint

This document traces the exact flow from when a user clicks the Send button in the chat interface to when the backend API endpoint is invoked.

---

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. USER ACTION                                                          │
│    User clicks Send button or presses Enter                             │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. FRONTEND EVENT HANDLER                                               │
│    File: frontend/dashboard.jsx:645                                     │
│                                                                          │
│    <button onClick={handleSendMessage} ... >                            │
│      <Send className="w-5 h-5" />                                       │
│    </button>                                                             │
│                                                                          │
│    OR                                                                    │
│                                                                          │
│    <input onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. HANDLE SEND MESSAGE FUNCTION                                         │
│    File: frontend/dashboard.jsx:159                                     │
│                                                                          │
│    const handleSendMessage = async (messageOverride = null) => {        │
│      // Validation                                                      │
│      if (isSending) return;  // Prevent duplicate calls                │
│      if (!messageToSend.trim()) return;  // Empty message check         │
│                                                                          │
│      // Set loading state                                               │
│      setIsSending(true);                                                │
│                                                                          │
│      // Add user message to UI                                          │
│      setMessages(prev => [...prev, userMessage]);                       │
│                                                                          │
│      // Classify query locally (for logging)                            │
│      const agentType = classifyQuery(userMessage);                      │
│      addLog(`Classified as: ${agentType}`, 'info');                     │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. FETCH API CALL                                                       │
│    File: frontend/dashboard.jsx:205                                     │
│                                                                          │
│    const response = await fetch('/api/chat', {                          │
│      method: 'POST',                                                    │
│      headers: { 'Content-Type': 'application/json' },                   │
│      body: JSON.stringify({                                             │
│        message: userMessage,                                            │
│        sessionId: 'elephant-session-1',                                 │
│        useHistory: true,                                                │
│        agent: agentType                                                 │
│      })                                                                 │
│    });                                                                  │
│                                                                          │
│    🔍 Key: Uses relative path '/api/chat' (no hardcoded URL)            │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. VITE DEV SERVER PROXY                                                │
│    File: frontend/vite.config.js:13-30                                  │
│                                                                          │
│    proxy: {                                                             │
│      '/api': {                                                          │
│        target: `http://localhost:${backendPort}`,  // Port 3002        │
│        changeOrigin: true,                                              │
│        secure: false,                                                   │
│        ws: true                                                         │
│      }                                                                  │
│    }                                                                    │
│                                                                          │
│    ✅ Transforms:                                                        │
│       FROM: http://localhost:3000/api/chat                              │
│       TO:   http://localhost:3002/api/chat                              │
│                                                                          │
│    📋 Logs to terminal:                                                 │
│       "Proxying request: POST /api/chat -> /api/chat"                   │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 6. HTTP REQUEST ARRIVES AT BACKEND                                      │
│                                                                          │
│    POST http://localhost:3002/api/chat                                  │
│                                                                          │
│    Headers:                                                             │
│      Content-Type: application/json                                     │
│      Origin: http://localhost:3000                                      │
│                                                                          │
│    Body:                                                                │
│      {                                                                  │
│        "message": "candidates named khan",                              │
│        "sessionId": "elephant-session-1",                               │
│        "useHistory": true,                                              │
│        "agent": "general-chat"                                          │
│      }                                                                  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 7. EXPRESS ROUTER MATCHES ENDPOINT                                      │
│    File: backend-api/server-fast.js:60                                  │
│                                                                          │
│    🎯 THIS IS WHERE server-fast.js IS INVOKED! 🎯                        │
│                                                                          │
│    app.post('/api/chat', async (req, res) => {                          │
│      logger.info(`*******/api/chat endpoint called*******`);            │
│                                                                          │
│      try {                                                              │
│        const { message, sessionId, useHistory, agent } = req.body;      │
│                                                                          │
│        // Validation                                                    │
│        if (!message || !message.trim()) {                               │
│          return res.status(400).json({ error: 'Message is required' }); │
│        }                                                                │
│                                                                          │
│        // Log request details                                           │
│        console.log(`[${new Date().toISOString()}] Chat request:`, {     │
│          sessionId, agent, message, useHistory                          │
│        });                                                              │
│                                                                          │
│        logger.info('Chat request received', {                           │
│          sessionId, agent, messageLength: message.length, useHistory    │
│        });                                                              │
│                                                                          │
│        // Call Python AI Router HTTP server...                          │
│        const response = await fetch(`${AI_ROUTER_URL}/route`, {         │
│          method: 'POST',                                                │
│          headers: { 'Content-Type': 'application/json' },               │
│          body: JSON.stringify({                                         │
│            query: message,                                              │
│            session_id: sessionId,                                       │
│            user_id: 'web-user'                                          │
│          })                                                             │
│        });                                                              │
│        ...                                                              │
│      }                                                                  │
│    });                                                                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Step-by-Step Breakdown

### Step 1: User Action
**Location:** Browser UI
**Files:** `frontend/dashboard.jsx:645`

User triggers one of two events:
1. **Click Send Button:** `<button onClick={handleSendMessage}>`
2. **Press Enter Key:** `<input onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}>`

---

### Step 2: Event Handler Invocation
**Location:** React Component
**File:** `frontend/dashboard.jsx:159`

The `handleSendMessage` function is invoked:

```javascript
const handleSendMessage = async (messageOverride = null) => {
  // Generate unique call ID for debugging
  const callId = Math.random().toString(36).substring(7);

  // Prevent concurrent requests
  if (isSending) {
    console.log(`Already sending, ignoring duplicate call`);
    return;
  }

  // Extract message text
  const messageToSend = messageOverride || inputMessage;

  // Validate message
  if (!messageToSend || !messageToSend.trim()) {
    return;
  }

  // Set loading state
  setIsSending(true);

  // Add user message to UI immediately
  setMessages(prev => [...prev, {
    id: prev.length + 1,
    type: 'user',
    text: messageToSend,
    timestamp: new Date().toLocaleTimeString()
  }]);

  // Clear input field
  setInputMessage('');
```

---

### Step 3: Local Query Classification
**Location:** React Component
**File:** `frontend/dashboard.jsx:199`

Before sending to backend, frontend performs local classification for UI logging:

```javascript
// Simple keyword-based classification (for UI logging only)
const agentType = classifyQuery(userMessage);
addLog(`Classified as: ${agentType}`, 'info');
```

This is **NOT** the real classification - it's just for UI feedback. The real classification happens in Python.

---

### Step 4: Fetch API Call
**Location:** React Component
**File:** `frontend/dashboard.jsx:205-216`

The critical HTTP request is made:

```javascript
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userMessage,              // "candidates named khan"
    sessionId: 'elephant-session-1',   // Session ID for conversation context
    useHistory: true,                  // Enable conversation history
    agent: agentType                   // Frontend classification (for logging)
  })
});
```

**Key Points:**
- ✅ Uses **relative path** `/api/chat` (no hardcoded URL)
- ✅ Sends JSON payload with message and metadata
- ✅ Async/await for clean promise handling

---

### Step 5: Vite Proxy Intercepts Request
**Location:** Vite Dev Server
**File:** `frontend/vite.config.js:13-30`

The Vite dev server's proxy middleware intercepts the request:

```javascript
proxy: {
  '/api': {
    target: `http://localhost:${backendPort}`,  // Port 3002
    changeOrigin: true,
    secure: false,
    ws: true,
    configure: (proxy, _options) => {
      proxy.on('proxyReq', (proxyReq, req, _res) => {
        console.log('Proxying request:', req.method, req.url);
      });
    }
  }
}
```

**What Happens:**
1. Request comes in: `http://localhost:3000/api/chat`
2. Matches proxy rule: `/api`
3. Transforms to: `http://localhost:3002/api/chat`
4. Logs: `"Proxying request: POST /api/chat -> /api/chat"`

**Why This Works:**
- Frontend runs on port 3000
- Backend runs on port 3002
- Proxy handles the port mapping automatically
- No CORS issues (same-origin from browser's perspective)

---

### Step 6: HTTP Request Arrives at Backend
**Location:** Node.js Express Server
**Port:** 3002

The HTTP request arrives at the backend:

```
POST http://localhost:3002/api/chat HTTP/1.1
Host: localhost:3002
Content-Type: application/json
Origin: http://localhost:3000
Content-Length: 123

{
  "message": "candidates named khan",
  "sessionId": "elephant-session-1",
  "useHistory": true,
  "agent": "general-chat"
}
```

---

### Step 7: Express Router Invokes Endpoint Handler
**Location:** Backend API Server
**File:** `backend-api/server-fast.js:60`

🎯 **THIS IS THE MOMENT!** The endpoint handler is invoked:

```javascript
app.post('/api/chat', async (req, res) => {
  // ✅ UNIFIED LOGGING - First log message!
  logger.info(`*******/api/chat endpoint called*******`);

  try {
    // Extract request body
    const { message, sessionId = 'default', useHistory = true, agent = 'auto' } = req.body;

    // Validate message
    if (!message || !message.trim()) {
      return res.status(400).json({
        error: 'Message is required'
      });
    }

    // ✅ Console logging (old style)
    console.log(`[${new Date().toISOString()}] Chat request:`, {
      sessionId,
      agent,
      message: message.substring(0, 100),
      useHistory
    });

    // ✅ UNIFIED LOGGING - Request details with structured data
    logger.info(`Chat request received`, {
      sessionId,
      agent,
      messageLength: message.length,
      useHistory
    });

    // Call Python AI Router HTTP Server (FAST!)
    const startTime = Date.now();

    // ✅ UNIFIED LOGGING - AI Router call
    logger.info(`Calling AI Router at ${AI_ROUTER_URL}/route`);

    try {
      const response = await fetch(`${AI_ROUTER_URL}/route`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          session_id: sessionId,
          user_id: 'web-user'
        })
      });

      const responseTime = Date.now() - startTime;
      const result = await response.json();

      // ✅ UNIFIED LOGGING - AI Router response
      logger.info(`AI Router response received in ${responseTime}ms`, {
        agent: result.agent,
        confidence: result.confidence,
        success: result.success
      });

      // Return response to frontend
      res.json({
        success: true,
        message: result.content || '',
        metadata: { ... }
      });

    } catch (fetchError) {
      // ✅ UNIFIED LOGGING - Error handling
      logger.error(`Failed to call AI Router`, {
        error: fetchError.message,
        url: AI_ROUTER_URL
      });

      res.status(503).json({
        success: false,
        error: 'AI Router service unavailable'
      });
    }

  } catch (error) {
    // ✅ UNIFIED LOGGING - General error handling
    logger.error(`Error in /api/chat endpoint`, {
      error: error.message,
      stack: error.stack?.substring(0, 200)
    });

    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
});
```

---

## Logging Output You'll See

When you send a message, you'll see logs in your `npm start` terminal:

```bash
# Frontend (Vite proxy)
[frontend] Proxying request: POST /api/chat -> /api/chat

# Backend (server-fast.js)
[20:44:42] [BACKEND-API] [INFO] *******/api/chat endpoint called*******
[2025-11-02T19:44:42.108Z] Chat request: { sessionId: 'elephant-session-1', agent: 'general-chat', ... }
[20:44:42] [BACKEND-API] [INFO] Chat request received
{
  "sessionId": "elephant-session-1",
  "agent": "general-chat",
  "messageLength": 19,
  "useHistory": true
}
[20:44:42] [BACKEND-API] [INFO] Calling AI Router at http://localhost:8888/route

# AI Router (Python)
[20:44:42] [AI-ROUTER] [INFO] ******classify() called for query_id: abc123******

# Backend (after AI Router responds)
[20:44:43] [BACKEND-API] [INFO] AI Router response received in 1102ms
{
  "agent": "INFORMATION_RETRIEVAL",
  "confidence": 0.9,
  "success": true
}

# Frontend (Vite proxy)
[frontend] Proxied response: 200 /api/chat
```

---

## Key Takeaways

1. **Relative Paths:** Frontend uses `/api/chat` (no hardcoded URLs)
2. **Vite Proxy:** Automatically routes frontend → backend across different ports
3. **Unified Logging:** Green `[BACKEND-API]` logs appear in terminal when endpoint is hit
4. **Express Router:** Pattern matching happens automatically
5. **Async/Await:** Clean promise handling throughout the chain
6. **Error Handling:** Multiple levels with unified logging at each level

---

## File Summary

| File | Line | Purpose |
|------|------|---------|
| `frontend/dashboard.jsx` | 645 | Send button onClick handler |
| `frontend/dashboard.jsx` | 641 | Enter key onKeyPress handler |
| `frontend/dashboard.jsx` | 159 | Main handleSendMessage function |
| `frontend/dashboard.jsx` | 205 | fetch('/api/chat') API call |
| `frontend/vite.config.js` | 13-30 | Vite proxy configuration |
| `backend-api/server-fast.js` | 60 | Express POST /api/chat endpoint ⭐ |
| `backend-api/server-fast.js` | 61 | First unified log message |
| `backend-api/server-fast.js` | 79 | Request details logging |
| `backend-api/server-fast.js` | 88 | AI Router call logging |

---

**Last Updated:** 2025-11-02
**Status:** Complete flow analysis with unified logging system integrated
