# Chat System Expert Skill

A comprehensive skill providing expert knowledge about the ProActive People chat system architecture, agents, classification, and configuration.

## What This Skill Covers

This skill makes Claude an expert in answering questions about:

- **Chat Interface & Architecture** - How the React frontend, Express backend, and Python AI Router work together
- **7 Specialized Agents** - Each agent's purpose, configuration, LLM model, tools, and when it's used
- **Query Classification** - Both regex (frontend) and semantic ML (AI Router) classification systems
- **API Endpoints** - Complete reference for `/api/chat`, `/api/chat/clear`, `/api/chat/stats`
- **Configuration Management** - agents.json structure, environment variables, LLM model selection
- **Data Flow** - Step-by-step journey of messages from frontend through routing to LLM and back
- **Session Management** - Conversation history, context persistence, message trimming
- **Routing Logic** - Confidence thresholds, fallback mechanisms, timeout/retry strategies
- **Performance & Reliability** - Latency targets, throughput, error handling, monitoring

## File Structure

```
chat/
├── SKILL.md                              # Main skill definition with frontmatter
├── README.md                             # This file
└── references/
    ├── chat-architecture.md              # System architecture & complete data flow
    ├── agent-types.md                    # All 7 agents with specs
    ├── api-endpoints.md                  # API reference with examples
    ├── configuration.md                  # Config file reference & tuning
    └── query-classification.md           # Classification systems explained
```

## Key Features

### Comprehensive Architecture Documentation
- 3-layer system: Frontend (React) → Backend (Express) → AI Router (Python)
- Complete message flow from user input to AI response
- Error handling and fallback mechanisms
- Performance targets and reliability patterns

### Detailed Agent Reference
- All 7 agents fully documented:
  - General Chat (fallback)
  - Information Retrieval (P1 MVP)
  - Problem Solving (P2)
  - Report Generation (P3)
  - Automation (P2)
  - Industry Knowledge (P1 MVP)
  - Data Operations (P1 MVP)
- For each: purpose, configuration, LLM model, tools, example queries, response format

### Complete API Documentation
- All endpoints: `/api/chat`, `/api/chat/clear`, `/api/chat/stats`, `/health`
- Request/response formats with examples
- Error codes and handling strategies
- Retry logic and best practices
- Code examples in JavaScript and Python

### Configuration Reference
- agents.json structure and all fields explained
- Environment variable configuration
- LLM model selection and settings
- Temperature tuning guide
- Runtime configuration without server restart
- Performance tuning strategies

### Classification System Deep Dive
- Regex patterns (frontend) explained
- Semantic ML classification (AI Router) explained
- Confidence thresholds and routing logic
- Example queries for each agent
- Improving classification accuracy
- Classification drift monitoring

## Use This Skill When

Ask Claude about:
- "How does the chat interface work?"
- "What agents are available and when are they used?"
- "How are queries classified and routed?"
- "What API endpoints are available?"
- "How do I configure an agent?"
- "How does conversation history work?"
- "What are the performance targets?"
- "How do I add a new agent?"
- "What LLM models are being used?"
- "How does semantic classification work?"
- "What happens when an agent times out?"
- "How do I debug routing issues?"
- "How can I improve classification accuracy?"
- "What temperature settings should I use?"
- "How do I change which LLM an agent uses?"

Any question about how the chat system works, how to configure it, how to extend it, or how to debug issues.

## Content Highlights

### Architecture Overview
- Detailed 3-layer architecture with data flow diagrams
- Frontend regex classification for immediate feedback
- Backend message assembly and LLM API calls
- AI Router semantic classification using sentence transformers
- Session management (in-memory, Redis, PostgreSQL)

### Agent System
- 7 specialized agents with different priorities (P1, P2, P3)
- Agent contract: timeout protection, error handling, response format
- Agent Registry for dynamic loading
- Configuration-driven agent definitions

### Classification
- Dual-layer approach: regex (fast, frontend) + GroqClassifier LLM (accurate, backend)
- Groq LLM (llama-3.3-70b-versatile) for intent analysis
- JSON response with category, confidence, and reasoning
- Confidence threshold (0.65 for primary routing)
- Fallback to General Chat when confidence < 0.65

> **Note:** For detailed classification information, see the **`router` skill**.

### Performance & Reliability
- <500ms classification latency (GroqClassifier LLM)
- <2s agent execution timeout
- <3s end-to-end latency target
- Automatic retry with 500ms delay
- Fallback to General Chat on failures
- All decisions logged to PostgreSQL

### Configuration Options
- Change LLM models per agent
- Disable/enable agents at runtime
- Temperature tuning for creativity vs accuracy
- Token limits and max response length
- Example query management for classification
- Timeout and retry configuration

## Integration Points

This skill integrates with:
- **Frontend:** React components in `/frontend/dashboard.jsx`
- **Backend:** Express API in `/backend-api/server-fast.js` with Python router lifecycle management
- **AI Router:** Python components in `/utils/ai_router/` (router.py, groq_classifier.py)
- **Configuration:** `/config/agents.json` and environment variables
- **APIs:** Groq and Anthropic LLM APIs

## Reference Information

Each reference document provides deep-dive information:

**chat-architecture.md** (3000+ words)
- System architecture with ASCII diagrams
- Frontend/Backend/AI Router layer details
- Complete message data flow (14 steps)
- Session management and storage
- Error handling and fallback logic
- Performance targets and reliability

**agent-types.md** (2000+ words)
- BaseAgent contract specification
- All 7 agents fully documented
- Configuration template
- Agent selection criteria
- Instructions for adding new agents

**api-endpoints.md** (2000+ words)
- All 4 endpoints documented
- Request/response formats
- Error handling and codes
- Usage examples (JavaScript/Python)
- Common patterns and retry strategies
- Rate limiting and CORS

**configuration.md** (2500+ words)
- agents.json structure and all fields
- Configuration validation
- LLM model reference
- Environment variable guide
- Backend configuration options
- Best practices and tuning

**query-classification.md** (2000+ words)
- Frontend regex patterns (explained)
- AI Router semantic classification
- Similarity metrics and embeddings
- Confidence thresholds
- Example queries for each agent
- Improving accuracy and monitoring drift

## Total Content

- **Main SKILL.md:** ~2000 words
- **5 Reference Documents:** ~12,000 words
- **Total:** ~14,000 words of expert knowledge
- **Code Examples:** 50+ snippets (JSON, JavaScript, Python)
- **Diagrams:** Architecture, data flow, classification process

## How It Works

When you ask Claude about the chat system, this skill:
1. Provides the main SKILL.md content immediately
2. Claude knows to reference specific reference documents as needed
3. You can directly query the references or ask Claude to search them
4. Quick reference section provides instant answers to common questions

## For Questions About...

| Topic | Reference Document |
|-------|-------------------|
| System architecture & data flow | chat-architecture.md |
| Specific agent details | agent-types.md |
| API endpoints & integration | api-endpoints.md |
| Configuration & tuning | configuration.md |
| Classification systems | query-classification.md |

## Getting Started

1. Use the skill by asking Claude about any aspect of the chat system
2. Claude will reference relevant documentation
3. Ask follow-up questions for deeper understanding
4. Reference specific documents for detailed information

Example questions:
- "How does query classification work? Check the chat skill."
- "What does the Information Retrieval agent do?"
- "How do I add a new agent to the system?"
- "What are the API endpoints available?"
- "How can I improve classification accuracy?"

## Maintenance Notes

This skill is based on the current codebase as of creation date. To keep it current:

1. Update when agents are added/removed
2. Update when API endpoints change
3. Refresh classification patterns if they're updated
4. Add new agents to agent-types.md reference
5. Update configuration reference if agents.json structure changes

## Contact & Support

For questions about the chat system, ask Claude to use this skill. For codebase questions, reference the actual source files:

- `/frontend/dashboard.jsx` - Frontend implementation
- `/backend-api/server-fast.js` - Backend API with Python router management
- `/backend-api/pythonRouterManager.js` - Python AI Router lifecycle
- `/utils/ai_router/` - AI Router Python code
- `/config/agents.json` - Agent configurations
