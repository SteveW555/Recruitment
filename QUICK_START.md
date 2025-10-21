# 🐘 Elephant AI - Quick Start Guide

## Get Started in 2 Minutes!

### Prerequisites
- Python 3.12+ installed
- Node.js 18+ installed
- GROQ API key in `.env` file

---

## Step 1: Start the Backend (Terminal 1)

```bash
cd backend-api
python server_python.py
```

You should see:
```
============================================================
        ELEPHANT AI BACKEND SERVER RUNNING
                 (Python/Flask)
============================================================

  [OK] Server:      http://localhost:3001
  [OK] Health:      http://localhost:3001/health
  [OK] Chat API:    POST http://localhost:3001/api/chat
  [OK] GROQ Model:  llama-3.3-70b-versatile
  [OK] System Prompt: NL2SQL for candidates database

  Ready to process queries!
```

---

## Step 2: Start the Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

You should see:
```
  VITE v5.4.21  ready in 1771 ms

  ➜  Local:   http://localhost:3000/
```

---

## Step 3: Open Your Browser

Navigate to: **http://localhost:3000**

---

## Step 4: Start Asking Questions!

Try these example queries in the chat interface:

### Basic Queries
```
Find Python developers
Show available candidates
Who was contacted this week?
```

### Advanced Queries
```
AWS engineers wanting over 100k
Available Python developers contacted recently
Top 5 highest salary expectations
Candidates with fintech experience
```

### Aggregation Queries
```
How many available candidates do we have?
Count candidates by status
What's the average desired salary?
```

---

## What You'll See

1. **Type your question** in the chat input field
2. **Press Enter** or click Send
3. **AI responds** with the SQL query
4. **Chat history** is maintained automatically

---

## Example Interaction

**You**: `Find Python developers`

**AI**:
```sql
select c.first_name, c.last_name, c.primary_email, c.job_title_target
from candidates as c
where c.primary_skills ilike '%python%'
and c.job_title_target ilike '%developer%'
```

**You**: `Who is available?`

**AI**:
```sql
select c.first_name, c.last_name, c.primary_email, c.job_title_target
from candidates as c
where c.current_status ilike '%available%'
```

---

## Troubleshooting

### Backend won't start?
```bash
# Install dependencies
pip install flask flask-cors groq python-dotenv
```

### Frontend won't start?
```bash
# Install dependencies
cd frontend
npm install
```

### Can't connect to backend?
1. Check backend is running on port 3001
2. Open http://localhost:3001/health
3. Should return: `{"status":"ok"}`

### GROQ API errors?
1. Check `.env` file has `GROQ_API_KEY=your_key`
2. Verify network access to api.groq.com
3. Check firewall settings

---

## Stopping the System

1. **Stop Backend**: Press `Ctrl+C` in Terminal 1
2. **Stop Frontend**: Press `Ctrl+C` in Terminal 2

---

## What's Happening Behind the Scenes?

```
Your Question
     ↓
Frontend (React)
     ↓
Backend API (Flask)
     ↓
GROQ AI (with System Prompt)
     ↓
SQL Query
     ↓
Displayed in Chat
```

The system uses a **System + User Prompt** pattern:
- **System Prompt**: Contains all the rules for SQL generation (from `prompts/candidates_nl2sql_system_prompt.txt`)
- **User Prompt**: Your actual question
- **GROQ AI**: Combines both to generate accurate SQL

---

## Key Features

✅ **Natural Language to SQL** - Ask questions in plain English
✅ **Conversation History** - Context maintained across queries
✅ **Real-time Responses** - Typically < 1 second
✅ **Accurate SQL** - Follows PostgreSQL best practices
✅ **Error Handling** - Graceful fallback on errors

---

## Documentation

- **Complete Guide**: `ELEPHANT_AI_INTEGRATION_GUIDE.md`
- **Test Results**: `SYSTEM_TEST_RESULTS.md`
- **Backend API**: `backend-api/README.md`
- **System Prompt**: `prompts/candidates_nl2sql_system_prompt.txt`

---

## Support

**System is ready!** Open http://localhost:3000 and start querying! 🚀
