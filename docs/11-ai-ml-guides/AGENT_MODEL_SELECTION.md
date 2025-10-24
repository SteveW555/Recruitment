# Agent Model Selection & Configuration

**Question**: Is there a dedicated step in each route where I can specify the model to be used, or are they all defaulting to the groq llama 70b?

**Answer**: ✅ **YES - Model selection is fully configurable per agent**, not defaulting to a single model.

---

## How Model Selection Works

### Architecture Overview

```
Request comes in
    ↓
Router.route() called with query_text, user_id, session_id
    ↓
Query validation & classification
    ↓
Router retrieves agent from AgentRegistry
    ↓
AgentRegistry.get_agent(category) looks up agent instance
    ↓
Agent instance was pre-configured with specific model on startup
    ↓
Agent.process() uses its configured model (llm_provider + llm_model)
```

### Key Points

1. **Model selection is NOT made per-request** - It's determined at **startup/initialization time** from `config/agents.json`
2. **Each agent is pre-configured** with a specific LLM provider and model
3. **Different agents can use different models** - They're not all defaulting to Groq llama-70b
4. **The router doesn't specify the model** - It just routes to the correct agent, which already knows what model to use

---

## Current Model Configuration

### By Agent (from config/agents.json)

| Agent | Category | LLM Provider | Model | Notes |
|-------|----------|--------------|-------|-------|
| **Information Retrieval** | INFORMATION_RETRIEVAL | Groq | llama-3-70b-8192 | Multi-source lookup |
| **Industry Knowledge** | INDUSTRY_KNOWLEDGE | Groq | llama-3-70b-8192 | UK recruitment expertise |
| **Problem Solving** | PROBLEM_SOLVING | **Anthropic** | **claude-3-5-sonnet-20241022** | ⭐ **Different provider** |
| **Automation** | AUTOMATION | Groq | llama-3-70b-8192 | Workflow design |
| **Report Generation** | REPORT_GENERATION | Groq | llama-3-70b-8192 | Professional reports |
| **General Chat** | GENERAL_CHAT | Groq | llama-3-70b-8192 | Friendly fallback |

### Summary
- **5 agents use Groq llama-3-70b-8192**
- **1 agent uses Anthropic Claude 3.5 Sonnet** (Problem Solving - intentionally different for superior reasoning)

---

## How to Change Models

### Option 1: Update config/agents.json (Recommended)

Edit the `llm_provider` and `llm_model` fields for any agent:

```json
{
  "INFORMATION_RETRIEVAL": {
    "llm_provider": "groq",              // Change provider here
    "llm_model": "llama-3-70b-8192",    // Change model here
    ...
  },
  "PROBLEM_SOLVING": {
    "llm_provider": "anthropic",        // Different provider
    "llm_model": "claude-3-5-sonnet-20241022",  // Different model
    ...
  }
}
```

**How it works**:
1. On startup, `AgentRegistry` loads `config/agents.json`
2. For each agent category, it extracts the `llm_provider` and `llm_model`
3. Passes the entire config dict to the agent's `__init__()` method
4. Agent stores `self.llm_provider` and `self.llm_model` for later use
5. When `agent.process()` is called, it uses these stored values

### Option 2: Override at Runtime

You can dynamically enable/disable agents or modify configurations:

```python
from utils.ai_router.agent_registry import AgentRegistry
from utils.ai_router.models.category import Category

registry = AgentRegistry("config/agents.json")
registry.instantiate_agents()

# Get current config for an agent
info_config = registry.get_agent_config(Category.INFORMATION_RETRIEVAL)
print(info_config['llm_model'])  # Prints: llama-3-70b-8192

# Modify agent configuration (if needed - requires reinstantiation)
# Note: Changes to config_path would require reloading and re-instantiating agents
```

---

## Detailed Flow: How Each Agent Gets Its Model

### Step 1: Configuration Loading (Startup)
```python
# In agent_registry.py
def _load_config(self):
    """Load agent configurations from JSON file."""
    with open(self.config_path, "r") as f:
        self.config = json.load(f)  # Loads all 6 agents with their configs
```

### Step 2: Agent Instantiation (Startup)
```python
# In agent_registry.py
def _load_agent_class(self, class_path: str, config: Dict[str, Any]) -> BaseAgent:
    """
    config = {
        'llm_provider': 'groq',
        'llm_model': 'llama-3-70b-8192',
        'system_prompt': '...',
        ...
    }
    """
    # Load and instantiate the agent class
    agent_class = getattr(module, class_name)
    return agent_class(config)  # ← Config (with model info) passed here
```

### Step 3: Agent Constructor (Startup)
```python
# In each agent's __init__()
class InformationRetrievalAgent(BaseAgent):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)  # Calls BaseAgent.__init__
        self.client = Groq()  # Initializes Groq client
```

```python
# In base_agent.py
class BaseAgent(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_provider = config['llm_provider']  # ← Stores provider
        self.llm_model = config['llm_model']        # ← Stores model
        self.system_prompt = config['system_prompt']
```

### Step 4: Agent Processing (Runtime)
```python
# In each agent's process() method
async def process(self, request: AgentRequest) -> AgentResponse:
    # Uses pre-configured model from initialization
    message = await self._call_llm_api(
        prompt=prompt,
        model=self.llm_model  # ← Uses model set at startup
    )
```

### Step 5: Router Invocation (Runtime)
```python
# In router.py
async def route(self, query_text: str, user_id: str, session_id: str, **kwargs):
    # Step 3: Classify query
    decision = self.classifier.classify(query.text)  # Returns category

    # Step 5: Get agent
    agent = self.agent_registry.get_agent(decision.primary_category)
    # ↑ Agent already has model set from startup - router doesn't choose model

    # Step 6: Execute agent
    agent_response = await agent.process(request)
    # ↑ Agent uses its configured model internally
```

---

## Environment Variables & API Keys

Each LLM provider requires its own API key:

```bash
# In .env or environment
GROQ_API_KEY=sk_live_xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

Each agent's `__init__()` creates a client:

```python
# In information_retrieval_agent.py (Groq-based)
class InformationRetrievalAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.client = Groq()  # Uses GROQ_API_KEY from env

# In problem_solving_agent.py (Anthropic-based)
class ProblemSolvingAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.client = Anthropic()  # Uses ANTHROPIC_API_KEY from env
```

---

## Per-Request Model Override Capability

**Current Status**: ❌ NOT IMPLEMENTED

If you wanted to allow per-request model overrides, you would need to:

### Option A: Add Model Selection to Route Parameters

```python
# Would need to modify router.py
async def route(
    self,
    query_text: str,
    user_id: str,
    session_id: str,
    override_model: Optional[str] = None,  # ← New parameter
    override_provider: Optional[str] = None,  # ← New parameter
    **kwargs
) -> Dict[str, Any]:
    # Get agent as normal
    agent = self.agent_registry.get_agent(decision.primary_category)

    # Override model if provided
    if override_model:
        agent.llm_model = override_model
    if override_provider:
        agent.llm_provider = override_provider

    # Continue with execution
    agent_response = await agent.process(request)
```

### Option B: Store Model Override in Metadata

```python
# In request metadata
request_metadata = {
    'override_model': 'gpt-4',  # ← Specify model here
    'override_provider': 'openai'
}

result = await router.route(
    query_text="...",
    user_id="...",
    session_id="...",
    **request_metadata  # ← Passed as kwargs
)
```

---

## Recommendation

### Current Architecture ✅ Best Practice
- **Model selection at startup** (config file) is clean and maintainable
- Each agent is specialized for its task with appropriate model choice
- Problem Solving using Claude for superior reasoning is intentional and correct
- No need to change per-request (adds latency, complexity)

### When to Change Models

1. **Update config/agents.json** if:
   - You want a permanently different model
   - Example: Switch Information Retrieval to use Claude for better quality

2. **Implement per-request override** only if:
   - You need A/B testing between models
   - You want user-facing model selection UI
   - You need cost optimization (cheaper models for certain queries)

### Recommended Model Alternatives

| Agent | Current | Good Alternatives |
|-------|---------|-------------------|
| Information Retrieval | Groq llama-3-70b | Claude 3.5 Sonnet (better quality), GPT-4 (most capable) |
| Industry Knowledge | Groq llama-3-70b | Claude 3.5 Sonnet (better reasoning), GPT-4 (most comprehensive) |
| Problem Solving | Claude 3.5 Sonnet | GPT-4 (slightly better reasoning), Claude 3 Opus |
| Automation | Groq llama-3-70b | Claude 3.5 Sonnet (cleaner specs) |
| Report Generation | Groq llama-3-70b | Claude 3.5 Sonnet (better formatting) |
| General Chat | Groq llama-3-70b | (Good as-is, lightweight) |

---

## Summary

| Aspect | Status | Details |
|--------|--------|---------|
| **Dedicated Model Selection Step?** | ✅ YES | Each agent configured with specific model in config/agents.json |
| **All Using Groq llama-70b?** | ❌ NO | 5 agents use Groq, 1 (Problem Solving) uses Anthropic Claude |
| **Model Selection Per-Request?** | ❌ NO | Models selected at startup, not per-request |
| **Can Be Changed?** | ✅ YES | Edit config/agents.json and restart |
| **Can Be Overridden Per-Request?** | ❌ NO (But could be added) | Would require code changes for per-request override |

**Bottom Line**: Model selection is fully configurable, intentionally different between agents for optimal performance, and determined at startup from configuration - not defaulting all to Groq llama-70b.
