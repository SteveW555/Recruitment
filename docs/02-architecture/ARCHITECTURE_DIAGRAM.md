# Elephant Frontend-Backend Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DEVELOPMENT SETUP                           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  USER BROWSER                                                       │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │  Dashboard UI (React)                                     │     │
│  │  http://localhost:3000                                    │     │
│  └───────────────────────────────────────────────────────────┘     │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ fetch('/api/chat')
                             │ (relative path - no hardcoded URL)
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  VITE DEV SERVER (Port 3000)                                        │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  PROXY MIDDLEWARE                                        │      │
│  │  ─────────────────────────────────────────────────────   │      │
│  │  Routes: /api/* → http://localhost:3002/api/*           │      │
│  │  • Eliminates CORS issues                               │      │
│  │  • Automatic forwarding                                 │      │
│  │  • WebSocket support (ws: true)                         │      │
│  │  • Detailed request/response logging                    │      │
│  └──────────────────────────────────────────────────────────┘      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Proxied request to
                             │ http://localhost:3002/api/chat
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  EXPRESS BACKEND (Port 3002)                                        │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  CORS Middleware (allows all origins)                   │      │
│  │  JSON Body Parser                                        │      │
│  └──────────────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  API Endpoints                                           │      │
│  │  • POST /api/chat      - Process chat messages          │      │
│  │  • GET  /health        - Health check                   │      │
│  │  • POST /api/chat/clear - Clear conversation            │      │
│  │  • GET  /api/chat/stats - Get statistics               │      │
│  └──────────────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  Agent System                                            │      │
│  │  • General Chat                                          │      │
│  │  • Information Retrieval                                 │      │
│  │  • Problem Solving                                       │      │
│  │  • Automation                                            │      │
│  │  • Report Generation                                     │      │
│  │  • Industry Knowledge                                    │      │
│  └──────────────────────────────────────────────────────────┘      │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ LLM API Calls
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│  GROQ API                                                           │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  Model: llama-3.3-70b-versatile                         │      │
│  │  • Temperature: 0.7 (chat) / 0.3 (structured)           │      │
│  │  • Max tokens: 2000                                      │      │
│  │  • System prompts per agent                             │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

## Request Flow Example

```
1. User types "Hello" in browser
   │
   ├─→ Browser: fetch('/api/chat', { message: "Hello" })
   │
2. Vite Proxy intercepts
   │
   ├─→ Rewrites to: http://localhost:3002/api/chat
   ├─→ Logs: "Proxying request: POST /api/chat"
   │
3. Express Backend receives
   │
   ├─→ Classifies query: "general-chat"
   ├─→ Loads system prompt
   ├─→ Calls GROQ API
   │
4. GROQ processes
   │
   ├─→ Model: llama-3.3-70b-versatile
   ├─→ Temperature: 0.7
   ├─→ Response generated: 314ms
   │
5. Backend returns JSON
   │
   ├─→ { success: true, message: "...", metadata: {...} }
   │
6. Proxy forwards response
   │
   ├─→ Logs: "Proxied response: 200 /api/chat"
   │
7. Frontend receives and displays
   │
   └─→ User sees: "Hello, it's lovely to connect with you..."
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  ENVIRONMENT CONFIGURATION                                          │
└─────────────────────────────────────────────────────────────────────┘

ROOT .env
├─→ FRONTEND_PORT=3000
├─→ BACKEND_PORT=3002
└─→ GROQ_API_KEY=...

frontend/.env
├─→ VITE_BACKEND_PORT=3002
└─→ VITE_API_URL=http://localhost:3002

┌─────────────────────────────────────────────────────────────────────┐
│  frontend/vite.config.js                                            │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  1. Load environment variables                           │      │
│  │     const env = loadEnv(mode, process.cwd(), '')         │      │
│  │                                                           │      │
│  │  2. Extract backend port                                 │      │
│  │     const backendPort = env.VITE_BACKEND_PORT || 3002    │      │
│  │                                                           │      │
│  │  3. Configure proxy                                      │      │
│  │     proxy: {                                             │      │
│  │       '/api': {                                          │      │
│  │         target: `http://localhost:${backendPort}`        │      │
│  │       }                                                  │      │
│  │     }                                                    │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  backend-api/server-fast.js                                              │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  1. Load environment                                     │      │
│  │     dotenv.config({ path: '../.env' })                   │      │
│  │                                                           │      │
│  │  2. Set port                                             │      │
│  │     const PORT = process.env.BACKEND_PORT || 3001        │      │
│  │                                                           │      │
│  │  3. Start server                                         │      │
│  │     app.listen(PORT, ...)                                │      │
│  └──────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

## Startup Sequence

```
start-dev.bat
      │
      ├─→ 1. Kill existing node processes
      │      taskkill /F /IM node.exe
      │
      ├─→ 2. Start Backend (Port 3002)
      │      cd backend-api
      │      set BACKEND_PORT=3002 && npm start
      │      │
      │      ├─→ Load environment variables
      │      ├─→ Load system prompts (7 agents)
      │      ├─→ Initialize GROQ client
      │      ├─→ Start Express on 3002
      │      └─→ ✓ Backend ready in ~2s
      │
      ├─→ 3. Wait 5 seconds
      │
      └─→ 4. Start Frontend (Port 3000)
             cd frontend
             npm start
             │
             ├─→ Load Vite config
             ├─→ Configure proxy
             ├─→ Start dev server
             ├─→ Open browser
             └─→ ✓ Frontend ready in ~3s
```

## Network Diagram

```
Port 3000                    Port 3002
┌────────────┐              ┌────────────┐
│            │              │            │
│  FRONTEND  │─────────────▶│  BACKEND   │
│   (Vite)   │◀─────────────│ (Express)  │
│            │   /api/*     │            │
└────────────┘   Proxy      └────────────┘
      │                            │
      │                            │
      ▼                            ▼
User Browser              GROQ API (External)
http://localhost:3000     llama-3.3-70b-versatile
```

## Benefits Summary

```
┌─────────────────────────────────────────────────────────────────────┐
│  ✅ NO CORS ISSUES                                                  │
│     Proxy makes requests appear same-origin                         │
│                                                                     │
│  ✅ NO HARDCODED URLS                                               │
│     All configuration via environment variables                     │
│                                                                     │
│  ✅ SINGLE SOURCE OF TRUTH                                          │
│     Port config in .env files only                                  │
│                                                                     │
│  ✅ AUTOMATIC ROUTING                                               │
│     Developers use relative paths: fetch('/api/chat')               │
│                                                                     │
│  ✅ WEBSOCKET READY                                                 │
│     Proxy configured with ws: true                                  │
│                                                                     │
│  ✅ PRODUCTION READY                                                │
│     Easy to swap proxy for real backend URL                         │
│                                                                     │
│  ✅ DETAILED LOGGING                                                │
│     Every request tracked for debugging                             │
│                                                                     │
│  ✅ BULLETPROOF                                                     │
│     Works identically on all developer machines                     │
└─────────────────────────────────────────────────────────────────────┘
```
