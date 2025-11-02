"""
AI Router HTTP Server - Persistent server for fast responses.

Runs a FastAPI server that keeps the AI Router loaded in memory,
providing fast Groq LLM-based routing with no model download overhead.

Usage:
    python -m utils.ai_router.http_server

Then call via HTTP:
    POST http://localhost:8888/route
    Body: {"query": "hi", "session_id": "session-1", "user_id": "user-1"}
"""

import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from utils.ai_router.router import AIRouter
from utils.ai_router.groq_classifier import GroqClassifier
from utils.ai_router.storage.session_store import SessionStore
from utils.ai_router.storage.log_repository import LogRepository
from utils.ai_router.agent_registry import AgentRegistry

# Initialize FastAPI app
app = FastAPI(title="AI Router Service", version="1.0.0")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global router instance (loaded once at startup)
router = None


class RouteRequest(BaseModel):
    """Request model for routing queries."""
    query: str
    session_id: str
    user_id: str = "web-user"


class RouteResponse(BaseModel):
    """Response model for routing results."""
    success: bool
    content: Optional[str] = None
    agent: Optional[str] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None  # Classification reasoning from GroqClassifier
    system_prompt: Optional[str] = None  # Full system prompt sent to GroqClassifier
    classification_latency_ms: Optional[int] = None
    fallback_triggered: Optional[bool] = None
    latency_ms: int
    error: Optional[str] = None
    metadata: Optional[dict] = None
    low_confidence_warning: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize AI Router on server startup (runs once)."""
    global router

    print("[*] Starting AI Router HTTP Server...")
    print("[*] Initializing router dependencies...")

    try:
        # Initialize Groq LLM-based classifier
        print("[*] Loading Groq classifier...")
        print("[*] Using Groq LLM-based routing (fast startup, no model download)")
        classifier = GroqClassifier(
            config_path="config/agents.json",
            confidence_threshold=0.70,  # Raised to reduce false positives on vague queries
            routing_model="llama-3.3-70b-versatile",
            temperature=0.3
        )
        print("[OK] Groq classifier ready")

        # Initialize session store
        print("[*] Connecting to Redis...")
        try:
            session_store = SessionStore()
            if not session_store.ping():
                print("[WARN] Redis not available - using in-memory sessions")
                from utils.ai_router.storage.in_memory_session_store import InMemorySessionStore
                session_store = InMemorySessionStore()
            else:
                print("[OK] Redis connected")
        except Exception as e:
            print(f"[WARN] Redis unavailable: {e}")
            print("[INFO] Using in-memory session store (development mode)")
            from utils.ai_router.storage.in_memory_session_store import InMemorySessionStore
            session_store = InMemorySessionStore()

        # Initialize log repository (optional)
        print("[*] Connecting to PostgreSQL...")
        try:
            log_repository = LogRepository()
            if not log_repository.test_connection():
                raise ConnectionError("PostgreSQL not available")
            print("[OK] PostgreSQL connected")
        except Exception as e:
            print(f"[WARN] PostgreSQL unavailable: {e}")
            print("[INFO] Continuing without logging (development mode)")
            log_repository = None

        # Initialize agent registry
        print("[*] Loading agents...")
        agent_registry = AgentRegistry("config/agents.json")
        status = agent_registry.instantiate_agents()
        available = sum(1 for s in status.values() if s == "OK")
        print(f"[OK] {available} agent(s) loaded", file=sys.stderr)

        # Initialize router
        print("[*] Initializing router...", file=sys.stderr)
        confidence_threshold = 0.70  # Raised to reduce false positives on vague queries
        router = AIRouter(
            classifier=classifier,
            session_store=session_store,
            log_repository=log_repository,
            agent_registry=agent_registry,
            confidence_threshold=confidence_threshold
        )
        print(f"[*] Router confidence threshold: {confidence_threshold}", file=sys.stderr)
        print("[OK] Router ready", file=sys.stderr)
        print("[*] Server ready on http://localhost:8888", file=sys.stderr)
        print("[*] Using Groq LLM routing - fast startup, intelligent routing!", file=sys.stderr)

    except Exception as e:
        print(f"[ERROR] Failed to initialize: {e}", file=sys.stderr)
        raise


@app.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    """
    Route a query to the appropriate agent.

    This endpoint is fast because the model is already loaded!
    """
    if router is None:
        raise HTTPException(status_code=503, detail="Router not initialized")

    try:
        # Log the routing call
        print(f"[HTTP Server] Routing query for user {request.user_id}, session {request.session_id}", file=sys.stderr)
        sys.stderr.flush()

        # Route the query (fast - model already loaded!)
        result = await router.route(
            query_text=request.query,
            user_id=request.user_id,
            session_id=request.session_id
        )

        # Format response
        if result['success']:
            agent_response = result.get('agent_response')
            decision = result.get('decision')

            # Log metadata for debugging
            if agent_response and agent_response.metadata:
                print(f"[HTTP Server] Agent metadata keys: {list(agent_response.metadata.keys())}", file=sys.stderr)
                if 'sql_query' in agent_response.metadata:
                    print(f"[HTTP Server] SQL query present in metadata: {agent_response.metadata['sql_query'][:100]}...", file=sys.stderr)
                if 'result_count' in agent_response.metadata:
                    print(f"[HTTP Server] Result count in metadata: {agent_response.metadata['result_count']}", file=sys.stderr)

            # Add router debug info to metadata
            metadata = agent_response.metadata if agent_response else {}
            if metadata is None:
                metadata = {}

            # Add router debug messages (combines HTTP server + router.py messages)
            debug_messages = [
                f"[HTTP Server] Routing query for user {request.user_id}, session {request.session_id}",
                f"[Router] Routing Called: query for user {request.user_id}, session {request.session_id}",
                f"[Router] Agent={decision.primary_category.value if decision else 'unknown'}, Confidence={decision.primary_confidence if decision else 0:.1%}"
            ]
            metadata['router_debug'] = '\n'.join(debug_messages)

            return RouteResponse(
                success=True,
                content=agent_response.content if agent_response else None,
                agent=decision.primary_category.value if decision else None,
                confidence=decision.primary_confidence if decision else None,
                reasoning=decision.reasoning if decision else None,
                system_prompt=getattr(decision, 'system_prompt', None) if decision else None,
                classification_latency_ms=decision.classification_latency_ms if decision else None,
                fallback_triggered=decision.fallback_triggered if decision else None,
                latency_ms=result['latency_ms'],
                metadata=metadata,
                low_confidence_warning=result.get('low_confidence_warning')
            )
        else:
            return RouteResponse(
                success=False,
                latency_ms=result['latency_ms'],
                error=result.get('error', 'Unknown error')
            )

    except Exception as e:
        return RouteResponse(
            success=False,
            latency_ms=0,
            error=f"Router error: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "router_initialized": router is not None,
        "service": "AI Router"
    }


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8888,
        log_level="info"
    )
