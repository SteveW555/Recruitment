"""
Test CV Matching Bypass
"""
import asyncio
import sys
import os

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.ai_router.router import AIRouter
from utils.ai_router.groq_classifier import GroqClassifier
from utils.ai_router.agent_registry import AgentRegistry


async def test_cv_bypass():
    """Test the CV matching bypass"""
    print("\n" + "="*70)
    print("TESTING CV MATCHING BYPASS")
    print("="*70 + "\n")

    # Create minimal router (no storage/logging needed for test)
    classifier = GroqClassifier()
    agent_registry = AgentRegistry()
    
    router = AIRouter(
        classifier=classifier,
        session_store=None,
        log_repository=None,
        agent_registry=agent_registry,
        confidence_threshold=0.65
    )

    # Test the bypass with exact query
    query = "Find best matching CVs"
    user_id = "test_user"
    session_id = "test_session"

    print(f"Query: '{query}'")
    print(f"User: {user_id}")
    print(f"Session: {session_id}\n")

    try:
        result = await router.route(query, user_id, session_id)
        
        print("\n" + "="*70)
        print("RESULT:")
        print("="*70)
        print(f"Success: {result['success']}")
        print(f"Latency: {result['latency_ms']}ms")
        
        if result['agent_response']:
            print(f"\nAgent Response:")
            print(f"Content:\n{result['agent_response'].content}")
            print(f"\nMetadata: {result['agent_response'].metadata}")
        
        if result['error']:
            print(f"\nError: {result['error']}")
        
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return result['success']


if __name__ == "__main__":
    success = asyncio.run(test_cv_bypass())
    sys.exit(0 if success else 1)
