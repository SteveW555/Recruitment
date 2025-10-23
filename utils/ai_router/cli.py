"""
CLI Interface - Command-line testing and development interface for AIRouter.

Provides manual testing capabilities for routing decisions, agent execution,
and debugging without requiring a full API server.
"""

import asyncio
import argparse
import json
import sys
import uuid
from datetime import datetime
from typing import Optional
import structlog

from .router import AIRouter
from .classifier import Classifier
from .storage.session_store import SessionStore
from .storage.log_repository import LogRepository
from .agent_registry import AgentRegistry


# Setup structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class RouterCLI:
    """Command-line interface for router testing and development."""

    def __init__(
        self,
        classifier_model: str = "all-MiniLM-L6-v2",
        config_path: str = "config/agents.json",
    ):
        """
        Initialize CLI with router dependencies.

        Args:
            classifier_model: Sentence-transformers model name
            config_path: Path to agents.json configuration
        """
        self.classifier_model = classifier_model
        self.config_path = config_path

        # Initialize components
        self._initialize_dependencies()

    def _initialize_dependencies(self):
        """Initialize all router dependencies."""
        print("[*] Initializing router dependencies...")

        try:
            # Initialize classifier
            print("[*] Loading classifier...")
            self.classifier = Classifier(
                model_name=self.classifier_model,
                config_path=self.config_path
            )
            print("✓ Classifier ready")

            # Initialize session store
            print("[*] Connecting to Redis...")
            self.session_store = SessionStore()
            if not self.session_store.ping():
                raise ConnectionError("Redis not available")
            print("✓ Redis connected")

            # Initialize log repository
            print("[*] Connecting to PostgreSQL...")
            self.log_repository = LogRepository()
            if not self.log_repository.test_connection():
                raise ConnectionError("PostgreSQL not available")
            print("✓ PostgreSQL connected")

            # Initialize agent registry
            print("[*] Loading agents...")
            self.agent_registry = AgentRegistry(self.config_path)
            status = self.agent_registry.instantiate_agents()
            available = sum(1 for s in status.values() if s == "OK")
            print(f"✓ {available} agent(s) loaded")

            # Initialize router
            print("[*] Initializing router...")
            self.router = AIRouter(
                classifier=self.classifier,
                session_store=self.session_store,
                log_repository=self.log_repository,
                agent_registry=self.agent_registry
            )
            print("✓ Router ready\n")

        except Exception as e:
            print(f"✗ Failed to initialize: {e}")
            sys.exit(1)

    async def run_query(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        verbose: bool = False,
        json_output: bool = False
    ) -> Dict[str, Any]:
        """
        Run a query through the router and display results.

        Args:
            query: Query text
            user_id: User ID (defaults to 'cli-user')
            session_id: Session ID (defaults to random UUID)
            verbose: Whether to display full JSON response
            json_output: Whether to output clean JSON only (for API integration)

        Returns:
            Routing result dictionary
        """
        user_id = user_id or "cli-user"
        session_id = session_id or str(uuid.uuid4())

        if not json_output:
            print(f"[*] Routing query...")
            print(f"    Query: {query[:100]}{'...' if len(query) > 100 else ''}")
            print(f"    User: {user_id}")
            print(f"    Session: {session_id}\n")

        result = await self.router.route(
            query_text=query,
            user_id=user_id,
            session_id=session_id,
            source="cli",
            timestamp=datetime.utcnow().isoformat()
        )

        # JSON output mode (for API integration)
        if json_output:
            output = self._format_json_output(result)
            print(json.dumps(output, indent=2))
            return result

        # Display results (human-readable)
        self._display_result(result, verbose)

        return result

    def _display_result(self, result: Dict, verbose: bool = False):
        """Display routing result in formatted output."""
        if not result.get('decision'):
            print("✗ Routing failed\n")
            print(f"Error: {result.get('error', 'Unknown error')}\n")
            return

        decision = result['decision']
        print("═" * 60)
        print("ROUTING DECISION")
        print("═" * 60)

        # Display classification results
        print(f"\nClassification:")
        print(f"  Primary:   {decision.primary_category.value}")
        print(f"  Confidence: {decision.primary_confidence:.1%}")

        if decision.secondary_category:
            print(f"  Secondary: {decision.secondary_category.value}")
            print(f"  Confidence: {decision.secondary_confidence:.1%}")

        # Display reasoning
        print(f"\nReasoning:")
        print(f"  {decision.reasoning}\n")

        # Display agent response (if available)
        if result.get('agent_response'):
            agent_response = result['agent_response']
            print("═" * 60)
            print("AGENT RESPONSE")
            print("═" * 60)
            print(f"\nSuccess: {'✓' if agent_response.success else '✗'}")

            if agent_response.success:
                print(f"\nContent:")
                # Truncate long responses
                content = agent_response.content
                if len(content) > 500:
                    print(f"  {content[:500]}...")
                else:
                    print(f"  {content}")

                # Display metadata (sources, latency, etc.)
                if agent_response.metadata:
                    print(f"\nMetadata:")
                    if 'agent_latency_ms' in agent_response.metadata:
                        print(f"  Latency: {agent_response.metadata['agent_latency_ms']}ms")
                    if 'sources' in agent_response.metadata:
                        sources = agent_response.metadata['sources']
                        sources_str = ", ".join(sources) if sources else "None"
                        print(f"  Sources: {sources_str}")
            else:
                print(f"Error: {agent_response.error}")

        # Display fallback info
        if decision.fallback_triggered:
            print(f"\n⚠ Fallback triggered - primary agent failed")

        # Display latency
        print(f"\nTotal Latency: {result['latency_ms']}ms")
        print("═" * 60 + "\n")

        # Verbose output (full JSON)
        if verbose:
            print("FULL JSON RESPONSE:")
            print(json.dumps(self._serialize_result(result), indent=2))
            print()

    def _format_json_output(self, result: Dict) -> Dict:
        """Format result for clean JSON output (API integration)."""
        output = {
            'success': result.get('success', False),
            'latency_ms': result.get('latency_ms', 0)
        }

        # Add agent response
        if result.get('agent_response'):
            agent_response = result['agent_response']
            output['content'] = agent_response.content
            output['metadata'] = agent_response.metadata or {}
            output['error'] = agent_response.error

        # Add decision info
        if result.get('decision'):
            decision = result['decision']
            output['agent'] = decision.primary_category.value
            output['confidence'] = decision.primary_confidence

        return output

    def _serialize_result(self, result: Dict) -> Dict:
        """Convert result to JSON-serializable format."""
        serialized = {}

        # Serialize decision
        if result.get('decision'):
            decision = result['decision']
            serialized['decision'] = {
                'primary_category': decision.primary_category.value,
                'primary_confidence': decision.primary_confidence,
                'secondary_category': decision.secondary_category.value if decision.secondary_category else None,
                'secondary_confidence': decision.secondary_confidence,
                'reasoning': decision.reasoning,
                'fallback_triggered': decision.fallback_triggered,
                'classification_latency_ms': decision.classification_latency_ms
            }

        # Serialize agent response
        if result.get('agent_response'):
            agent_response = result['agent_response']
            serialized['agent_response'] = {
                'success': agent_response.success,
                'content': agent_response.content[:200] + '...' if len(agent_response.content) > 200 else agent_response.content,
                'error': agent_response.error,
                'metadata': agent_response.metadata
            }

        serialized['success'] = result.get('success')
        serialized['error'] = result.get('error')
        serialized['latency_ms'] = result.get('latency_ms')

        return serialized

    def display_stats(self):
        """Display router statistics."""
        stats = self.router.get_stats()
        print("═" * 60)
        print("ROUTER STATISTICS")
        print("═" * 60)
        print(f"Classifier: {stats['classifier']}")
        print(f"Agents Available: {stats['agents_available']}")
        print(f"Session Store: {stats['session_store']}")
        print(f"Log Repository: {stats['log_repository']}")
        print("═" * 60 + "\n")

    def display_agent_list(self):
        """Display list of available agents."""
        available = self.agent_registry.list_available_agents()
        print("═" * 60)
        print("AVAILABLE AGENTS")
        print("═" * 60)

        for category in available:
            config = self.agent_registry.get_agent_config(category)
            llm_provider = config.get('llm_provider', 'N/A')
            llm_model = config.get('llm_model', 'N/A')
            print(f"  • {category.value}")
            print(f"    Provider: {llm_provider}")
            print(f"    Model: {llm_model}")

        print("═" * 60 + "\n")

    async def interactive_mode(self):
        """Run interactive query loop."""
        print("═" * 60)
        print("AI ROUTER CLI - Interactive Mode")
        print("═" * 60)
        print("Commands:")
        print("  query <text>   - Route a query")
        print("  stats         - Display router statistics")
        print("  agents        - List available agents")
        print("  clear         - Clear screen")
        print("  exit          - Exit CLI")
        print("═" * 60 + "\n")

        while True:
            try:
                user_input = input("router> ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "exit":
                    print("\nGoodbye!")
                    break

                elif user_input.lower() == "stats":
                    self.display_stats()

                elif user_input.lower() == "agents":
                    self.display_agent_list()

                elif user_input.lower() == "clear":
                    import os
                    os.system("clear" if sys.platform != "win32" else "cls")

                elif user_input.lower().startswith("query "):
                    query_text = user_input[6:].strip()
                    if query_text:
                        await self.run_query(query_text)
                    else:
                        print("Usage: query <text>\n")

                else:
                    print(f"Unknown command: {user_input}\n")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Router CLI - Test and debug query routing"
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="Query to route (interactive mode if not provided)"
    )

    parser.add_argument(
        "--user-id",
        default="cli-user",
        help="User ID for routing (default: cli-user)"
    )

    parser.add_argument(
        "--session-id",
        help="Session ID (defaults to random UUID)"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Display full JSON response"
    )

    parser.add_argument(
        "--config",
        default="config/agents.json",
        help="Path to agents.json configuration"
    )

    parser.add_argument(
        "--model",
        default="all-MiniLM-L6-v2",
        help="Classifier model name"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Display router statistics and exit"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output clean JSON only (for API integration)"
    )

    args = parser.parse_args()

    # Initialize CLI
    cli = RouterCLI(
        classifier_model=args.model,
        config_path=args.config
    )

    # Handle different modes
    if args.stats:
        cli.display_stats()
        cli.display_agent_list()
    elif args.query:
        # Single query mode
        await cli.run_query(
            query=args.query,
            user_id=args.user_id,
            session_id=args.session_id,
            verbose=args.verbose,
            json_output=args.json
        )
    else:
        # Interactive mode
        await cli.interactive_mode()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
