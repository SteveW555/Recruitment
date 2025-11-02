# Extended Troubleshooting Guide

## Detailed Error Scenarios and Solutions

### Scenario 1: "Failed to fetch" Error

**Full Error**:
```
Failed to fetch
TypeError: Failed to fetch
```

**Root Causes**:
1. Backend not running
2. Wrong port in fetch URL
3. CORS blocking request
4. Network/firewall issue

**Diagnostic Steps**:
```bash
# 1. Verify backend is running
curl http://localhost:BACKEND_PORT/health

# 2. Check frontend console (F12)
#    - Network tab: Check request URL
#    - Console tab: Check error details

# 3. Verify ports match
cat .env | grep PORT
cat frontend/vite.config.js | grep target

# 4. Test from command line
curl -X POST http://localhost:BACKEND_PORT/api/endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

**Solution**:
```javascript
// frontend/vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3002',
        changeOrigin: true
      }
    }
  }
});

// frontend/component.jsx
// Change from:
fetch('http://localhost:3002/api/endpoint')

// To:
fetch('/api/endpoint')
```

### Scenario 2: CORS Error

**Full Error**:
```
Access to fetch at 'http://localhost:3002/api/chat' from origin 'http://localhost:3000'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
on the requested resource.
```

**Root Cause**: Cross-origin request without proper headers or proxy

**Diagnostic Steps**:
```bash
# Check if CORS middleware is enabled
cat backend-api/server-fast.js | grep cors

# Check request origin
# Browser DevTools → Network → Request Headers → Origin
```

**Preferred Solution (Proxy)**:
```javascript
// vite.config.js - Add proxy to eliminate CORS
proxy: {
  '/api': {
    target: 'http://localhost:3002',
    changeOrigin: true  // This fixes CORS
  }
}
```

**Alternative Solution (CORS Middleware)**:
```javascript
// backend-api/server-fast.js
import cors from 'cors';

app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:5173'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
}));
```

### Scenario 3: Port Already in Use

**Full Error**:
```
Error: listen EADDRINUSE: address already in use :::3002
```

**Root Cause**: Another process is using the port

**Diagnostic Steps**:
```bash
# Find process using port (Windows)
netstat -ano | findstr :3002
# Note the PID (last column)

# Find process using port (Linux/Mac)
lsof -i :3002
```

**Solution**:
```bash
# Kill process (Windows)
taskkill /F /PID [PID_NUMBER]
# Or kill all node processes:
taskkill /F /IM node.exe

# Kill process (Linux/Mac)
kill -9 [PID]
# Or:
killall node
```

### Scenario 4: Environment Variables Not Loading

**Symptoms**:
- `process.env.BACKEND_PORT` is `undefined`
- `import.meta.env.VITE_BACKEND_PORT` is `undefined`

**Diagnostic Steps**:
```bash
# Check .env exists
ls .env
ls frontend/.env

# Check variable names
cat .env
# Backend uses: BACKEND_PORT
# Frontend uses: VITE_BACKEND_PORT (must start with VITE_)

# Check dotenv is loaded (backend)
cat backend-api/server-fast.js | grep dotenv

# Check if servers were restarted after .env changes
```

**Solution**:
```javascript
// backend-api/server-fast.js
import dotenv from 'dotenv';
dotenv.config({ path: '../.env' });  // Load from root
const PORT = process.env.BACKEND_PORT || 3001;

// frontend/vite.config.js
import { loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backendPort = env.VITE_BACKEND_PORT || 3002;

  return {
    server: {
      proxy: {
        '/api': {
          target: `http://localhost:${backendPort}`
        }
      }
    }
  };
});
```

### Scenario 5: Proxy Not Working

**Symptoms**:
- Fetch to `/api/endpoint` returns 404
- Proxy logs not appearing in terminal

**Diagnostic Steps**:
```bash
# 1. Check vite.config.js syntax
cat frontend/vite.config.js

# 2. Verify proxy configuration loaded
# Frontend terminal should show: "Proxy configured for /api"

# 3. Test direct backend access
curl http://localhost:BACKEND_PORT/api/endpoint

# 4. Test through proxy
curl http://localhost:FRONTEND_PORT/api/endpoint

# 5. Check frontend is making requests to /api/*
# Browser DevTools → Network tab → Request URL should start with /api
```

**Common Mistakes**:
```javascript
// ❌ WRONG - Missing /api prefix in fetch
fetch('/chat')  // Won't proxy

// ✅ CORRECT - Has /api prefix
fetch('/api/chat')  // Will proxy

// ❌ WRONG - Full URL bypasses proxy
fetch('http://localhost:3002/api/chat')

// ✅ CORRECT - Relative URL uses proxy
fetch('/api/chat')
```

**Solution**:
1. Ensure vite.config.js has proxy configuration
2. Clear Vite cache: `rm -rf node_modules/.vite`
3. Restart frontend: `npm start`
4. Update all fetch calls to use relative paths

### Scenario 6: Vite Cache Issues

**Symptoms**:
- Proxy changes not applying
- Old configuration still running
- Changes require multiple restarts

**Solution**:
```bash
cd frontend

# Windows
rmdir /s /q node_modules\.vite

# Linux/Mac
rm -rf node_modules/.vite

# Restart
npm start
```

### Scenario 7: Mixed Content (HTTP/HTTPS)

**Full Error**:
```
Mixed Content: The page at 'https://example.com' was loaded over HTTPS,
but requested an insecure resource 'http://api.example.com'.
This request has been blocked.
```

**Root Cause**: HTTPS page trying to call HTTP API

**Solution**:
```javascript
// Development - Both HTTP
Frontend: http://localhost:3000
Backend:  http://localhost:3002

// Production - Both HTTPS
Frontend: https://app.example.com
Backend:  https://api.example.com

// Use environment variable to adapt
const API_URL = import.meta.env.PROD
  ? 'https://api.example.com'
  : '/api';
```

### Scenario 8: WebSocket Connection Failed

**Symptoms**:
- WebSocket upgrade fails
- Real-time features not working

**Solution**:
```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:3002',
    changeOrigin: true,
    ws: true  // ← Enable WebSocket support
  }
}
```

## Platform-Specific Issues

### Windows

**Issue**: Command not found
```bash
# Use Windows equivalents:
dir          # Instead of ls
type         # Instead of cat
findstr      # Instead of grep
rmdir /s /q  # Instead of rm -rf
set          # Instead of export
```

**Issue**: Permission denied on port
```bash
# Run as Administrator, or use port >1024
# Ports 1-1023 require admin on Windows
```

### Linux/Mac

**Issue**: Port permission denied
```bash
# Use sudo, or ports >1024
sudo npm start

# Or change to non-privileged port
PORT=3002 npm start
```

**Issue**: Command not found
```bash
# Install missing tools
brew install curl  # Mac
apt-get install curl  # Linux
```

## Advanced Debugging

### Enable Detailed Proxy Logging

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:3002',
    configure: (proxy, options) => {
      proxy.on('error', (err, req, res) => {
        console.log('❌ Proxy error:', err);
      });
      proxy.on('proxyReq', (proxyReq, req, res) => {
        console.log('→ Proxying:', req.method, req.url);
        console.log('  Headers:', proxyReq.getHeaders());
      });
      proxy.on('proxyRes', (proxyRes, req, res) => {
        console.log('← Response:', proxyRes.statusCode, req.url);
        console.log('  Headers:', proxyRes.headers);
      });
    }
  }
}
```

### Monitor Backend Requests

```javascript
// backend-api/server-fast.js
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.url}`);
  console.log('  Headers:', req.headers);
  console.log('  Body:', req.body);
  next();
});
```

### Network Tracing

```bash
# Windows - Packet capture
netsh trace start capture=yes

# Linux - tcpdump
sudo tcpdump -i any port 3002

# Mac - Network sniffer
sudo tcpdump -i any port 3002
```

## Configuration File Templates

### Complete vite.config.js

```javascript
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  // Load env file based on `mode`
  const env = loadEnv(mode, process.cwd(), '');
  const backendPort = env.VITE_BACKEND_PORT || 3002;

  return {
    plugins: [react()],
    server: {
      port: 3000,
      open: true,
      host: true,  // Expose to network
      proxy: {
        '/api': {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
          secure: false,
          ws: true,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('Proxy error:', err);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('Proxying:', req.method, req.url, '->', proxyReq.path);
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log('Response:', proxyRes.statusCode, req.url);
            });
          }
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: true
    }
  };
});
```

### Complete Backend Server Setup

```javascript
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

// Load environment
dotenv.config({ path: '../.env' });

const app = express();
const PORT = process.env.BACKEND_PORT || 3001;

// Middleware
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:5173'],
  credentials: true
}));
app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'Backend API',
    port: PORT,
    timestamp: new Date().toISOString()
  });
});

// API routes
app.post('/api/chat', async (req, res) => {
  try {
    const { message } = req.body;
    // Process request
    res.json({ success: true, response: 'Message received' });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Backend running on http://localhost:${PORT}`);
  console.log(`Health: http://localhost:${PORT}/health`);
});
```

## Prevention Checklist

✅ Use environment variables for all ports
✅ Configure Vite proxy for development
✅ Use relative paths for API calls
✅ Enable detailed logging for debugging
✅ Create automated startup scripts
✅ Write comprehensive tests
✅ Document port configuration
✅ Clear Vite cache after config changes
✅ Test both direct and proxied access
✅ Monitor logs in both terminals

## When All Else Fails

If none of the above solutions work:

1. **Nuclear Option - Complete Reset**:
```bash
# Kill all processes
taskkill /F /IM node.exe

# Clear all caches
rm -rf frontend/node_modules/.vite
rm -rf backend/node_modules
rm -rf frontend/node_modules

# Reinstall
cd backend && npm install
cd ../frontend && npm install

# Verify configuration
cat .env
cat frontend/.env
cat frontend/vite.config.js

# Restart from automated script
./start-dev.bat
```

2. **Create minimal reproduction**:
- Strip down to simplest possible setup
- Single API endpoint
- Single fetch call
- No authentication
- No complex logic

3. **Check external factors**:
- Antivirus/Firewall blocking connections
- VPN interfering with localhost
- Corporate proxy settings
- Windows Defender blocking ports
- WSL vs native Windows differences
