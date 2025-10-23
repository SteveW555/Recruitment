---
name: frontend-backend-troubleshoot
description: Expert troubleshooting for frontend-backend communication issues in web applications. This skill should be used when debugging connection errors, CORS issues, port mismatches, proxy configuration problems, or "Failed to fetch" errors between frontend and backend services. Provides systematic diagnosis, permanent fixes using Vite proxy configuration, and comprehensive testing strategies.
---

# Frontend-Backend Communication Troubleshooting

## Purpose

This skill provides expert guidance for diagnosing and permanently fixing communication issues between frontend and backend services in web applications. It embodies battle-tested troubleshooting methodologies, configuration patterns, and testing strategies proven to resolve common connectivity problems.

## When to Use This Skill

Use this skill when encountering:

- **Connection errors**: "Failed to fetch", "Connection refused", "Network error"
- **CORS errors**: Cross-Origin Resource Sharing violations
- **Port mismatch issues**: Frontend and backend on different ports not communicating
- **Proxy configuration problems**: Vite/Webpack proxies not routing correctly
- **Hardcoded URL issues**: Direct fetch calls to localhost URLs failing
- **Environment variable problems**: Configuration not loading properly
- **Development server issues**: Servers running but not reaching each other

## Core Troubleshooting Methodology

### Step 1: Identify the Symptom Pattern

Analyze the error message to determine the root cause category:

**Connection Errors** (`Failed to fetch`, `ECONNREFUSED`)
- Backend not running on expected port
- Frontend attempting connection to wrong port
- Firewall/security blocking connection

**HTTP Errors** (`404`, `500`, `502`)
- Endpoint path incorrect
- API route not defined
- Backend routing misconfigured

**CORS Errors** (`Access-Control-Allow-Origin`)
- Cross-origin request without proper headers
- No proxy configured for development
- CORS middleware not enabled on backend

**Timeout Errors**
- Backend processing too slowly
- Network latency issues
- Infinite loops or hanging processes

### Step 2: Systematic Diagnosis

Execute the diagnostic sequence in order:

#### 2.1 Verify Backend Status
```bash
# Check if backend port is listening (Windows)
netstat -ano | findstr :PORT_NUMBER
# Returns: TCP 0.0.0.0:PORT ... LISTENING PID

# Check if backend port is listening (Linux/Mac)
lsof -i :PORT_NUMBER

# Alternative Windows check using PowerShell
powershell -Command "Test-NetConnection -ComputerName localhost -Port PORT_NUMBER -InformationLevel Quiet"
# Returns: True (listening) or False (not listening)

# Test backend directly
curl http://localhost:PORT/health
curl http://localhost:PORT/api/endpoint

# Windows alternative if curl not available
powershell -Command "Invoke-WebRequest -Uri http://localhost:PORT/health -UseBasicParsing"
```

#### 2.2 Verify Frontend Status
```bash
# Check if frontend dev server is running
curl http://localhost:FRONTEND_PORT

# Check browser console for errors (F12)
# Look for: Network errors, CORS errors, 404s
```

#### 2.3 Check Configuration Files
```bash
# Backend port configuration
cat backend/package.json          # Check scripts
cat backend/server.js             # Check PORT variable
cat .env                          # Check BACKEND_PORT

# Frontend proxy configuration
cat frontend/vite.config.js       # Check proxy settings
cat frontend/.env                 # Check VITE_BACKEND_PORT
cat frontend/package.json         # Check start script
```

#### 2.4 Trace Request Path
```bash
# Enable verbose logging
# Vite: Check terminal for proxy logs
# Backend: Add console.log to request handlers

# Monitor network tab in browser DevTools
# Check request URL, method, headers, response
```

### Step 3: Apply Permanent Fix

Based on diagnosis, apply the appropriate solution pattern.

## Solution Patterns

### Pattern 1: Vite Proxy Configuration (Recommended)

The bulletproof solution for development environments.

#### Implementation

**Step 1: Environment Configuration**

Create `.env` files:

```env
# Root .env
FRONTEND_PORT=3000
BACKEND_PORT=3002
GROQ_API_KEY=your_key_here
```

```env
# frontend/.env
VITE_BACKEND_PORT=3002
VITE_API_URL=http://localhost:3002
```

**Step 2: Vite Proxy Setup**

Edit `frontend/vite.config.js`:

```javascript
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backendPort = env.VITE_BACKEND_PORT || 3002;

  return {
    plugins: [react()],
    server: {
      port: 3000,
      open: true,
      proxy: {
        '/api': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
          secure: false,
          ws: true,  // WebSocket support
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('Proxy error:', err);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('Proxying request:', req.method, req.url, '->', proxyReq.path);
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log('Proxied response:', proxyRes.statusCode, req.url);
            });
          }
        }
      }
    }
  };
});
```

**Step 3: Update Frontend API Calls**

Replace hardcoded URLs with relative paths:

```javascript
// ❌ BEFORE (Hardcoded - will fail)
fetch('http://localhost:3002/api/chat', { ... })

// ✅ AFTER (Relative - proxy handles routing)
fetch('/api/chat', { ... })
```

**Step 4: Update Backend Port Reading**

```javascript
// backend/server.js
const PORT = process.env.BACKEND_PORT || 3001;
app.listen(PORT, () => {
  console.log(`Backend running on port ${PORT}`);
});
```

**Why This Works:**
- ✅ Eliminates CORS issues (same origin)
- ✅ No hardcoded URLs
- ✅ Environment-driven configuration
- ✅ WebSocket support ready
- ✅ Production-ready (swap proxy for real URL)

### Pattern 2: CORS Configuration (Fallback)

Use only when proxy configuration is not possible.

```javascript
// backend/server.js
import cors from 'cors';

app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:5173'],
  credentials: true
}));
```

**Limitations:**
- ⚠️ Not recommended for production
- ⚠️ Requires updating for each frontend port
- ⚠️ More complex security configuration

### Pattern 3: Automated Startup Script

Create `start-dev.bat` (Windows) or `start-dev.sh` (Linux/Mac):

```batch
@echo off
echo Starting development servers...

REM Clean up existing processes
taskkill /F /IM node.exe 2>nul

REM Start backend on configured port
cd backend-api
start "Backend" cmd /k "set BACKEND_PORT=3002 && npm start"
cd ..

REM Wait for backend to initialize
timeout /t 5 /nobreak >nul

REM Start frontend
cd frontend
start "Frontend" cmd /k "npm start"
cd ..

echo Servers starting...
echo Backend:  http://localhost:3002
echo Frontend: http://localhost:3000
```

## Testing Strategy

### Automated Testing Script

Use the comprehensive test script from `references/test-script-template.py`:

```bash
python testends.py
```

The script validates:
1. Backend health and availability
2. Frontend server running
3. Proxy configuration working
4. Direct backend API access
5. Proxied API access
6. Agent/route classification
7. Session/state management
8. Error handling

### Manual Testing Checklist

```bash
# 1. Backend Direct Test
curl http://localhost:BACKEND_PORT/health
curl -X POST http://localhost:BACKEND_PORT/api/endpoint

# 2. Frontend Proxy Test
curl http://localhost:FRONTEND_PORT/api/endpoint

# 3. Browser Test
# Open DevTools (F12) → Network tab
# Trigger API call from UI
# Verify: Status 200, no CORS errors, response received

# 4. Proxy Logs Test
# Check frontend terminal for:
# "Proxying request: POST /api/endpoint -> /api/endpoint"
# "Proxied response: 200 /api/endpoint"
```

## Common Pitfalls and Solutions

### Pitfall 1: Hardcoded Ports in Multiple Places

**Symptom**: Changing port requires updates in 5+ files

**Solution**: Single source of truth via environment variables
- Define in `.env` only
- Load via `process.env` or `import.meta.env`
- Never hardcode in source code

### Pitfall 2: Forgetting to Restart Servers

**Symptom**: Changes not taking effect

**Solution**: Always restart both servers after configuration changes
```bash
# Kill all node processes
taskkill /F /IM node.exe  # Windows
killall node              # Linux/Mac

# Restart using automated script
./start-dev.bat
```

### Pitfall 3: Mixed HTTP/HTTPS

**Symptom**: `Mixed Content` errors

**Solution**: Ensure both frontend and backend use same protocol
- Development: Both HTTP
- Production: Both HTTPS

### Pitfall 4: Cached Proxy Configuration

**Symptom**: Vite proxy changes not applying

**Solution**: Clear Vite cache
```bash
cd frontend
rm -rf node_modules/.vite  # Linux/Mac
rmdir /s /q node_modules\.vite  # Windows
npm start
```

### Pitfall 5: Wrong API Path Pattern

**Symptom**: Some endpoints proxy, others don't

**Solution**: Ensure all API calls start with `/api`
```javascript
// ✅ Will proxy
fetch('/api/chat')
fetch('/api/users/123')

// ❌ Won't proxy
fetch('/chat')
fetch('/users/123')
```

## Architecture Patterns

### Development Setup (Recommended)

```
User Browser (localhost:3000)
    ↓
Vite Dev Server (Port 3000)
    ↓ [Proxy: /api/* → localhost:3002/api/*]
    ↓
Express Backend (Port 3002)
    ↓
External APIs (GROQ, OpenAI, etc.)
```

**Benefits:**
- No CORS configuration needed
- Easy localhost development
- Simple to switch to production URLs

### Production Setup

```
User Browser (https://app.example.com)
    ↓
Frontend Build (Static files)
    ↓ [API calls to https://api.example.com]
    ↓
Backend Server (https://api.example.com)
    ↓
External APIs
```

**Migration:**
```javascript
// Use environment variable to switch
const API_URL = import.meta.env.VITE_API_URL || '/api';
fetch(`${API_URL}/chat`, { ... });
```

## Diagnostic Flowchart

```
Connection Error Detected
    ↓
Is Backend Running?
    → NO → Start backend on correct port
    → YES ↓
Can curl backend directly?
    → NO → Check firewall/port availability
    → YES ↓
Is Frontend Running?
    → NO → Start frontend dev server
    → YES ↓
Is proxy configured in vite.config.js?
    → NO → Add proxy configuration
    → YES ↓
Are API calls using relative paths?
    → NO → Change to fetch('/api/...')
    → YES ↓
Clear Vite cache and restart
    ↓
Still failing? → Check references/troubleshooting-guide.md
```

## Performance Benchmarks

Target response times for healthy system:

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Backend Health | <100ms | <500ms | >1s |
| Proxy Overhead | <50ms | <200ms | >500ms |
| API Response | <3s | <5s | >10s |
| Frontend Load | <1s | <3s | >5s |

## Additional Resources

See the `references/` directory for:

- `troubleshooting-guide.md` - Extended troubleshooting scenarios
- `configuration-templates/` - Ready-to-use config files
- `test-script-template.py` - Comprehensive testing script

See the `scripts/` directory for:

- `diagnose.py` - Automated diagnostic tool
- `fix-ports.sh` - Port cleanup utility

See the `assets/` directory for:

- `vite.config.template.js` - Production-ready Vite config
- `start-dev.template.bat` - Startup script template

## Real-World Troubleshooting Example

### Case Study: "500 Internal Server Error" on /api/chat

**Initial Symptoms:**
```
Browser Console:
POST http://localhost:3000/api/chat 500 (Internal Server Error)
Failed to load resource: the server responded with a status of 404 (Not Found)
[vite] connected.
```

**Step-by-Step Diagnosis:**

1. **Analyzed the error pattern**
   - 500 error suggests backend issue
   - But also seeing connection issues
   - Vite is connected (frontend working)

2. **Checked if backend is running**
   ```bash
   # Windows PowerShell
   Test-NetConnection -ComputerName localhost -Port 3002 -InformationLevel Quiet
   # Result: False ← BACKEND NOT RUNNING!

   # Confirmed with netstat
   netstat -ano | findstr :3002
   # Result: No output ← Port not listening
   ```

3. **Verified frontend proxy configuration**
   ```javascript
   // vite.config.js was correct:
   proxy: {
     '/api': {
       target: 'http://localhost:3002',
       changeOrigin: true
     }
   }
   ```

4. **Root Cause Identified**
   - Backend server was never started
   - Frontend was running and trying to proxy
   - Proxy had nowhere to forward requests

5. **Solution Applied**
   ```bash
   cd backend-api
   set BACKEND_PORT=3002
   npm start
   ```

6. **Verification**
   ```bash
   # Test health endpoint
   curl http://localhost:3002/health
   # Result: {"status":"ok","service":"Elephant AI Backend","groq":true}

   # Test chat endpoint
   curl -X POST http://localhost:3002/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"Hello","sessionId":"test"}'
   # Result: {"success":true,"message":"...","metadata":{...}}
   ```

**Key Takeaway:** Always verify BOTH servers are actually running before diving into complex proxy or CORS debugging. Use `Test-NetConnection` (Windows) or `lsof` (Linux/Mac) to quickly check port status.

## Quick Reference

### Diagnostic Commands

```bash
# Check ports (Windows)
netstat -ano | findstr :3000
netstat -ano | findstr :3002
powershell -Command "Test-NetConnection -ComputerName localhost -Port 3002 -InformationLevel Quiet"

# Check ports (Linux/Mac)
lsof -i :3000
lsof -i :3002

# Test endpoints
curl http://localhost:3002/health
curl -X POST http://localhost:3000/api/chat -d '{}'

# Kill processes (Windows)
taskkill /F /IM node.exe
# Kill specific process
taskkill /F /PID [PID_NUMBER]

# Kill processes (Linux/Mac)
killall node
# Kill specific process
kill -9 [PID]
```

### Key Files to Check
1. `.env` - Port configuration
2. `frontend/vite.config.js` - Proxy settings
3. `frontend/.env` - Vite env vars
4. `backend/server.js` - Port reading
5. Frontend API calls - Relative vs absolute paths

### Red Flags
- ⚠️ Hardcoded `http://localhost:PORT` in frontend code
- ⚠️ No proxy configuration in vite.config.js
- ⚠️ Port numbers scattered across multiple files
- ⚠️ CORS middleware as primary solution
- ⚠️ Mixed HTTP/HTTPS protocols

### Green Flags
- ✅ All API calls use relative paths (`/api/*`)
- ✅ Proxy configured in vite.config.js
- ✅ Ports defined in `.env` files
- ✅ Automated startup script exists
- ✅ Test script validates connectivity
- ✅ Proxy logging enabled for debugging
