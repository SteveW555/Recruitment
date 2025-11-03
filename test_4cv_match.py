"""
Test 4-CV Multiple Matching
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
import json


async def test_4cv_matching():
    """Test multiple CV matching with 4 candidates"""
    print("\n" + "="*70)
    print("TEST: 4-CV MULTIPLE MATCHING (2 Bad + 2 Good)")
    print("="*70 + "\n")

    # Update config to use multiple mode
    with open('config/cv_matching_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['cv_matching']['default_scenario'] = 'multiple_customer_support'
    
    with open('config/cv_matching_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    # Create router
    classifier = GroqClassifier()
    agent_registry = AgentRegistry()
    
    router = AIRouter(
        classifier=classifier,
        session_store=None,
        log_repository=None,
        agent_registry=agent_registry,
        confidence_threshold=0.65
    )

    # Test
    result = await router.route("Find best matching CVs", "test_user", "test_session")
    
    print("\n" + "="*70)
    print("RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Latency: {result['latency_ms']}ms")
    
    if result['agent_response']:
        metadata = result['agent_response'].metadata
        print(f"\nMetadata:")
        print(f"  Scenario: {metadata.get('scenario')}")
        print(f"  Job: {metadata.get('job')}")
        print(f"  Find Multiple: {metadata.get('find_multiple')}")
        print(f"  Candidates Count: {metadata.get('candidates_count')}")
        print(f"  Candidates: {metadata.get('candidates')}")
        
        print(f"\n" + "="*70)
        print("FULL RANKING:")
        print("="*70)
        print(result['agent_response'].content)
    
    # Restore default config
    with open('config/cv_matching_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    config['cv_matching']['default_scenario'] = 'elena_customer_support'
    with open('config/cv_matching_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
    
    return result['success']


if __name__ == "__main__":
    try:
        success = asyncio.run(test_4cv_matching())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
