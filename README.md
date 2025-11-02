# Elephant AI - ProActive People Recruitment System

Enterprise recruitment automation platform with AI-powered candidate matching and workflow automation.

---

## 🚀 Quick Start (Simple - One Command!)

### Prerequisites
- Node.js 18+ and npm
- Python 3.12+
- Git

### Start Everything
```cmd
start-all.bat
```

That's it! This starts:
- Python AI Router (port 8888)
- Node.js Backend (port 3002)
- React Frontend (port 3000)

**To stop:** Press `Ctrl+C` in the terminal

---

## 📋 Management Commands

### Check Status
```cmd
status-check.bat
```
Shows which services are running with health checks.

### Stop All Services
```cmd
stop-all.bat
```
Emergency stop button - kills all services immediately.

---

## 🔧 Alternative: PM2 Process Manager (Production)

For team environments or production:

### Install PM2 (one-time)
```cmd
npm install -g pm2
```

### PM2 Commands
```cmd
pm2 start ecosystem.config.js    # Start all services
pm2 status                        # Check status
pm2 logs                          # View logs
pm2 logs ai-router               # View specific service
pm2 stop all                      # Stop all
pm2 restart all                   # Restart all
pm2 delete all                    # Remove all
```

### Auto-start on boot
```cmd
pm2 startup       # Setup startup script
pm2 save          # Save current processes
```

---

## 📁 Project Structure

```
recruitment-automation-system/
├── backend-api/          # Node.js Express API (port 3002)
├── frontend/             # React frontend (port 3000)
├── utils/
│   └── ai_router/        # Python AI Router (port 8888)
├── config/
│   └── agents.json       # Agent configuration
├── logs/                 # Log files (auto-created)
├── start-all.bat         # 🎯 One-command startup
├── stop-all.bat          # Emergency stop
├── status-check.bat      # Health check
└── ecosystem.config.js   # PM2 configuration
```

---

## 🏗️ Architecture

### Services

**Python AI Router** (port 8888)
- Query classification
- Agent routing
- 7 specialized agents (Information Retrieval, Data Operations, Problem Solving, etc.)
- Uses Groq LLM for intelligent classification

**Node.js Backend** (port 3002)
- Express API
- Proxies to Python AI Router
- Session management
- API key management

**React Frontend** (port 3000)
- Vite dev server
- Modern React 18
- Tailwind CSS
- Real-time chat interface

---

## 🎯 Core Features

### 7 Specialized AI Agents

1. **Information Retrieval** - Search candidates, jobs, clients
2. **Data Operations** - Create/update records, schedule actions
3. **Problem Solving** - Complex business analysis
4. **Report Generation** - Charts, dashboards, insights
5. **Automation** - Workflow design
6. **Industry Knowledge** - UK recruitment regulations
7. **General Chat** - Casual conversation fallback

### Agent Routing
- Groq LLM-based classification with reasoning
- Confidence scoring (55% threshold)
- Automatic fallback to general chat
- Query logging and analytics

---

## 🔐 Environment Variables

Create `.env` in project root:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
BACKEND_PORT=3002
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 📊 Monitoring

### View Logs
```cmd
# All logs in logs/ directory
logs\ai-router.log          # Python AI Router output
logs\backend.log            # Backend API output
```

### URLs
- Frontend: http://localhost:3000
- Backend Health: http://localhost:3002/health
- AI Router Health: http://localhost:8888/health

---

## 🧪 Testing

### Test Agent Routing
```cmd
python test_routing_fix.py
```

All 7 agents should pass classification tests.

---

## 🐛 Troubleshooting

### Services won't start
1. Check if ports are already in use: `status-check.bat`
2. Stop conflicting services: `stop-all.bat`
3. Check logs in `logs/` directory

### AI Router fails to load
- Ensure Python 3.12+ is installed
- Install requirements: `pip install -r requirements-ai-router.txt`
- Check model cache: `~/.cache/sentence_transformers/`

### Backend can't connect to AI Router
- Ensure AI Router is running: http://localhost:8888/health
- Check environment variables in `.env`

---

## 📚 Documentation

- **Architecture**: See `ARCHITECTURE_ANALYSIS.md`
- **Fast Mode Setup**: See `FAST_MODE_SETUP.md`
- **Project Details**: See `CLAUDE.md`

---

## 🚦 Development Workflow

### Daily Development
```cmd
# Morning - start everything
start-all.bat

# Work on code...

# Evening - stop everything
Ctrl+C (or stop-all.bat)
```

### Before Committing
```cmd
# Test routing
python test_routing_fix.py

# Check status
status-check.bat
```

---

## 📞 Support

ProActive People Ltd.
- Phone: 0117 9377 199
- Email: info@proactivepeople.com
- Location: Bristol, UK

---

## 📄 License

Proprietary - ProActive People Ltd © 2025
