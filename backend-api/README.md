# Elephant AI Backend API

Backend API server for Elephant AI Assistant with GROQ integration.

## Features

- **GROQ Integration**: Uses llama-3.3-70b-versatile model
- **System Prompt**: NL2SQL for ProActive People candidates database
- **Conversation History**: Maintains chat context per session
- **CORS Enabled**: Works with frontend on different port
- **Health Monitoring**: Health check endpoint

## Installation

```bash
cd backend-api
npm install
```

## Environment Variables

Create a `.env` file in the root directory (or use the existing one):

```env
GROQ_API_KEY=your_groq_api_key_here
BACKEND_PORT=3001
```

## Running the Server

### Production
```bash
npm start
```

### Development (with auto-reload)
```bash
npm run dev
```

Server will start on `http://localhost:3001`

## API Endpoints

### Health Check
```
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "Elephant AI Backend",
  "groq": true,
  "timestamp": "2025-10-21T14:42:00.000Z"
}
```

### Chat
```
POST /api/chat
```

Request Body:
```json
{
  "message": "Find Python developers",
  "sessionId": "elephant-session-1",
  "useHistory": true
}
```

Response:
```json
{
  "success": true,
  "message": "select c.first_name, c.last_name, c.primary_skills, c.job_title_target from candidates as c where c.primary_skills ilike '%python%';",
  "metadata": {
    "model": "llama-3.3-70b-versatile",
    "tokens": {
      "prompt": 450,
      "completion": 35,
      "total": 485
    },
    "responseTime": 850,
    "sessionId": "elephant-session-1",
    "historyLength": 2
  }
}
```

### Clear Conversation
```
POST /api/chat/clear
```

Request Body:
```json
{
  "sessionId": "elephant-session-1"
}
```

### Get Statistics
```
GET /api/chat/stats
```

Response:
```json
{
  "totalSessions": 1,
  "sessions": [
    {
      "sessionId": "elephant-session-1",
      "messageCount": 4,
      "lastActivity": "2025-10-21T14:42:00.000Z"
    }
  ]
}
```

## System Prompt

The server loads the NL2SQL system prompt from:
```
../prompts/candidates_nl2sql_system_prompt.txt
```

This prompt instructs GROQ to:
- Convert natural language to PostgreSQL queries
- Use the candidates database schema
- Apply recruitment-specific logic
- Handle skills, salary, status, and date filtering

## Example Queries

| User Input | Expected SQL Output |
|------------|-------------------|
| "Find Python developers" | `select c.first_name, c.last_name, c.primary_skills from candidates as c where c.primary_skills ilike '%python%';` |
| "Show available candidates" | `select c.first_name, c.last_name, c.current_status from candidates as c where c.current_status ilike '%available%';` |
| "AWS engineers wanting over 100k" | `select c.first_name, c.last_name, c.desired_salary from candidates as c where c.primary_skills ilike '%aws%' and c.desired_salary > 100000;` |

## Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
│   Port 3000     │
└────────┬────────┘
         │ POST /api/chat
         ▼
┌─────────────────┐
│   Backend API   │
│   (Express)     │
│   Port 3001     │
└────────┬────────┘
         │ System + User Prompts
         ▼
┌─────────────────┐
│   GROQ API      │
│   llama-3.3     │
└─────────────────┘
```

## Conversation Management

- **Session-based**: Each session maintains its own conversation history
- **Memory-efficient**: Keeps last 10 exchanges (20 messages) per session
- **Context-aware**: Sends full history to GROQ for contextual responses
- **Optional**: Can disable history with `useHistory: false`

## Performance

- **Average Response Time**: 400-1500ms (depends on GROQ API)
- **Token Usage**: ~400-800 tokens per query
- **Concurrent Sessions**: Unlimited (in-memory storage)
- **Rate Limiting**: None (relies on GROQ API limits)

## Error Handling

All endpoints return structured error responses:

```json
{
  "success": false,
  "error": "Error message",
  "details": "Detailed error information"
}
```

## Security Notes

- **CORS**: Currently allows all origins (configure for production)
- **API Key**: Stored in environment variable
- **Input Validation**: Basic validation on message content
- **Rate Limiting**: Not implemented (add for production)

## Production Considerations

For production deployment:

1. **Add rate limiting** (e.g., express-rate-limit)
2. **Configure CORS** for specific domains
3. **Add authentication** for API endpoints
4. **Use persistent storage** for conversation history (Redis/database)
5. **Add logging** (Winston, Morgan)
6. **Set up monitoring** (health checks, metrics)
7. **Use process manager** (PM2, systemd)
8. **Add request validation** (Joi, express-validator)

## Troubleshooting

### Server won't start
- Check GROQ_API_KEY is set in .env
- Ensure port 3001 is not in use
- Verify system prompt file exists

### GROQ API errors
- Check API key is valid
- Check rate limits
- Review GROQ status page

### CORS errors
- Ensure backend is running on port 3001
- Check frontend is making requests to correct URL
- Verify CORS middleware is enabled

## License

ProActive People - Internal Use
