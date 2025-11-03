# Complete AI Router System Architecture

**Last Updated**: 2025-11-03
**Version**: 2.0

## System Overview

The AI Router is a persistent FastAPI service that provides intelligent query routing using Groq LLM classification, connecting the Node.js backend to specialized Python agents.

### Architecture Layers

```
Frontend (React)
    ↓ HTTP POST /api/chat
Backend API (Node.js Express) [server-fast.js]
    ↓ HTTP POST /route
AI Router API (Python FastAPI) [utils/ai_router/ai_router_api.py]
    ↓
AIRouter Orchestrator [utils/ai_router/router.py]
    ├→ GroqClassifier [groq_classifier.py]
    ├→ AgentRegistry [agent_registry.py]
    ├→ SessionStore (Redis)
    └→ LogRepository (PostgreSQL)
        ↓
Specialized Agents [utils/ai_router/agents/]
    ├→ InformationRetrievalAgent (NL2SQL → Supabase)
    ├→ ProblemSolvingAgent (Claude 3.5 Sonnet)
    ├→ ReportGenerationAgent (Groq)
    ├→ AutomationAgent (Groq)
    ├→ IndustryKnowledgeAgent (Groq)
    └→ GeneralChatAgent (Groq)
```

## Key Files

### API Layer
- **`utils/ai_router/ai_router_api.py`** - FastAPI server (formerly http_server.py)
  - Port: 8888
  - Endpoints: `/health`, `/route`, `/agents`
  - Keeps router loaded in memory for fast responses (~150ms classification)

### Core Routing
- **`utils/ai_router/router.py`** - Main orchestrator
  - Routes queries through classification → agent selection → execution
  - Manages retries, timeouts, and fallback logic
  - Stores session context and logs decisions

### Classification
- **`utils/ai_router/groq_classifier.py`** - LLM-based classifier
  - Model: llama-3.3-70b-versatile (Groq)
  - Returns: category, confidence (0.0-1.0), reasoning
  - Threshold: 0.70 (configurable)
  - Latency: ~150ms

### Agent Management
- **`utils/ai_router/agent_registry.py`** - Dynamic agent loading
  - Loads agents from config/agents.json
  - Supports enable/disable without restart
  - Validates agent availability

### Lifecycle Management
- **`backend-api/pythonRouterManager.js`** - Process manager
  - Spawns Python process: `python -m utils.ai_router.ai_router_api`
  - Health checks every 1 second
  - Graceful shutdown on exit
  - Logs to `logs/ai-router.log`

## Complete Query Flow (Information Retrieval Example)

### Step 1: Frontend Submission
**File**: `frontend/dashboard.jsx:159`

```javascript
handleSendMessage() {
  await fetch('/api/chat', {
    method: 'POST',
    body: JSON.stringify({
      message: "Find Python developers",
      sessionId: "session-1",
      useHistory: true
    })
  });
}
```

### Step 2: Backend Proxy
**File**: `backend-api/server-fast.js:60`

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

```python
@app.post("/route")
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

```python
async def route(self, query_text, user_id, session_id):
    # Create query object
    query = Query(text=query_text, user_id=user_id, session_id=session_id)

    # Load session context
    session_context = self.session_store.load(user_id, session_id)

    # Classify query
    decision = self.classifier.classify(query.text, query.id)

    # Get agent
    agent = self.agent_registry.get_agent(decision.primary_category)

    # Execute with retry
    response = await self._execute_agent_with_retry(
        agent, query, session_context
    )

    # Save session and log
    self.session_store.save(user_id, session_id, context)
    self.log_repository.log(decision, response)

    return result
```

### Step 5: Query Classification
**File**: `utils/ai_router/groq_classifier.py:170`

```python
def classify(self, query_text, query_id):
    # Build classification prompt
    system_prompt = self._build_classification_prompt()

    # Call Groq LLM
    response = self.groq_client.complete(
        prompt=query_text,
        system_prompt=system_prompt,
        config=CompletionConfig(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=200
        )
    )

    # Parse JSON: {category, confidence, reasoning}
    result = json.loads(response.content)

    # Return decision
    return RoutingDecision(
        query_id=query_id,
        primary_category=Category.INFORMATION_RETRIEVAL,
        primary_confidence=0.85,
        reasoning=result['reasoning'],
        classification_latency_ms=150
    )
```

### Step 6: Agent Execution
**File**: `utils/ai_router/agents/information_retrieval_agent.py:104`

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
            'sql_results': results[:10]
        }
    )
```

### Step 7: NL2SQL Conversion
**File**: `utils/ai_router/agents/information_retrieval_agent.py:219`

```python
async def _convert_to_sql(self, query):
    completion = await asyncio.to_thread(
        self.client.chat.completions.create,
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": self.nl2sql_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.1,
        max_tokens=500
    )

    sql_query = completion.choices[0].message.content.strip()
    # Returns: "SELECT * FROM candidates WHERE primary_skills ILIKE '%Python%'"
    return sql_query, self.nl2sql_prompt
```

### Step 8: SQL Execution (Supabase)
**File**: `utils/ai_router/agents/information_retrieval_agent.py:284`

```python
async def _execute_sql(self, sql_query):
    # Execute via Supabase RPC function
    response = await asyncio.to_thread(
        self.supabase.rpc('exec_sql', {'query': sql_query}).execute
    )

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
  EXECUTE format('SELECT jsonb_agg(row_to_json(t.*)) FROM (%s) t', query) INTO result;
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

### Step 9: Result Formatting
**File**: `utils/ai_router/agents/information_retrieval_agent.py:358`

```python
async def _format_results(self, original_query, sql_query, results, result_count):
    agent_prompt = f"""You are a recruitment assistant.

User Query: {original_query}
SQL Query: {sql_query}
Results: {result_count} candidates

Please provide a concise, professional summary (150-200 words)."""

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
    # Returns: "I found 47 Python developers..."
    return formatted_response, agent_prompt
```

### Step 10: Response Propagation

**Router → API → Backend → Frontend**

Each layer adds metadata and propagates the response:

```python
# Agent Response
AgentResponse(
    success=True,
    content="I found 47 Python developers...",
    metadata={
        'sql_query': "SELECT...",
        'result_count': 47,
        'sql_results': [...]
    }
)

# Router adds classification metadata
router_result = {
    'success': True,
    'content': agent_response.content,
    'agent': 'information-retrieval',
    'confidence': 0.85,
    'reasoning': "...",
    'metadata': agent_response.metadata
}

# Backend adds processing metadata
backend_response = {
    'success': True,
    'message': router_result['content'],
    'metadata': {
        ...router_result['metadata'],
        'agent': 'information-retrieval',
        'confidence': 0.85,
        'processingTime': 1200
    }
}

# Frontend displays and logs
messages.push({
    type: 'ai',
    text: data.message,
    timestamp: '10:32',
    metadata: data.metadata
});
addLog(`Agent: ${metadata.agent} | Confidence: 85%`);
addLog(`SQL QUERY GENERATED: ${metadata.sql_query}`);
```

## Performance Metrics

### Latency Breakdown (Information Retrieval)
```
Classification:        150ms  (Groq LLM)
NL2SQL Conversion:     200ms  (Groq LLM)
SQL Execution:         350ms  (Supabase)
Result Formatting:     250ms  (Groq LLM)
Network Overhead:       50ms  (HTTP requests)
--------------------------------
Total End-to-End:     1000ms  (Target: <3000ms ✅)
```

### Performance Targets
- **Classification**: <500ms (95th percentile)
- **Agent Execution**: <2s (with timeout)
- **End-to-End**: <3s (95th percentile)
- **Throughput**: 1000+ req/s

## Configuration

### Router Configuration
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
      "Find Python developers with 5+ years",
      "Show available candidates",
      "Who was contacted this week?"
    ]
  }
}
```

### Classifier Configuration
**File**: `prompts/ai_router_classification.json`

```json
{
  "version": "1.0",
  "model": "llama-3.3-70b-versatile",
  "temperature": 0.3,
  "max_tokens": 200,
  "system_prompt": "You are a query classification system...",
  "output_format": {
    "type": "json",
    "schema": {
      "category": "string",
      "confidence": "float",
      "reasoning": "string"
    }
  }
}
```

### NL2SQL Prompt
**File**: `prompts/candidates_nl2sql_system_prompt.txt`

```
You are a SQL query generator for a candidates database.

Database Schema:
- Table: candidates
- Columns: id, first_name, last_name, email, phone, primary_skills,
           job_title_target, desired_salary, years_experience,
           current_status, location

Convert natural language to PostgreSQL queries.

Example:
Input: "Find Python developers"
Output: SELECT * FROM candidates WHERE primary_skills ILIKE '%Python%' LIMIT 100;
```

## Error Handling

### Confidence-Based Fallback
```python
if decision.primary_confidence < self.confidence_threshold:
    # Route to general chat
    decision.primary_category = Category.GENERAL_CHAT
    decision.fallback_triggered = True
```

### Agent Timeout/Retry
```python
for attempt in range(self.max_retries + 1):
    try:
        response = await asyncio.wait_for(
            agent.process(request),
            timeout=self.agent_timeout  # 2 seconds
        )
        return response
    except asyncio.TimeoutError:
        if attempt < self.max_retries:
            await asyncio.sleep(self.retry_delay_ms / 1000.0)
            continue
        else:
            # Fall back to general chat
            fallback_agent = self.agent_registry.get_agent(Category.GENERAL_CHAT)
            return await fallback_agent.process(request)
```

### SQL Error Handling
```python
try:
    response = await self.supabase.rpc('exec_sql', {'query': sql_query}).execute()
    if isinstance(response.data, dict) and 'error' in response.data:
        logger.error("sql_execution_error", error=response.data['error'])
        return [], 0
    return response.data, len(response.data)
except Exception as e:
    logger.error("sql_execution_error", error=str(e))
    return [], 0
```

## Observability

### Logging Locations
1. **Browser Console**: Frontend query/response logging
2. **System Console Panel**: UI component with color-coded logs
3. **Backend API Logs**: Terminal stdout
4. **AI Router Logs**: `logs/ai-router.log`
5. **SQL Query Logs**: `logs/sql.log`
6. **PostgreSQL Routing Logs**: `routing_logs` table

### Monitoring Queries
```sql
-- View recent routing decisions
SELECT * FROM routing_logs
ORDER BY created_at DESC
LIMIT 10;

-- Classification accuracy by category
SELECT
  primary_category,
  AVG(primary_confidence) as avg_confidence,
  COUNT(*) as query_count
FROM routing_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY primary_category;

-- Failed routes
SELECT * FROM routing_logs
WHERE success = false
ORDER BY created_at DESC;
```

## Startup Commands

### Development (Integrated)
```bash
npm start  # Starts backend + Python AI Router + frontend
```

### Production (PM2)
```bash
pm2 start config/ecosystem.config.js
pm2 logs ai-router  # View Python router logs
pm2 status          # Check all services
```

### Direct Python Invocation
```bash
python -m utils.ai_router.ai_router_api
```

## Documentation References

For complete end-to-end flow with detailed code traces:
- **`INFORMATION_RETRIEVAL_FLOW_GUIDE.md`** - Complete 12-step trace from query → SQL → display

For agent-specific implementation:
- **Information Retrieval Agent**: NL2SQL conversion, Supabase integration
- **Problem Solving Agent**: Claude 3.5 Sonnet, multi-step analysis
- **Report Generation Agent**: Structured reports with visualizations
- **Automation Agent**: Workflow specifications (n8n, Zapier)
- **Industry Knowledge Agent**: UK recruitment compliance (GDPR, IR35)
- **General Chat Agent**: Friendly fallback conversation

---

**Version History**:
- 2.0 (2025-11-03): Updated with ai_router_api.py rename, complete NL2SQL flow, exec_sql function
- 1.0 (2025-01-01): Initial documentation
