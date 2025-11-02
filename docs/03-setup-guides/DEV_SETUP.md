# Development Setup - Quick Start

## 🚀 Quick Start (Windows)

### Option 1: Batch Script (Easiest for Windows)
```bash
# From the root directory
dev.bat
```
This opens two separate command windows:
- Backend API on `http://localhost:3002`
- Frontend dev server on `http://localhost:5173`

---

### Option 2: PowerShell (Single Window)
```powershell
# Install dependencies (first time only)
npm run install:all

# Start backend and frontend
npm run dev
```

---

### Option 3: Individual Terminals (Full Control)

**Terminal 1 - Backend:**
```bash
cd backend-api
npm start
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🔧 Setup

### First Time Only
```bash
# Install all dependencies
npm run install:all
```

This installs:
- Root dependencies (concurrently for parallel execution)
- Backend dependencies (`backend-api/`)
- Frontend dependencies (`frontend/`)

---

## 📋 Available Commands

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start backend + frontend together (requires concurrently) |
| `npm run dev:backend` | Start backend only on port 3002 |
| `npm run dev:frontend` | Start frontend only on port 5173 |
| `npm run dev:backend:watch` | Start backend with file watching |
| `npm run install:all` | Install all dependencies |
| `dev.bat` | Windows batch script (opens 2 windows) |
| `./dev.sh` | Linux/Mac shell script |

---

## 🌐 URLs

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:3002/api/chat
- **API docs:** http://localhost:3002/api/docs (if available)

---

## 🔌 Connection Details

The frontend automatically connects to the backend at:
```
http://localhost:3002/api/chat
```

When you send a message in the UI:
1. Frontend classifies the query locally
2. Sends to backend at `http://localhost:3002/api/chat`
3. Backend routes to appropriate AI agent
4. Response displayed in console + chat

If you see `Failed to reach routing service at http://localhost:3002/api/chat`:
- ✗ Backend is not running
- ✓ Start backend using one of the methods above

---

## 🛠️ Configuration

### Backend Port
Set via environment variable `BACKEND_PORT`:
```bash
# Windows (PowerShell)
$env:BACKEND_PORT = "3002"
npm start

# Linux/Mac
BACKEND_PORT=3002 npm start
```

Default port in backend: **3001** (override with env var)

### Frontend Port
Set via Vite config (`frontend/vite.config.js`):
```javascript
server: {
  port: 5173,    // Change here
  open: true
}
```

---

## 📝 Project Structure

```
recruitment/
├── backend-api/          # Node.js Express API
│   ├── server-fast.js    # Main server file (with Python router)
│   ├── pythonRouterManager.js  # Python AI Router lifecycle
│   └── package.json      # Backend scripts
├── frontend/             # React + Vite SPA
│   ├── dashboard.jsx     # Main component
│   └── package.json      # Frontend scripts
├── utils/ai_router/      # Python AI Router
│   ├── router.py         # Main router
│   └── groq_classifier.py  # LLM-based classification
├── scripts/
│   └── start-dev.js      # Cross-platform startup
├── dev.bat              # Windows batch script
├── dev.sh               # Linux/Mac shell script
└── package.json         # Root scripts
```

---

## 🐛 Troubleshooting

### Frontend can't connect to backend
- Check backend is running: `http://localhost:3002`
- Check `BACKEND_PORT=3002` environment variable
- Check no other service using ports 3002 or 5173

### Port already in use
```bash
# Windows - find process on port 3002
netstat -ano | findstr :3002
# Kill it: taskkill /PID <PID> /F

# Linux/Mac
lsof -i :3002
kill -9 <PID>
```

### Module not found errors
```bash
# Reinstall all dependencies
npm run install:all

# Clear cache
rm -rf node_modules backend-api/node_modules frontend/node_modules
npm run install:all
```

---

## 📚 API Endpoint

**POST** `/api/chat`

```javascript
{
  "message": "Find Python developers",
  "sessionId": "elephant-session-1",
  "useHistory": true,
  "agent": "information-retrieval"
}
```

Response:
```javascript
{
  "success": true,
  "message": "AI response here...",
  "metadata": {
    "agent": "information-retrieval",
    "confidence": 0.95,
    "processingTime": 245
  }
}
```

---

## 🎯 Next Steps

1. ✓ Start both services
2. Open http://localhost:5173
3. Try a query like: "Find candidates with 5+ years experience"
4. Check console logs for routing information

---

