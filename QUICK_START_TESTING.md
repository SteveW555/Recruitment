# Quick Start Testing Guide

## 🚀 Test the Graph Analysis Feature in 5 Minutes

### Prerequisites

Make sure you have:
- ✅ Python dependencies installed (`pip install -r requirements.txt`)
- ✅ Node.js dependencies installed (`npm install` in both `backend-api` and `frontend`)
- ✅ `GROQ_API_KEY` environment variable set
- ✅ Redis running (optional - will use mock if unavailable)
- ✅ PostgreSQL running (optional - will use mock if unavailable)

---

## Step 1: Start Backend (Terminal 1)

```bash
cd backend-api
npm start
```

Wait for:
```
🐘 ELEPHANT AI BACKEND SERVER RUNNING 🐘
✓ Server: http://localhost:3002
```

---

## Step 2: Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Wait for:
```
➜ Local: http://localhost:3000
```

---

## Step 3: Open Browser

Navigate to: **http://localhost:3000**

---

## Step 4: Test Graph Analysis

### Test 1: Advertising Costs (Should Show Graph)

**Type in chat:**
```
report advertising costs over the last year
```

**Expected Result:**
1. ✅ Professional report displays
2. ✅ "Data Visualization Available" section appears below report
3. ✅ Shows: Chart Type, Library, Reasoning
4. ✅ Displays SQL query in code block
5. ✅ "Copy SQL" button present

**System Console Should Show:**
- `[INFO] Python AI Router response in ~2000ms`
- `[SUCCESS] hasGraphAnalysis: true`

---

### Test 2: Company Profile (Should NOT Show Graph)

**Type in chat:**
```
create a company profile for ABC Corporation
```

**Expected Result:**
1. ✅ Company profile report displays
2. ✅ NO graph analysis section (correctly identified as textual)

**System Console Should Show:**
- `[INFO] Python AI Router response in ~1500ms`
- `[INFO] hasGraphAnalysis: false` or `hasGraphAnalysis: undefined`

---

### Test 3: Placement Trends (Should Show Graph)

**Type in chat:**
```
show placement trends over the last 12 months
```

**Expected Result:**
1. ✅ Report with trend analysis
2. ✅ Graph section recommends **line chart**
3. ✅ SQL query includes `DATE_TRUNC('month', ...)`
4. ✅ X-axis: month, Y-axis: placement_count

---

### Test 4: Revenue Comparison (Should Show Graph)

**Type in chat:**
```
compare revenue by division for Q4 2024
```

**Expected Result:**
1. ✅ Report with revenue breakdown
2. ✅ Graph section recommends **bar chart**
3. ✅ SQL query includes `GROUP BY division`
4. ✅ Recommends Recharts or Plotly

---

## Troubleshooting

### ❌ "Python not found"

**Fix:**
1. Check Python is in PATH: `python --version`
2. Or edit `backend-api/server.js` line 97:
   ```javascript
   const pythonPath = 'C:\\Python312\\python.exe'; // Windows
   // or
   const pythonPath = 'python3'; // Linux/Mac
   ```

### ❌ "AI Router execution failed"

**Check backend terminal for error messages:**

Common issues:
1. Missing dependencies: `pip install groq anthropic structlog`
2. Missing API key: `export GROQ_API_KEY=your_key`
3. Redis/PostgreSQL errors (these are optional)

### ❌ Graph section not appearing

**Check browser console (F12):**
- Should see metadata object with `graph_analysis`
- If missing, check backend logs

**Verify:**
1. Backend console shows: `hasGraphAnalysis: true`
2. Network tab shows metadata in response
3. No JavaScript errors in console

### ❌ Frontend compilation errors

```bash
cd frontend
rm -rf node_modules/.vite
npm run dev
```

---

## What Success Looks Like

### ✅ Successful Test

**Backend terminal:**
```
[2025-01-23T10:30:45.123Z] Chat request: { sessionId: 'elephant-session-1', agent: 'auto', ... }
[2025-01-23T10:30:45.124Z] Calling Python AI Router: { agent: 'auto' }
[2025-01-23T10:30:47.456Z] Python AI Router response in 2332ms: {
  success: true,
  agent: 'REPORT_GENERATION',
  confidence: 0.92,
  hasGraphAnalysis: true
}
```

**Browser chat:**
```
┌─────────────────────────────────────────────┐
│ AI Assistant                                │
│                                             │
│ # Advertising Costs Report                 │
│                                             │
│ ## Executive Summary                        │
│ Our advertising costs for the last year... │
│                                             │
│ ─────────────────────────────────────────  │
│                                             │
│ 📊 Data Visualization Available            │
│                                             │
│ Chart Type: bar                            │
│ Library: Plotly                            │
│                                             │
│ SQL Query:                                 │
│ ┌─────────────────────────────────────┐   │
│ │ SELECT job_board,                   │   │
│ │   SUM(amount) as total_cost        │   │
│ │ FROM job_board_advertising          │   │
│ │ WHERE expense_date >= NOW() ...     │   │
│ └─────────────────────────────────────┘   │
│                                             │
│ [ Copy SQL ]                               │
└─────────────────────────────────────────────┘
```

**Browser console:**
```
[SUCCESS] SQL query copied to clipboard
```

---

## Next Steps After Testing

Once all tests pass:

1. **Try More Queries:**
   - "show candidate distribution by status"
   - "analyze job posting trends"
   - "generate quarterly performance dashboard"

2. **Check SQL Queries:**
   - Click "Copy SQL" button
   - Paste into database tool
   - Verify query is valid

3. **Review Recommendations:**
   - Chart types make sense for data?
   - SQL queries are efficient?
   - Library recommendations appropriate?

4. **Performance Check:**
   - Responses under 3 seconds? ✅
   - No timeout errors? ✅
   - Console shows reasonable latency? ✅

---

## Support

If you encounter issues:

1. **Check logs:**
   - Backend terminal (Python errors)
   - Browser console (JavaScript errors)
   - Network tab (API responses)

2. **Review documentation:**
   - [OPTION_2_IMPLEMENTATION_COMPLETE.md](OPTION_2_IMPLEMENTATION_COMPLETE.md)
   - [REPORT_GRAPH_ANALYSIS_FEATURE.md](docs/REPORT_GRAPH_ANALYSIS_FEATURE.md)

3. **Verify configuration:**
   - `config/agents.json` - Check REPORT_GENERATION agent
   - Environment variables - GROQ_API_KEY set?
   - Dependencies - All installed?

---

**Total Testing Time:** ~5 minutes
**Status:** Ready to test! 🎉
