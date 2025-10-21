"""
Test GROQ Setup and Context Query Tool

Quick verification script to ensure everything is configured correctly.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass


def test_environment():
    """Test environment setup"""
    print("\n" + "="*70)
    print("🔍 Testing GROQ Setup")
    print("="*70 + "\n")

    # Test 1: Check .env file
    print("1️⃣  Checking .env file...")
    if os.path.exists(".env"):
        print("   ✓ .env file found")
        from dotenv import load_dotenv
        load_dotenv()

        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            print(f"   ✓ GROQ_API_KEY found ({groq_key[:20]}...)")
        else:
            print("   ❌ GROQ_API_KEY not found in .env")
            return False
    else:
        print("   ❌ .env file not found")
        return False

    # Test 2: Check groq_client module
    print("\n2️⃣  Checking groq_client.py module...")
    if os.path.exists("groq_client.py"):
        print("   ✓ groq_client.py found")
        try:
            from groq_client import GroqClient
            print("   ✓ GroqClient imported successfully")
        except ImportError as e:
            print(f"   ❌ Import error: {e}")
            return False
    else:
        print("   ❌ groq_client.py not found")
        return False

    # Test 3: Check dependencies
    print("\n3️⃣  Checking Python dependencies...")
    try:
        import groq as groq_pkg
        print("   ✓ groq package installed")
    except ImportError:
        print("   ❌ groq package not installed")
        print("      Run: pip install groq")
        return False

    try:
        from dotenv import load_dotenv
        print("   ✓ python-dotenv installed")
    except ImportError:
        print("   ❌ python-dotenv not installed")
        print("      Run: pip install python-dotenv")
        return False

    # Test 4: Check CSV file
    print("\n4️⃣  Checking client database CSV...")
    csv_path = "Fake Data/fake_client_database_50.csv"
    if os.path.exists(csv_path):
        print(f"   ✓ CSV file found: {csv_path}")

        # Check file size
        size = os.path.getsize(csv_path)
        print(f"   ✓ File size: {size:,} bytes")

        # Count lines
        with open(csv_path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        print(f"   ✓ Lines in file: {lines}")
    else:
        print(f"   ❌ CSV file not found: {csv_path}")
        return False

    # Test 5: Check context query module
    print("\n5️⃣  Checking groq_with_context.py module...")
    if os.path.exists("groq_with_context.py"):
        print("   ✓ groq_with_context.py found")
        try:
            from groq_with_context import GroqContextQuery
            print("   ✓ GroqContextQuery imported successfully")
        except ImportError as e:
            print(f"   ❌ Import error: {e}")
            return False
    else:
        print("   ❌ groq_with_context.py not found")
        return False

    return True


def test_simple_query():
    """Test a simple GROQ query"""
    print("\n" + "="*70)
    print("🧪 Testing Simple GROQ Query")
    print("="*70 + "\n")

    try:
        from groq_client import GroqClient, CompletionConfig

        client = GroqClient()
        print("✓ GroqClient initialized\n")

        print("Sending test query to GROQ...")
        response = client.complete(
            "Say 'GROQ is working!' in exactly 3 words.",
            config=CompletionConfig(max_tokens=50, temperature=0.0)
        )

        print(f"\n✓ Response received: {response.content}")
        print(f"✓ Model: {response.model}")
        print(f"✓ Tokens used: {response.usage['total_tokens']}")

        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def test_context_query():
    """Test context query with CSV"""
    print("\n" + "="*70)
    print("🧪 Testing Context Query with CSV")
    print("="*70 + "\n")

    try:
        from groq_with_context import GroqContextQuery

        csv_path = "Fake Data/fake_client_database_50.csv"
        print(f"Initializing with CSV: {csv_path}")

        query_tool = GroqContextQuery(csv_path)
        print("✓ GroqContextQuery initialized\n")

        print("Running test query: 'How many clients are in the database?'\n")

        response = query_tool.query(
            "How many total clients are in this database? Just give me the number.",
            max_records=5,  # Small sample for quick test
            temperature=0.0
        )

        print("\n✓ Context query completed successfully!")

        return True

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("🚀 GROQ Setup Verification for ProActive People")
    print("="*70)

    # Test 1: Environment
    env_ok = test_environment()

    if not env_ok:
        print("\n" + "="*70)
        print("❌ SETUP INCOMPLETE")
        print("="*70)
        print("\nPlease fix the issues above before proceeding.\n")
        sys.exit(1)

    # Test 2: Simple query
    simple_ok = test_simple_query()

    if not simple_ok:
        print("\n" + "="*70)
        print("❌ GROQ CONNECTION FAILED")
        print("="*70)
        print("\nPlease check your API key and internet connection.\n")
        sys.exit(1)

    # Test 3: Context query
    context_ok = test_context_query()

    if not context_ok:
        print("\n" + "="*70)
        print("❌ CONTEXT QUERY FAILED")
        print("="*70)
        print("\nThere may be an issue with CSV loading or context formatting.\n")
        sys.exit(1)

    # All tests passed
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\n🎉 Your GROQ setup is complete and working!\n")
    print("Next steps:")
    print("  1. Try interactive mode: python groq_with_context.py")
    print("  2. Run examples: python example_groq_queries.py")
    print("  3. Read the guide: GROQ_CONTEXT_README.md\n")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}\n")
        import traceback
        traceback.print_exc()
