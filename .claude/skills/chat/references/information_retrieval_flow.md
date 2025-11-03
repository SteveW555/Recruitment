# Information Retrieval Query Flow - Complete Reference

**Last Updated**: 2025-11-03
**Version**: 1.0

## Overview

This document provides a complete technical reference for how Information Retrieval queries flow through the system, from frontend submission through NL2SQL conversion, database execution, and response display.

## Architecture Summary

```
Frontend (React)
   ↓ POST /api/chat
Backend API (Node.js)
   ↓ POST /route
AI Router API (Python FastAPI) [ai_router_api.py:147]
   ↓
AIRouter [router.py:101]
   ↓
GroqClassifier [groq_classifier.py:170]
   ↓ Classification: INFORMATION_RETRIEVAL (confidence: 0.85)
InformationRetrievalAgent [information_retrieval_agent.py:104]
   ├→ NL2SQL Conversion [Groq llama-3.3-70b]
   ├→ SQL Execution [Supabase exec_sql RPC]
   └→ Result Formatting [Groq llama-3.3-70b]
      ↓
Response Display (Frontend)
```

## Complete Flow (12 Steps)

### Step 1: Frontend Query Submission
**File**: `frontend/dashboard.jsx:159`

User submits query "Find Python developers with 5 years experience"

```javascript
const handleSendMessage = async () => {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: userMessage,
      sessionId: 'elephant-session-1',
      useHistory: true
    })
  });
};
```

### Step 2: Backend Proxy
**File**: `backend-api/server-fast.js:60`

Node.js backend proxies to Python AI Router:

```javascript
app.post('/api/chat', async (req, res) => {
  const response = await fetch('http://localhost:8888/route', {
    method: 'POST',
    body: JSON.stringify({
      query: req.body.message,
      session_id: req.body.sessionId,
      user_id: 'web-user'
    })
  });
});
```

### Step 3: AI Router Entry Point
**File**: `utils/ai_router/ai_router_api.py:147`

FastAPI server receives request:

```python
@app.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    result = await router.route(
        query_text=request.query,
        user_id=request.user_id,
        session_id=request.session_id
    )
    return RouteResponse(**result)
```

### Step 4: Router Orchestration
**File**: `utils/ai_router/router.py:101`

Main routing logic:

```python
async def route(self, query_text, user_id, session_id):
    # Create query object
    query = Query(text=query_text, user_id=user_id, session_id=session_id)

    # Load session context (Redis)
    session_context = self.session_store.load(user_id, session_id)

    # Classify query
    decision = self.classifier.classify(query.text, query.id)
    # Returns: INFORMATION_RETRIEVAL, confidence=0.85

    # Get agent from registry
    agent = self.agent_registry.get_agent(decision.primary_category)
    # Returns: InformationRetrievalAgent instance

    # Execute with retry
    response = await self._execute_agent_with_retry(agent, query, session_context)

    return response
```

### Step 5: Query Classification
**File**: `utils/ai_router/groq_classifier.py:170`

LLM-based classification:

```python
def classify(self, query_text, query_id):
    system_prompt = """You are a query classification system.

    Classify into one of:
    - INFORMATION_RETRIEVAL: Database lookups, finding data
    - PROBLEM_SOLVING: Analysis with recommendations
    ...

    Return JSON: {category, confidence, reasoning}
    """

    response = self.groq_client.complete(
        prompt=query_text,
        system_prompt=system_prompt,
        config=CompletionConfig(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=200
        )
    )

    # Parses: {"category": "INFORMATION_RETRIEVAL", "confidence": 0.85, ...}
    return RoutingDecision(
        primary_category=Category.INFORMATION_RETRIEVAL,
        primary_confidence=0.85,
        reasoning="Query requests database lookup for candidates"
    )
```

### Step 6: Agent Execution
**File**: `utils/ai_router/agents/information_retrieval_agent.py:104`

Agent processes request:

```python
async def process(self, request: AgentRequest):
    # Step 1: Convert NL to SQL
    sql_query, nl2sql_prompt = await self._convert_to_sql(request.query)

    # Step 2: Execute SQL
    results, result_count = await self._execute_sql(sql_query)

    # Step 3: Format results
    formatted_response, agent_prompt = await self._format_results(
        request.query, sql_query, results, result_count
    )

    return AgentResponse(
        success=True,
        content=formatted_response,
        metadata={
            'sql_query': sql_query,
            'result_count': result_count,
            'sql_results': results[:10],
            'agent_prompt': agent_prompt
        }
    )
```

### Step 7: NL2SQL Conversion
**File**: `utils/ai_router/agents/information_retrieval_agent.py:219`

Convert natural language to SQL:

```python
async def _convert_to_sql(self, query):
    nl2sql_prompt = """You are a SQL query generator.

    Database Schema:
    - Table: candidates
    - Columns: id, first_name, last_name, email, primary_skills,
               job_title_target, desired_salary, years_experience, ...

    Convert natural language to PostgreSQL queries.
    """

    completion = await asyncio.to_thread(
        self.client.chat.completions.create,
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": nl2sql_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.1,  # Low for consistent SQL
        max_tokens=500
    )

    sql_query = completion.choices[0].message.content.strip()
    # Returns: "SELECT first_name, last_name, email, primary_skills,
    #           years_experience FROM candidates
    #           WHERE primary_skills ILIKE '%Python%'
    #           AND years_experience >= 5 LIMIT 100"

    return sql_query, nl2sql_prompt
```

### Step 8: SQL Execution
**File**: `utils/ai_router/agents/information_retrieval_agent.py:284`

Execute SQL via Supabase:

```python
async def _execute_sql(self, sql_query):
    # Call Supabase RPC function
    rpc_builder = self.supabase.rpc('exec_sql', {'query': sql_query})
    response = await asyncio.to_thread(rpc_builder.execute)

    if isinstance(response.data, dict) and 'error' in response.data:
        # SQL execution error
        return [], 0

    results = response.data if isinstance(response.data, list) else []
    return results, len(results)
```

**Database Function**: `sql/migrations/004_create_exec_sql_function.sql`

```sql
CREATE OR REPLACE FUNCTION exec_sql(query text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  result jsonb;
BEGIN
  -- Execute dynamic SQL and return as JSONB
  EXECUTE format('SELECT jsonb_agg(row_to_json(t.*)) FROM (%s) t', query)
    INTO result;

  IF result IS NULL THEN
    result := '[]'::jsonb;
  END IF;

  RETURN result;
EXCEPTION
  WHEN OTHERS THEN
    RETURN jsonb_build_object('error', SQLERRM, 'detail', SQLSTATE);
END;
$$;
```

**Example Response**:
```json
[
  {
    "id": 1234,
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@example.com",
    "primary_skills": "Python, Django, REST APIs",
    "job_title_target": "Senior Python Developer",
    "years_experience": 7,
    "desired_salary": 75000
  },
  {
    "id": 5678,
    "first_name": "Sarah",
    "last_name": "Johnson",
    "email": "sarah.j@example.com",
    "primary_skills": "Python, FastAPI, PostgreSQL",
    "years_experience": 6,
    "desired_salary": 70000
  }
  // ... 45 more results
]
```

### Step 9: Result Formatting
**File**: `utils/ai_router/agents/information_retrieval_agent.py:358`

Format results for user display:

```python
async def _format_results(self, original_query, sql_query, results, result_count):
    agent_prompt = f"""You are a recruitment assistant.

User Query: {original_query}
SQL Query Executed: {sql_query}
Results Retrieved: {result_count} candidates

Results Data:
{self._format_results_for_llm(results[:5])}

Provide a concise, professional summary (150-200 words):
1. State how many candidates were found
2. Highlight key details from top results
3. Mention notable patterns
"""

    completion = await asyncio.to_thread(
        self.client.chat.completions.create,
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": agent_prompt},
            {"role": "user", "content": "Format the results"}
        ],
        temperature=0.3,
        max_tokens=400
    )

    formatted_response = completion.choices[0].message.content.strip()
    return formatted_response, agent_prompt
```

**Example Formatted Response**:
```
I found 47 Python developers with 5+ years of experience in our database.

Top Candidates:
• John Smith - 7 years experience as Senior Python Developer, specializing in
  Django and REST APIs. Currently seeking £75k, based in Bristol.

• Sarah Johnson - 6 years as Python Backend Engineer, expert in FastAPI and
  PostgreSQL. Looking for £70k, located in London.

• Michael Chen - 8 years with strong Python/AWS background, DevOps experience.
  Seeking £80k, Bristol-based.

These candidates are all actively seeking opportunities and have strong
Python expertise across various frameworks. Would you like more details on
any specific candidates or to filter by other criteria?

Source: Supabase Candidates Database
```

### Step 10: Response Propagation
**Files**: `router.py` → `ai_router_api.py` → `server-fast.js` → `dashboard.jsx`

Response flows back through layers:

**Agent Response**:
```python
AgentResponse(
    success=True,
    content="I found 47 Python developers...",
    metadata={
        'sql_query': "SELECT...",
        'result_count': 47,
        'sql_results': [...]
    }
)
```

**Router Result**:
```python
{
    'success': True,
    'content': agent_response.content,
    'agent': 'information-retrieval',
    'confidence': 0.85,
    'reasoning': "Query requests database lookup",
    'classification_latency_ms': 150,
    'latency_ms': 1200,
    'metadata': agent_response.metadata
}
```

**Backend Response**:
```json
{
  "success": true,
  "message": "I found 47 Python developers...",
  "metadata": {
    "agent": "information-retrieval",
    "confidence": 0.85,
    "reasoning": "Query requests database lookup",
    "sql_query": "SELECT...",
    "result_count": 47,
    "sql_results": [...],
    "classification_latency_ms": 150,
    "processingTime": 1200,
    "sessionId": "elephant-session-1"
  }
}
```

### Step 11: Frontend Display
**File**: `frontend/dashboard.jsx:341`

Add AI message to chat:

```javascript
setMessages(prev => [...prev, {
  id: prev.length + 1,
  type: 'ai',
  text: data.message,
  timestamp: new Date().toLocaleTimeString(),
  metadata: data.metadata
}]);
```

### Step 12: Console Logging
**File**: `frontend/dashboard.jsx:288-338`

Log metadata to System Console:

```javascript
addLog(`━━━ SQL QUERY GENERATED ━━━`, 'info');
addLog(metadata.sql_query, 'info');
addLog(`━━━ SQL RESULTS (${metadata.result_count} total) ━━━`, 'info');
addLog(JSON.stringify(metadata.sql_results, null, 2), 'info');
addLog(`Agent: ${metadata.agent} | Confidence: ${metadata.confidence * 100}%`, 'info');
addLog(`Classification: ${metadata.classification_latency_ms}ms`, 'info');
addLog(`Agent response received`, 'success');
```

## Performance Breakdown

### Latency by Step (Example)
```
Step 1: Frontend submission         20ms  (Network)
Step 2: Backend proxy                30ms  (HTTP)
Step 3: AI Router entry               5ms  (FastAPI)
Step 4: Router orchestration         10ms  (Python)
Step 5: Classification (Groq)       150ms  (LLM)
Step 6: Agent initialization          5ms  (Python)
Step 7: NL2SQL (Groq)               200ms  (LLM)
Step 8: SQL execution               350ms  (Supabase)
Step 9: Formatting (Groq)           250ms  (LLM)
Step 10: Response propagation        30ms  (HTTP)
Step 11: Frontend display            20ms  (React)
Step 12: Console logging              5ms  (DOM)
----------------------------------------
Total:                             1075ms  (Target: <3000ms ✅)
```

### Performance Targets
- **Classification**: <500ms (95th percentile)
- **NL2SQL Conversion**: <300ms
- **SQL Execution**: <500ms
- **Result Formatting**: <300ms
- **End-to-End**: <3000ms (95th percentile)

## Error Handling

### Classification Failure
```python
if decision.primary_confidence < 0.70:
    decision.primary_category = Category.GENERAL_CHAT
    decision.fallback_triggered = True
```

### Agent Timeout
```python
try:
    response = await asyncio.wait_for(
        agent.process(request),
        timeout=2.0  # 2 seconds
    )
except asyncio.TimeoutError:
    # Retry once
    if attempt < max_retries:
        await asyncio.sleep(0.5)
        continue
    else:
        # Fall back to general chat
        return fallback_response
```

### SQL Error
```python
if isinstance(response.data, dict) and 'error' in response.data:
    error_msg = response.data['error']
    logger.error("sql_execution_error", error=error_msg)
    return [], 0
```

### Fallback Response
If any step fails, the system returns a friendly error:
```
"I'm having trouble accessing the candidate database right now.
Please try again in a moment. If the issue persists, contact support."
```

## Configuration Files

### Agent Configuration
**File**: `config/agents.json`

```json
{
  "information-retrieval": {
    "class": "utils.ai_router.agents.information_retrieval_agent.InformationRetrievalAgent",
    "enabled": true,
    "llm_provider": "groq",
    "llm_model": "llama-3.3-70b-versatile",
    "timeout_seconds": 2,
    "retry_count": 1,
    "example_queries": [
      "Find Python developers with 5+ years experience",
      "Show available candidates",
      "Who was contacted this week?"
    ]
  }
}
```

### NL2SQL Prompt
**File**: `prompts/candidates_nl2sql_system_prompt.txt`

Contains database schema and conversion examples for Groq LLM.

### Classification Prompt
**File**: `prompts/ai_router_classification.json`

Contains category definitions and output format specification.

## Observability

### Log Locations
1. **Browser Console**: `console.log()` statements
2. **System Console Panel**: Color-coded logs in UI
3. **Backend API**: Terminal stdout
4. **AI Router**: `logs/ai-router.log`
5. **SQL Queries**: `logs/sql.log`
6. **Routing Decisions**: PostgreSQL `routing_logs` table

### Example Log Output
```
[Frontend] Response received from backend
[Frontend] SQL query: SELECT first_name, last_name FROM candidates...
[Frontend] Result count: 47

[Backend] Chat request: sessionId=session-1, agent=information-retrieval
[Backend] Routing to Python AI Router at http://localhost:8888

[AI Router] Query classified: INFORMATION_RETRIEVAL (confidence: 0.85)
[AI Router] Agent execution: InformationRetrievalAgent
[AI Router] SQL generated: SELECT first_name, last_name FROM candidates...
[AI Router] SQL execution: 47 results returned
[AI Router] Response formatted: 194 words
```

## Testing

### Manual Testing
```bash
# Test classification
python -m utils.ai_router.cli classify "Find Python developers"

# Test full routing
python -m utils.ai_router.cli query "Find Python developers"

# Test via HTTP
curl -X POST http://localhost:8888/route \
  -H "Content-Type: application/json" \
  -d '{"query": "Find Python developers", "session_id": "test-1", "user_id": "test"}'
```

### Integration Tests
**File**: `tests/ai_router/integration/test_phase3_agents.py`

Contains 14+ test cases covering:
- Agent initialization
- Classification accuracy
- SQL generation
- Result formatting
- End-to-end flow
- Performance metrics

## Common Issues

### Issue: No Results Returned
**Cause**: SQL syntax error or no matching records
**Solution**: Check `logs/sql.log` for generated SQL, verify database contains matching records

### Issue: Slow Response (>5s)
**Cause**: Large result set or slow SQL query
**Solution**: Add LIMIT clause, optimize SQL with indexes, check Supabase performance

### Issue: Routes to Wrong Agent
**Cause**: Low classification confidence or ambiguous query
**Solution**: Rephrase query with more specific keywords, check classification reasoning in metadata

### Issue: SQL Execution Error
**Cause**: Invalid SQL syntax or missing RPC function
**Solution**: Verify exec_sql function exists, check SQL syntax, review error in response.data

## Related Documentation

- **`INFORMATION_RETRIEVAL_FLOW_GUIDE.md`** - Complete 12-step guide with code examples
- **`complete_system_architecture.md`** - Full system architecture (router skill)
- **`sql/migrations/004_create_exec_sql_function.sql`** - Database RPC function
- **`prompts/candidates_nl2sql_system_prompt.txt`** - NL2SQL conversion prompt

---

**Version**: 1.0
**Last Updated**: 2025-11-03
