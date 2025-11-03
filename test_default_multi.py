"""
Test Default Multiple CV Matching
"""
import asyncio
import sys
import os

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(__file__))

from utils.ai_router.router import AIRouter
from utils.ai_router.groq_classifier import GroqClassifier
from utils.ai_router.agent_registry import AgentRegistry


async def test_default():
    """Test that multiple CV matching is now the default"""
    print("\n" + "="*70)
    print("TEST: DEFAULT BEHAVIOR (Should be Multiple CV Matching)")
    print("="*70 + "\n")

    # Create router (no config changes needed)
    classifier = GroqClassifier()
    agent_registry = AgentRegistry()
    
    router = AIRouter(
        classifier=classifier,
        session_store=None,
        log_repository=None,
        agent_registry=agent_registry
    )

    # Test with default query
    result = await router.route("Find best matching CVs", "test_user", "test_session")
    
    print("\n" + "="*70)
    print("VERIFICATION:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Latency: {result['latency_ms']}ms")
    
    if result['agent_response']:
        metadata = result['agent_response'].metadata
        print(f"\n✓ Scenario: {metadata.get('scenario')}")
        print(f"✓ Find Multiple: {metadata.get('find_multiple')}")
        print(f"✓ Candidates Count: {metadata.get('candidates_count')}")
        print(f"✓ Candidates: {metadata.get('candidates')}")
        
        # Check if multiple mode is active
        if metadata.get('find_multiple') and metadata.get('candidates_count') == 4:
            print("\n🎉 SUCCESS: Multiple CV matching is now the DEFAULT!")
            return True
        else:
            print("\n❌ FAILED: Not using multiple CV matching mode")
            return False
    
    return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_default())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
