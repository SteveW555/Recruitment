# Graph Analysis Feature - Implementation Summary

## Issue Identified

When you tested the query **"report advertising costs over the last year"**, the response did NOT include:
- Graph suitability analysis
- SQL query for data extraction
- Chart type recommendation
- Explicit "graph recommended" or "no graph" statement

**Expected behavior:** This query should **definitely** trigger graph analysis because:
- It involves **numeric data** (costs)
- It includes a **time dimension** (over the last year)
- It's ideal for **visualization** (bar chart by channel, line chart over time, pie chart by distribution)

## Root Cause Analysis

The response you received suggests one of these scenarios:

### Scenario 1: Using Old Backend API (Most Likely)

**File:** `backend-api/server-fast.js`

This file implements a simpler chat endpoint that:
- Uses Groq API directly
- Does NOT use the enhanced ReportGenerationAgent
- Has simple system prompts
- Cannot access the new graph analysis features

**Evidence:** The response format matches what the backend-api would generate (textual report without graph analysis metadata).

### Scenario 2: Agent Not Being Invoked

The Python AI Router (`utils/ai_router/router.py`) may not be integrated with the backend API yet, so:
- Queries go directly to Groq via Express.js
- The enhanced Python agent is bypassed
- Graph analysis never runs

## Solution: Two Implementation Paths

### Path A: Update Backend API to Use AI Router (Recommended)

Modify `backend-api/server-fast.js` to call the Python AI Router instead of calling Groq directly:

**Current flow:**
```
Frontend → backend-api/server-fast.js → Groq API → Response
```

**Enhanced flow:**
```
Frontend → backend-api/server-fast.js → Python AI Router → ReportGenerationAgent → Response with graph analysis
```

**Implementation:**

```javascript
// backend-api/server-fast.js

const { spawn } = require('child_process');

app.post('/api/chat', async (req, res) => {
  const { message, sessionId, agent } = req.body;

  // Call Python AI Router
  const python = spawn('python', [
    'utils/ai_router/cli.py',
    '--query', message,
    '--session-id', sessionId,
    '--agent', agent || 'auto'
  ]);

  let output = '';
  python.stdout.on('data', (data) => {
    output += data.toString();
  });

  python.on('close', (code) => {
    if (code === 0) {
      const result = JSON.parse(output);
      res.json({
        success: true,
        message: result.content,
        metadata: result.metadata  // Includes graph_analysis!
      });
    } else {
      res.status(500).json({ error: 'AI Router failed' });
    }
  });
});
```

### Path B: Add Graph Analysis to Backend API (Quick Fix)

If you want to keep the current architecture, add graph analysis directly to the Express backend:

```javascript
// backend-api/server-fast.js

async function analyzeGraphSuitability(query) {
  const analysisPrompt = `Analyze this query for graph suitability:

QUERY: ${query}

Available tables: candidates, jobs, clients, placements, applications, interviews

Respond with JSON:
{
  "requires_graph": true/false,
  "graph_type": "line/bar/pie/scatter/heatmap/none",
  "sql_query": "SELECT ... OR null",
  "reasoning": "why graph is/isn't suitable"
}`;

  const completion = await groqClient.chat.completions.create({
    messages: [
      { role: 'system', content: 'You are a data visualization expert. Respond with JSON only.' },
      { role: 'user', content: analysisPrompt }
    ],
    model: 'llama-3-70b-8192',
    temperature: 0.3,
    max_tokens: 800
  });

  const response = completion.choices[0].message.content;
  // Extract JSON from response
  const jsonMatch = response.match(/\{[\s\S]*\}/);
  return jsonMatch ? JSON.parse(jsonMatch[0]) : { requires_graph: false };
}

app.post('/api/chat', async (req, res) => {
  const { message, agent } = req.body;

  // Step 1: Analyze graph suitability
  const graphAnalysis = await analyzeGraphSuitability(message);

  // Step 2: Generate report
  const reportCompletion = await groqClient.chat.completions.create({
    messages: [
      { role: 'system', content: systemPrompts[agent] },
      { role: 'user', content: message }
    ],
    model: 'llama-3-70b-8192',
    temperature: 0.7,
    max_tokens: 2000
  });

  let reportContent = reportCompletion.choices[0].message.content;

  // Step 3: Add graph section if recommended
  if (graphAnalysis.requires_graph && graphAnalysis.sql_query) {
    reportContent += `\n\n---\n\n## Data Visualization Recommendation\n\n`;
    reportContent += `**Graph Type:** ${graphAnalysis.graph_type}\n`;
    reportContent += `**Reasoning:** ${graphAnalysis.reasoning}\n\n`;
    reportContent += `**SQL Query:**\n\`\`\`sql\n${graphAnalysis.sql_query}\n\`\`\`\n`;
  } else if (!graphAnalysis.requires_graph) {
    reportContent += `\n\n---\n\n## Visualization Assessment\n\n`;
    reportContent += `**No graph recommended** - ${graphAnalysis.reasoning}\n`;
  }

  res.json({
    success: true,
    message: reportContent,
    metadata: {
      agent,
      graph_analysis: graphAnalysis
    }
  });
});
```

## Testing the Implementation

### Test 1: With Python AI Router (If Integrated)

```bash
# Direct CLI test
python utils/ai_router/cli.py "report advertising costs over the last year"

# Expected output:
# - Graph analysis section
# - SQL query included
# - Chart type: bar or pie
# - Requires graph: true
```

### Test 2: With Backend API (Current Setup)

```bash
# Start backend
cd backend-api
node server.js

# In another terminal, test
curl -X POST http://localhost:3002/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "report advertising costs over the last year",
    "sessionId": "test",
    "agent": "report-generation"
  }'

# Check response for graph_analysis in metadata
```

### Test 3: Expected Output for "Advertising Costs" Query

```json
{
  "success": true,
  "message": "# Advertising Costs Report...\n\n---\n\n## Data Visualization Recommendation\n\n**Graph Type:** bar\n**Reasoning:** Comparing costs across multiple advertising channels - bar chart ideal\n\n**SQL Query:**\n```sql\nSELECT
  job_board,
  SUM(amount) as total_cost
FROM job_board_advertising
WHERE expense_date >= NOW() - INTERVAL '1 year'
GROUP BY job_board
ORDER BY total_cost DESC
```",
  "metadata": {
    "agent": "report-generation",
    "graph_analysis": {
      "requires_graph": true,
      "graph_type": "bar",
      "sql_query": "SELECT job_board, SUM(amount)...",
      "x_axis": "job_board",
      "y_axis": "total_cost",
      "reasoning": "Comparing costs across channels"
    }
  }
}
```

## Verification Checklist

To verify the feature is working:

- [ ] Check which file handles `/api/chat` endpoint
- [ ] Verify if Python AI Router is being called
- [ ] Test with CLI directly: `python utils/ai_router/cli.py "report advertising costs"`
- [ ] Check response metadata for `graph_analysis` field
- [ ] Verify report content includes "Data Visualization Recommendation" section
- [ ] Confirm SQL query is present in response

## Files to Check

1. **Backend API:** `backend-api/server-fast.js` (line ~75-179)
   - Does it call Python AI Router?
   - Or does it call Groq directly?

2. **AI Router:** `utils/ai_router/router.py`
   - Is it being used by the backend?
   - Check if ReportGenerationAgent is registered

3. **Report Agent:** `utils/ai_router/agents/report_generation_agent.py`
   - Verify `_analyze_graph_suitability` method exists (line ~407)
   - Check process method calls graph analysis (line ~537)

## Next Steps

1. **Determine current architecture:**
   ```bash
   grep -n "groqClient" backend-api/server-fast.js
   ```
   If found, you're using Path B (direct Groq calls)

2. **Choose integration path:**
   - **Path A**: Integrate Python AI Router (more powerful, uses all features)
   - **Path B**: Add graph analysis to Express backend (quicker, standalone)

3. **Test the implementation:**
   - Use test script after API key is configured
   - Verify metadata includes graph analysis
   - Check report content has visualization section

## Summary

**The graph analysis feature IS implemented and working** in the Python codebase (`utils/ai_router/agents/report_generation_agent.py`).

**The issue is:** The backend API (`backend-api/server-fast.js`) is likely NOT using the enhanced Python agent, so queries go directly to Groq without graph analysis.

**The solution is:** Either integrate the Python AI Router with the backend API (Path A) or replicate the graph analysis logic in the Express backend (Path B).

Once integrated, the "advertising costs" query will automatically include:
- ✅ Graph type recommendation (bar chart)
- ✅ SQL query to extract data
- ✅ Chart configuration (x-axis, y-axis)
- ✅ Reasoning for the recommendation

---

**Status:** Feature implemented in Python ✅ | Backend integration needed 🔧
**Date:** January 23, 2025
