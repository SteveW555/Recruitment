# 🚀 Fast Mode Setup - Eliminate 14-Second Delay!

## Problem
The current system spawns a new Python process for every request, loading the 13-second sentence-transformers model each time.

**Before (Slow):**
- Request 1: 14.5 seconds
- Request 2: 14.5 seconds
- Request 3: 14.5 seconds

**After (Fast):**
- First startup: 13 seconds (one time!)
- Request 1: **~200ms** ⚡
- Request 2: **~200ms** ⚡
- Request 3: **~200ms** ⚡

## Solution
Use a **persistent Python HTTP server** that keeps the model loaded in memory.

---

## Installation Steps

### 1. Install Required Python Packages

```bash
cd d:\Recruitment
pip install fastapi uvicorn
```

Or add to `requirements-ai-router.txt`:
```
fastapi==0.104.1
uvicorn==0.24.0
```

Then install:
```bash
pip install -r requirements-ai-router.txt
```

### 2. Start the Python AI Router Server

**Option A: Use the startup script (Recommended)**
```bash
# Double-click this file or run:
start-ai-router-server.bat
```

**Option B: Manual startup**
```bash
cd d:\Recruitment
set GROQ_API_KEY=YOUR_GROQ_API_KEY_HERE
set ANTHROPIC_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE
python -m utils.ai_router.http_server
```

**Expected output:**
```
[*] Starting AI Router HTTP Server...
[*] Initializing router dependencies...
[*] Loading classifier...
Loading sentence-transformers model: all-MiniLM-L6-v2...
[OK] Model loaded successfully
...
[OK] 6 agent(s) loaded
[*] Server ready on http://localhost:8888
[*] Model loaded and cached - requests will be fast!
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8888
```

**Keep this terminal window open!** The server must stay running.

### 3. Start the Backend (Fast Version)

**In a NEW terminal:**
```bash
cd backend-api
set BACKEND_PORT=3002
node server-fast.js
```

**Expected output:**
```
============================================================
🚀 Backend API Server (FAST VERSION)
============================================================
✅ Server running on port 3002
✅ GROQ API Key: Configured
✅ AI Router URL: http://localhost:8888

📋 IMPORTANT: Start Python server first!
   Run: start-ai-router-server.bat

🔗 Endpoints:
   Health: http://localhost:3002/health
   Chat:   http://localhost:3002/api/chat
============================================================
```

### 4. Start the Frontend

**In a THIRD terminal:**
```bash
cd frontend
npm start
```

---

## Testing

### Test the Python Server Directly
```bash
curl -X POST http://localhost:8888/route \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"hi\",\"session_id\":\"test\",\"user_id\":\"test\"}"
```

**Expected response (~200ms):**
```json
{
  "success": true,
  "content": "Hello! How can I assist you...",
  "agent": "GENERAL_CHAT",
  "confidence": 0.807,
  "latency_ms": 168
}
```

### Test via Backend
```bash
curl -X POST http://localhost:3002/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"message\":\"hi\",\"sessionId\":\"test\"}"
```

### Test via Frontend
Open http://localhost:3000 and send a message - should respond in **~200ms**!

---

## Package.json Update

Add these scripts to `backend-api/package.json`:

```json
{
  "scripts": {
    "start": "node server.js",
    "start:fast": "node server-fast.js",
    "dev": "nodemon server.js",
    "dev:fast": "nodemon server-fast.js"
  }
}
```

Then use:
```bash
npm run start:fast  # Production fast mode
npm run dev:fast    # Development with auto-reload
```

---

## Architecture

### Old (Slow) Architecture
```
Frontend → Backend → spawn python (13s model load) → classify → respond → exit
                  → spawn python (13s model load) → classify → respond → exit
                  → spawn python (13s model load) → classify → respond → exit
```

### New (Fast) Architecture
```
Python HTTP Server (Port 8888)
   ↓ (loads model once at startup - 13s)
   ↓ (stays running, model in memory)

Frontend → Backend (Port 3002) → HTTP request → Python (200ms) → respond
                                → HTTP request → Python (200ms) → respond
                                → HTTP request → Python (200ms) → respond
```

---

## Troubleshooting

### Python server not starting
**Error:** `ModuleNotFoundError: No module named 'fastapi'`
**Fix:** `pip install fastapi uvicorn`

### Backend can't reach Python
**Error:** `AI Router service unavailable`
**Fix:** Make sure Python server is running on port 8888
```bash
netstat -ano | findstr :8888  # Check if port is listening
```

### Port 8888 already in use
**Fix:** Kill the existing process or change the port
```bash
# Kill process on port 8888
netstat -ano | findstr :8888
taskkill /F /PID <PID>

# Or use different port in http_server.py:
# uvicorn.run(app, host="0.0.0.0", port=8889)
```

### Still slow after switching
**Check:** Make sure you're using `server-fast.js` not `server.js`
**Check:** Python server is actually running (visit http://localhost:8888/health)

---

## Performance Comparison

| Scenario | Old (spawn) | New (HTTP) | Improvement |
|----------|-------------|------------|-------------|
| First request | 14.5s | 200ms | **72x faster** |
| Second request | 14.5s | 200ms | **72x faster** |
| 10 requests | 145s | 2s | **72x faster** |
| Startup time | 0s | 13s (one time) | One-time cost |

**Total time for 10 messages:**
- Old: 145 seconds (2 minutes 25 seconds) 🐌
- New: 15 seconds (13s startup + 2s messages) ⚡

---

## Production Deployment

For production, use a process manager to keep the Python server running:

**Option 1: PM2 (Recommended)**
```bash
npm install -g pm2
pm2 start "python -m utils.ai_router.http_server" --name ai-router
pm2 start backend-api/server-fast.js --name backend
pm2 save
pm2 startup  # Auto-start on reboot
```

**Option 2: Windows Service**
Use NSSM (Non-Sucking Service Manager) to run as a Windows service

**Option 3: Docker**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements-ai-router.txt .
RUN pip install -r requirements-ai-router.txt
COPY . .
CMD ["python", "-m", "utils.ai_router.http_server"]
```

---

## Rollback to Old Version

If you need to go back to the old (slow) version:

```bash
cd backend-api
node server.js  # Use original server.js
```

The old version still works, it's just slower.

---

## Summary

✅ **Install:** `pip install fastapi uvicorn`
✅ **Start Python:** `start-ai-router-server.bat`
✅ **Start Backend:** `node server-fast.js`
✅ **Start Frontend:** `npm start`
✅ **Enjoy:** 200ms responses instead of 14 seconds!
