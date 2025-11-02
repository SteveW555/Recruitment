# Elephant Development Setup Guide

## Quick Start

### Option 1: Automated Startup (Recommended)
```bash
# Windows
start-dev.bat

# This will:
# 1. Clean up any existing node processes
# 2. Start backend on port 3002
# 3. Start frontend on port 3000
# 4. Open your browser automatically
```

### Option 2: Manual Startup
```bash
# Terminal 1 - Backend
cd backend-api
set BACKEND_PORT=3002
npm start

# Terminal 2 - Frontend
cd frontend
npm start
```

## Architecture

### Ports Configuration
- **Frontend**: `http://localhost:3000` (Vite dev server)
- **Backend**: `http://localhost:3002` (Express API)

### How Communication Works

1. **Vite Proxy**: Frontend uses Vite's built-in proxy to route `/api/*` requests
2. **No CORS Issues**: Proxy eliminates cross-origin problems
3. **Environment Variables**: Configuration stored in `.env` files
4. **Bulletproof**: No hardcoded URLs - all configuration-driven

### Configuration Files

#### Root `.env`
```env
FRONTEND_PORT=3000
BACKEND_PORT=3002
GROQ_API_KEY=your_key_here
```

#### `frontend/.env`
```env
VITE_BACKEND_PORT=3002
VITE_API_URL=http://localhost:3002
```

#### `frontend/vite.config.js`
- Loads environment variables
- Configures proxy to route `/api/*` → `http://localhost:3002/api/*`
- Enables WebSocket support
- Adds detailed logging for debugging

#### `frontend/dashboard.jsx`
- Uses relative API paths: `fetch('/api/chat')`
- No hardcoded URLs
- Proxy handles routing automatically

#### `backend-api/server-fast.js`
- Reads `BACKEND_PORT` from environment
- Defaults to 3001 if not set
- CORS enabled for all origins
- Manages Python AI Router lifecycle via pythonRouterManager.js

## Troubleshooting

### Problem: "Failed to fetch"
**Solution**: Ensure both servers are running on correct ports
```bash
# Check if backend is running
curl http://localhost:3002/health

# Check if frontend is running
curl http://localhost:3000
```

### Problem: Port already in use
**Solution**: Kill existing processes
```bash
# Windows
taskkill /F /IM node.exe

# Then restart using start-dev.bat
```

### Problem: Proxy not working
**Solution**:
1. Delete `frontend/node_modules/.vite` cache
2. Restart frontend server
```bash
cd frontend
rmdir /s /q node_modules\.vite
npm start
```

### Problem: Environment variables not loading
**Solution**:
1. Ensure `.env` files exist in correct locations
2. Restart both servers
3. Check variable names start with `VITE_` for frontend

## Development Workflow

### Adding New API Endpoints

1. **Backend** (`backend-api/server-fast.js`):
```javascript
app.post('/api/your-endpoint', async (req, res) => {
  // Your logic here
  res.json({ success: true });
});
```

2. **Frontend** (`frontend/dashboard.jsx`):
```javascript
const response = await fetch('/api/your-endpoint', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ data: 'value' })
});
```

### Testing

```bash
# Backend health check
curl http://localhost:3002/health

# Frontend proxy test
curl http://localhost:3000/api/health

# Both should return the same response
```

## Why This Solution is Bulletproof

1. **No Hardcoded URLs**: All configuration via environment variables
2. **Proxy Eliminates CORS**: No cross-origin issues
3. **Single Source of Truth**: Port configuration in `.env`
4. **Automatic Routing**: Vite handles all API forwarding
5. **Development Parity**: Same setup on all machines
6. **Easy to Change**: Update `.env` to change ports
7. **WebSocket Ready**: Proxy supports WS for real-time features
8. **Detailed Logging**: Proxy logs all requests for debugging

## Production Deployment

For production, replace the proxy with actual backend URL:

```javascript
// frontend/dashboard.jsx
const API_URL = import.meta.env.VITE_API_URL || '/api';
const response = await fetch(`${API_URL}/chat`, { ... });
```

Then set `VITE_API_URL=https://your-production-backend.com/api` in production environment.
