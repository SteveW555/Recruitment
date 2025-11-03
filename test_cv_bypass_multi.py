"""
Test CV Matching Bypass - Single and Multiple Modes
"""
import asyncio
import sys
import os
import json

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.ai_router.router import AIRouter
from utils.ai_router.groq_classifier import GroqClassifier
from utils.ai_router.agent_registry import AgentRegistry


async def test_single_mode():
    """Test single CV matching"""
    print("\n" + "="*70)
    print("TEST 1: SINGLE CV MATCHING MODE")
    print("="*70 + "\n")

    # Update config to use single mode
    with open('config/cv_matching_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    config['cv_matching']['default_scenario'] = 'elena_customer_support'
    
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
    result = await router.route("Find best matching CVs", "test_user", "test_session_1")
    
    print("\n" + "="*70)
    print("SINGLE MODE RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Latency: {result['latency_ms']}ms")
    
    if result['agent_response']:
        print(f"\nMetadata:")
        for key, value in result['agent_response'].metadata.items():
            print(f"  {key}: {value}")
        
        print(f"\nResponse Preview (first 500 chars):")
        print(result['agent_response'].content[:500])
    
    return result['success']


async def test_multiple_mode():
    """Test multiple CV matching"""
    print("\n\n" + "="*70)
    print("TEST 2: MULTIPLE CV MATCHING MODE")
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
    result = await router.route("Find best matching CVs", "test_user", "test_session_2")
    
    print("\n" + "="*70)
    print("MULTIPLE MODE RESULT:")
    print("="*70)
    print(f"Success: {result['success']}")
    print(f"Latency: {result['latency_ms']}ms")
    
    if result['agent_response']:
        print(f"\nMetadata:")
        for key, value in result['agent_response'].metadata.items():
            print(f"  {key}: {value}")
        
        print(f"\nFull Response:")
        print(result['agent_response'].content)
    
    return result['success']


async def main():
    """Run all tests"""
    try:
        # Test single mode
        single_success = await test_single_mode()
        
        # Test multiple mode
        multiple_success = await test_multiple_mode()
        
        # Summary
        print("\n\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Single CV Mode:   {'✅ PASSED' if single_success else '❌ FAILED'}")
        print(f"Multiple CV Mode: {'✅ PASSED' if multiple_success else '❌ FAILED'}")
        print("="*70 + "\n")
        
        # Restore default config
        with open('config/cv_matching_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        config['cv_matching']['default_scenario'] = 'elena_customer_support'
        with open('config/cv_matching_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        return single_success and multiple_success
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
