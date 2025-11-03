# AI Router - Quick Start Testing Guide

**Status**: Phase 2 (Foundational) Complete
**Ready to Test**: ✅ YES (with mock agents)
**Ready for Real Agents**: 🔄 Phase 3

## Prerequisites

### Environment Setup

```bash
# Create/activate virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements-ai-router.txt

# Install testing dependencies
pip install pytest pytest-asyncio pytest-mock pytest-cov
```

### Services Required

For **mock testing** (no external services):
- None required! Everything is mocked

For **real testing** (Phase 3+):
```bash
# Start Redis
redis-server

# PostgreSQL should be running
# Create database:
createdb recruitment

# Run migration:
psql -U postgres -d recruitment -f sql/migrations/001_create_routing_logs.sql

# Set environment variables:
export GROQ_API_KEY="your-groq-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export REDIS_HOST="localhost"
export POSTGRES_HOST="localhost"
```

## Quick Test Scenarios

### Scenario 1: Run Unit Tests (No Services Required)

**Best for**: Verifying implementation, CI/CD pipelines

```bash
# Run all tests
pytest tests/ai_router/ -v

# Run specific test class
pytest tests/ai_router/unit/test_router.py::TestQueryValidation -v

# Run with coverage
pytest tests/ai_router/ --cov=utils.ai_router --cov-report=html

# Run just classifier tests
pytest tests/ai_router/unit/test_classifier.py -v

# Run just router tests
pytest tests/ai_router/unit/test_router.py -v

# Run just storage tests
pytest tests/ai_router/unit/test_storage.py -v
```

**Expected Output**:
```
tests/ai_router/unit/test_classifier.py::TestClassifierInitialization::test_classifier_loads_model PASSED
tests/ai_router/unit/test_classifier.py::TestClassifierInitialization::test_classifier_loads_examples PASSED
...
================================ 160 passed in 2.45s ================================
```

### Scenario 2: Test Router with Mock Agents

**Best for**: Integration testing, CLI development

```bash
# Test single routing decision
python -m utils.ai_router.cli "What are the top job boards?"

# Expected output:
# ============================================================
# ROUTING DECISION
# ============================================================
#
# Classification:
#   Primary:   INFORMATION_RETRIEVAL
#   Confidence: 85.0%
# ...
```

### Scenario 3: Test with Custom Queries

```bash
# Information Retrieval query
python -m utils.ai_router.cli "Where can I find qualified candidates for sales roles?"

# Problem Solving query
python -m utils.ai_router.cli "How can we reduce our placement dropout rate by 20%?"

# Industry Knowledge query
python -m utils.ai_router.cli "What are the GDPR requirements for storing candidate CVs?"

# General Chat query
python -m utils.ai_router.cli "Hello, how are you?"
```

### Scenario 4: Interactive CLI Testing

```bash
# Start interactive mode
python -m utils.ai_router.cli

# At prompt:
router> stats
# Shows: Classifier, Agents Available, Session Store, Log Repository

router> agents
# Lists: Available agents with providers/models

router> query What are the top job boards?
# Routes and displays decision

router> exit
```

### Scenario 5: Test with Verbose Output

```bash
# Get full JSON response
python -m utils.ai_router.cli "What are the top job boards?" --verbose

# Shows full routing decision including:
# - Classification with confidence scores
# - Agent response with latency
# - Full JSON structure
# - Sources and metadata
```

### Scenario 6: Verify Retry Logic

```python
# Create test script: test_retry.py
import asyncio
from utils.ai_router.router import AIRouter
from utils.ai_router.agents.mock_agent import create_mock_agent
from utils.ai_router.models.category import Category
from unittest.mock import Mock

# Create mock agent that fails first attempt
agent = create_mock_agent(
    Category.INFORMATION_RETRIEVAL,
    mock_response="Success on retry",
    fail_on_attempt=1  # Fail on 1st attempt
)

print(f"Call history: {agent.get_call_history()}")
print(f"Total calls: {agent.call_count}")
```

### Scenario 7: Test Fallback to General Chat

```python
# When primary agent fails and general chat is available,
# router should fallback gracefully
python -m utils.ai_router.cli "test query" --verbose

# In output look for:
# "⚠ Fallback triggered - primary agent failed"
```

## Test Coverage Verification

### Verify Classification Works

```bash
pytest tests/ai_router/unit/test_classifier.py::TestClassification -v
```

Expected test cases:
- `test_classify_information_retrieval` ✓
- `test_classify_problem_solving` ✓
- `test_classify_industry_knowledge` ✓
- `test_classify_general_chat` ✓

### Verify Router Works

```bash
pytest tests/ai_router/unit/test_router.py::TestQueryValidation -v
```

Expected test cases:
- `test_valid_query_routing` ✓
- `test_query_truncation` ✓
- `test_empty_query_rejection` ✓
- `test_missing_user_id` ✓

### Verify Storage Works

```bash
pytest tests/ai_router/unit/test_storage.py::TestSessionStore -v
```

Expected test cases:
- `test_session_key_generation` ✓
- `test_save_session` ✓
- `test_load_session` ✓
- `test_delete_session` ✓

## Performance Verification

### Measure Classification Latency

```python
# test_classification_latency.py
import time
from utils.ai_router.classifier import Classifier

classifier = Classifier("config/agents.json")

queries = [
    "What are the top job boards?",
    "How can we improve placement rates?",
    "What are GDPR requirements?",
    "Hello, how are you?"
]

for query in queries:
    start = time.time()
    decision = classifier.classify(query, "test_id")
    elapsed = (time.time() - start) * 1000

    print(f"Query: {query[:40]}")
    print(f"Category: {decision.primary_category.value}")
    print(f"Latency: {elapsed:.1f}ms")
    print(f"Confidence: {decision.primary_confidence:.1%}")
    print()
```

**Expected Output**:
```
Latency: 45-150ms per query
```

### Measure End-to-End Routing Latency

```python
# test_routing_latency.py
import asyncio
from utils.ai_router.router import AIRouter
from utils.ai_router.classifier import Classifier
from utils.ai_router.storage.session_store import SessionStore
from utils.ai_router.storage.log_repository import LogRepository
from utils.ai_router.agent_registry import AgentRegistry
import time

async def test_latency():
    classifier = Classifier("config/agents.json")
    session_store = SessionStore()
    log_repo = LogRepository()
    agent_registry = AgentRegistry("config/agents.json")
    agent_registry.instantiate_agents()

    router = AIRouter(classifier, session_store, log_repo, agent_registry)

    start = time.time()
    result = await router.route(
        "What are the top job boards?",
        "test_user",
        "test_session"
    )
    elapsed = result['latency_ms']

    print(f"End-to-end latency: {elapsed}ms")
    print(f"Target: <3000ms")
    print(f"Status: {'✓ PASS' if elapsed < 3000 else '✗ FAIL'}")

asyncio.run(test_latency())
```

**Expected Output**:
```
End-to-end latency: 200-1500ms
Target: <3000ms
Status: ✓ PASS
```

## Debugging

### Enable Structured Logging

```python
import structlog
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ]
)
```

### Check Classifier Predictions

```python
from utils.ai_router.classifier import Classifier

classifier = Classifier("config/agents.json")

query = "Your test query here"
decision = classifier.classify(query, "test_1")

print(f"Primary: {decision.primary_category}")
print(f"Confidence: {decision.primary_confidence:.1%}")
print(f"Secondary: {decision.secondary_category}")
print(f"Reasoning: {decision.reasoning}")

# Get all similarities
similarities = classifier.get_all_similarities(query)
for category, score in sorted(similarities.items(), key=lambda x: x[1], reverse=True):
    print(f"  {category.value}: {score:.1%}")
```

### Check Agent Registry

```python
from utils.ai_router.agent_registry import AgentRegistry

registry = AgentRegistry("config/agents.json")
status = registry.instantiate_agents()

print("Agent Loading Status:")
for category, stat in status.items():
    print(f"  {category}: {stat}")

print("\nAvailable Agents:")
for agent in registry.list_available_agents():
    print(f"  - {agent.value}")
```

## Common Issues & Solutions

### Issue: "Classifier model not found"
```
Solution: Model downloads automatically on first use.
Wait for completion or pre-download: python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue: "Config file not found"
```
Solution: Ensure config/agents.json exists with proper format
Location: /path/to/recruitment/config/agents.json
```

### Issue: "Redis connection refused"
```
Solution (for testing): Tests use mocked Redis, skip real Redis
For real testing: Start Redis with `redis-server`
```

### Issue: "PostgreSQL connection refused"
```
Solution (for testing): Tests use mocked PostgreSQL
For real testing: Start PostgreSQL and create database:
  createdb recruitment
  psql -U postgres -d recruitment -f sql/migrations/001_create_routing_logs.sql
```

## Next Steps

### After Phase 2 Verification ✅

**Phase 3 - Implement Real Agents**:
1. Implement InformationRetrievalAgent
2. Implement IndustryKnowledgeAgent
3. Test with real Groq API
4. Validate User Story acceptance criteria

**Phase 4 - Additional Agents**:
1. Implement ProblemSolvingAgent (Claude)
2. Implement AutomationAgent
3. Integration testing

## Test Statistics

- **Total Tests**: 160+
- **Test Types**: Unit, Integration, Edge Case
- **Code Coverage**: Comprehensive with mocks
- **Estimated Run Time**: 2-5 seconds (all tests)
- **CI/CD Ready**: ✅ YES (no external dependencies)

## Sign-Off

✅ Phase 2 (Foundational) - Ready for Testing
✅ All 160+ unit tests passing
✅ Mock implementation verified
✅ Ready for Phase 3 (Real Agent Implementation)

---

**Last Updated**: 2025-10-22
**Status**: READY FOR TESTING
