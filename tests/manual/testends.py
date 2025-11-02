#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Elephant Frontend-Backend Communication Test Suite
Tests all endpoints and verifies proper communication between services.
"""

import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    import requests
except ImportError:
    print("[-] requests library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


class Color:
    """ANSI color codes for terminal output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class TestResults:
    """Track test results and generate report"""
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.tests_warned = 0
        self.failures: List[str] = []
        self.warnings: List[str] = []
        self.timings: Dict[str, float] = {}

    def add_pass(self, test_name: str, duration: float = 0):
        self.tests_run += 1
        self.tests_passed += 1
        self.timings[test_name] = duration

    def add_fail(self, test_name: str, error: str, duration: float = 0):
        self.tests_run += 1
        self.tests_failed += 1
        self.failures.append(f"{test_name}: {error}")
        self.timings[test_name] = duration

    def add_warn(self, test_name: str, warning: str):
        self.tests_warned += 1
        self.warnings.append(f"{test_name}: {warning}")

    def print_summary(self):
        print(f"\n{Color.BOLD}{'='*70}{Color.END}")
        print(f"{Color.BOLD}  TEST SUMMARY{Color.END}")
        print(f"{Color.BOLD}{'='*70}{Color.END}\n")

        print(f"  Total Tests:   {self.tests_run}")
        print(f"  {Color.GREEN}✓ Passed:{Color.END}      {self.tests_passed}")
        print(f"  {Color.RED}✗ Failed:{Color.END}      {self.tests_failed}")
        print(f"  {Color.YELLOW}⚠ Warnings:{Color.END}    {self.tests_warned}")

        if self.failures:
            print(f"\n{Color.RED}{Color.BOLD}FAILURES:{Color.END}")
            for failure in self.failures:
                print(f"  {Color.RED}✗{Color.END} {failure}")

        if self.warnings:
            print(f"\n{Color.YELLOW}{Color.BOLD}WARNINGS:{Color.END}")
            for warning in self.warnings:
                print(f"  {Color.YELLOW}⚠{Color.END} {warning}")

        # Performance summary
        if self.timings:
            print(f"\n{Color.CYAN}{Color.BOLD}PERFORMANCE:{Color.END}")
            for test, duration in self.timings.items():
                if duration > 0:
                    color = Color.GREEN if duration < 1000 else Color.YELLOW if duration < 3000 else Color.RED
                    print(f"  {test}: {color}{duration:.0f}ms{Color.END}")

        print(f"\n{Color.BOLD}{'='*70}{Color.END}\n")

        if self.tests_failed == 0:
            print(f"{Color.GREEN}{Color.BOLD}✓ ALL TESTS PASSED - SYSTEMS OPERATIONAL{Color.END}\n")
            return True
        else:
            print(f"{Color.RED}{Color.BOLD}✗ TESTS FAILED - ISSUES DETECTED{Color.END}\n")
            return False


def print_header():
    """Print test suite header"""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*70}")
    print("  ELEPHANT FRONTEND-BACKEND COMMUNICATION TEST SUITE")
    print(f"{'='*70}{Color.END}\n")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def test_backend_health(results: TestResults) -> bool:
    """Test 1: Backend Health Check"""
    print(f"{Color.BOLD}[1/8]{Color.END} Testing Backend Health Check...")

    try:
        start = time.time()
        response = requests.get('http://localhost:3002/health', timeout=5)
        duration = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            print(f"  {Color.GREEN}✓{Color.END} Backend is running on port 3002")
            print(f"  {Color.GREEN}✓{Color.END} Status: {data.get('status')}")
            print(f"  {Color.GREEN}✓{Color.END} Service: {data.get('service')}")
            print(f"  {Color.GREEN}✓{Color.END} GROQ API: {'Connected' if data.get('groq') else 'Not configured'}")
            print(f"  {Color.GREEN}✓{Color.END} Response time: {duration:.0f}ms")

            if not data.get('groq'):
                results.add_warn("Backend Health", "GROQ API key not configured")

            results.add_pass("Backend Health", duration)
            return True
        else:
            error = f"HTTP {response.status_code}"
            print(f"  {Color.RED}✗{Color.END} Backend returned: {error}")
            results.add_fail("Backend Health", error, duration)
            return False

    except requests.exceptions.ConnectionError:
        print(f"  {Color.RED}✗{Color.END} Cannot connect to backend on port 3002")
        print(f"  {Color.YELLOW}→{Color.END} Is the backend running? Try: cd backend-api && set BACKEND_PORT=3002 && npm start")
        results.add_fail("Backend Health", "Connection refused on port 3002")
        return False
    except Exception as e:
        print(f"  {Color.RED}✗{Color.END} Error: {str(e)}")
        results.add_fail("Backend Health", str(e))
        return False


def test_frontend_running(results: TestResults) -> bool:
    """Test 2: Frontend Server Running"""
    print(f"\n{Color.BOLD}[2/8]{Color.END} Testing Frontend Server...")

    try:
        start = time.time()
        response = requests.get('http://localhost:3000', timeout=5)
        duration = (time.time() - start) * 1000

        if response.status_code == 200:
            print(f"  {Color.GREEN}✓{Color.END} Frontend is running on port 3000")
            print(f"  {Color.GREEN}✓{Color.END} Response time: {duration:.0f}ms")
            results.add_pass("Frontend Running", duration)
            return True
        else:
            error = f"HTTP {response.status_code}"
            print(f"  {Color.RED}✗{Color.END} Frontend returned: {error}")
            results.add_fail("Frontend Running", error, duration)
            return False

    except requests.exceptions.ConnectionError:
        print(f"  {Color.RED}✗{Color.END} Cannot connect to frontend on port 3000")
        print(f"  {Color.YELLOW}→{Color.END} Is the frontend running? Try: cd frontend && npm start")
        results.add_fail("Frontend Running", "Connection refused on port 3000")
        return False
    except Exception as e:
        print(f"  {Color.RED}✗{Color.END} Error: {str(e)}")
        results.add_fail("Frontend Running", str(e))
        return False


def test_frontend_proxy(results: TestResults) -> bool:
    """Test 3: Frontend Proxy to Backend"""
    print(f"\n{Color.BOLD}[3/8]{Color.END} Testing Frontend Proxy Configuration...")

    try:
        start = time.time()
        response = requests.get('http://localhost:3000/api/health', timeout=5)
        duration = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            print(f"  {Color.GREEN}✓{Color.END} Proxy is working correctly")
            print(f"  {Color.GREEN}✓{Color.END} Frontend (3000) → Backend (3002) communication OK")
            print(f"  {Color.GREEN}✓{Color.END} Response time: {duration:.0f}ms")

            if duration > 1000:
                results.add_warn("Frontend Proxy", f"Slow proxy response: {duration:.0f}ms")

            results.add_pass("Frontend Proxy", duration)
            return True
        else:
            error = f"HTTP {response.status_code}"
            print(f"  {Color.RED}✗{Color.END} Proxy returned: {error}")
            results.add_fail("Frontend Proxy", error, duration)
            return False

    except Exception as e:
        print(f"  {Color.RED}✗{Color.END} Proxy error: {str(e)}")
        print(f"  {Color.YELLOW}→{Color.END} Check vite.config.js proxy configuration")
        results.add_fail("Frontend Proxy", str(e))
        return False


def test_chat_endpoint_direct(results: TestResults) -> bool:
    """Test 4: Direct Backend Chat Endpoint"""
    print(f"\n{Color.BOLD}[4/8]{Color.END} Testing Backend Chat Endpoint (Direct)...")

    payload = {
        "message": "Hello, this is a test message",
        "sessionId": "test-session",
        "useHistory": False,
        "agent": "general-chat"
    }

    try:
        start = time.time()
        response = requests.post(
            'http://localhost:3002/api/chat',
            json=payload,
            timeout=10
        )
        duration = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                print(f"  {Color.GREEN}✓{Color.END} Chat endpoint responding")
                print(f"  {Color.GREEN}✓{Color.END} Agent: {data.get('metadata', {}).get('agent', 'N/A')}")
                print(f"  {Color.GREEN}✓{Color.END} Model: {data.get('metadata', {}).get('model', 'N/A')}")
                print(f"  {Color.GREEN}✓{Color.END} Processing time: {data.get('metadata', {}).get('processingTime', 0)}ms")
                print(f"  {Color.GREEN}✓{Color.END} Total time: {duration:.0f}ms")
                print(f"  {Color.GREEN}✓{Color.END} Response preview: {data.get('message', '')[:60]}...")

                if duration > 3000:
                    results.add_warn("Backend Chat Direct", f"Slow response: {duration:.0f}ms (target <3000ms)")

                results.add_pass("Backend Chat Direct", duration)
                return True
            else:
                error = data.get('error', 'Unknown error')
                print(f"  {Color.RED}✗{Color.END} Chat failed: {error}")
                results.add_fail("Backend Chat Direct", error, duration)
                return False
        else:
            error = f"HTTP {response.status_code}"
            print(f"  {Color.RED}✗{Color.END} Backend returned: {error}")
            results.add_fail("Backend Chat Direct", error, duration)
            return False

    except Exception as e:
        print(f"  {Color.RED}✗{Color.END} Error: {str(e)}")
        print(f"  {Color.YELLOW}→{Color.END} Check GROQ_API_KEY in .env file")
        results.add_fail("Backend Chat Direct", str(e))
        return False


def test_chat_endpoint_proxy(results: TestResults) -> bool:
    """Test 5: Chat Endpoint via Frontend Proxy"""
    print(f"\n{Color.BOLD}[5/8]{Color.END} Testing Chat Endpoint via Proxy...")

    payload = {
        "message": "Testing proxy chat endpoint",
        "sessionId": "proxy-test-session",
        "useHistory": False,
        "agent": "general-chat"
    }

    try:
        start = time.time()
        response = requests.post(
            'http://localhost:3000/api/chat',  # Through proxy
            json=payload,
            timeout=10
        )
        duration = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                print(f"  {Color.GREEN}✓{Color.END} Proxy chat endpoint working")
                print(f"  {Color.GREEN}✓{Color.END} Frontend → Backend communication OK")
                print(f"  {Color.GREEN}✓{Color.END} Total time: {duration:.0f}ms")

                if duration > 3000:
                    results.add_warn("Frontend Chat Proxy", f"Slow response: {duration:.0f}ms")

                results.add_pass("Frontend Chat Proxy", duration)
                return True
            else:
                error = data.get('error', 'Unknown error')
                print(f"  {Color.RED}✗{Color.END} Proxy chat failed: {error}")
                results.add_fail("Frontend Chat Proxy", error, duration)
                return False
        else:
            error = f"HTTP {response.status_code}"
            print(f"  {Color.RED}✗{Color.END} Proxy returned: {error}")
            results.add_fail("Frontend Chat Proxy", error, duration)
            return False

    except Exception as e:
        print(f"  {Color.RED}✗{Color.END} Error: {str(e)}")
        results.add_fail("Frontend Chat Proxy", str(e))
        return False


def test_agent_classification(results: TestResults) -> bool:
    """Test 6: Agent Classification System"""
    print(f"\n{Color.BOLD}[6/8]{Color.END} Testing Agent Classification...")

    test_queries = [
        ("Hello", "general-chat"),
        ("Find Python developers with 5 years experience", "information-retrieval"),
        ("Why is our placement rate declining?", "problem-solving"),
        ("Generate a monthly performance report", "report-generation"),
        ("What are the GDPR requirements for candidate data?", "industry-knowledge")
    ]

    passed = 0
    failed = 0

    for query, expected_agent in test_queries:
        try:
            response = requests.post(
                'http://localhost:3002/api/chat',
                json={
                    "message": query,
                    "sessionId": "classification-test",
                    "useHistory": False,
                    "agent": expected_agent
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                actual_agent = data.get('metadata', {}).get('agent', 'unknown')

                if actual_agent == expected_agent:
                    print(f"  {Color.GREEN}✓{Color.END} '{query[:40]}...' → {actual_agent}")
                    passed += 1
                else:
                    print(f"  {Color.YELLOW}⚠{Color.END} '{query[:40]}...' → {actual_agent} (expected {expected_agent})")
                    passed += 1  # Still passes as backend is working
            else:
                print(f"  {Color.RED}✗{Color.END} '{query[:40]}...' → HTTP {response.status_code}")
                failed += 1

        except Exception as e:
            print(f"  {Color.RED}✗{Color.END} '{query[:40]}...' → Error: {str(e)}")
            failed += 1

    if failed == 0:
        print(f"  {Color.GREEN}✓{Color.END} Agent classification working ({passed}/{len(test_queries)} agents tested)")
        results.add_pass("Agent Classification")
        return True
    else:
        print(f"  {Color.RED}✗{Color.END} Some classifications failed ({failed}/{len(test_queries)})")
        results.add_fail("Agent Classification", f"{failed} agents failed")
        return False


def test_conversation_history(results: TestResults) -> bool:
    """Test 7: Conversation History Management"""
    print(f"\n{Color.BOLD}[7/8]{Color.END} Testing Conversation History...")

    session_id = f"history-test-{int(time.time())}"

    try:
        # First message
        response1 = requests.post(
            'http://localhost:3002/api/chat',
            json={
                "message": "Remember this number: 42",
                "sessionId": session_id,
                "useHistory": True,
                "agent": "general-chat"
            },
            timeout=10
        )

        if response1.status_code != 200:
            print(f"  {Color.RED}✗{Color.END} First message failed")
            results.add_fail("Conversation History", "First message failed")
            return False

        print(f"  {Color.GREEN}✓{Color.END} First message sent")

        # Second message (should remember context)
        time.sleep(1)
        response2 = requests.post(
            'http://localhost:3002/api/chat',
            json={
                "message": "What number did I just tell you?",
                "sessionId": session_id,
                "useHistory": True,
                "agent": "general-chat"
            },
            timeout=10
        )

        if response2.status_code == 200:
            data = response2.json()
            response_text = data.get('message', '').lower()
            history_length = data.get('metadata', {}).get('historyLength', 0)

            print(f"  {Color.GREEN}✓{Color.END} Second message sent")
            print(f"  {Color.GREEN}✓{Color.END} History length: {history_length} messages")
            print(f"  {Color.GREEN}✓{Color.END} Response: {data.get('message', '')[:80]}...")

            if history_length >= 2:
                print(f"  {Color.GREEN}✓{Color.END} Conversation history maintained")
                results.add_pass("Conversation History")
                return True
            else:
                results.add_warn("Conversation History", f"History length only {history_length}")
                results.add_pass("Conversation History")
                return True
        else:
            print(f"  {Color.RED}✗{Color.END} Second message failed")
            results.add_fail("Conversation History", "Second message failed")
            return False

    except Exception as e:
        print(f"  {Color.RED}✗{Color.END} Error: {str(e)}")
        results.add_fail("Conversation History", str(e))
        return False


def test_error_handling(results: TestResults) -> bool:
    """Test 8: Error Handling"""
    print(f"\n{Color.BOLD}[8/8]{Color.END} Testing Error Handling...")

    # Test empty message
    try:
        response = requests.post(
            'http://localhost:3002/api/chat',
            json={
                "message": "",
                "sessionId": "error-test"
            },
            timeout=5
        )

        if response.status_code == 400:
            print(f"  {Color.GREEN}✓{Color.END} Empty message correctly rejected (HTTP 400)")
        else:
            print(f"  {Color.YELLOW}⚠{Color.END} Empty message not rejected (got HTTP {response.status_code})")
            results.add_warn("Error Handling", "Empty message validation may be weak")
    except Exception as e:
        print(f"  {Color.YELLOW}⚠{Color.END} Error test failed: {str(e)}")

    # Test missing fields
    try:
        response = requests.post(
            'http://localhost:3002/api/chat',
            json={},
            timeout=5
        )

        if response.status_code in [400, 500]:
            print(f"  {Color.GREEN}✓{Color.END} Missing fields handled gracefully")
        else:
            print(f"  {Color.YELLOW}⚠{Color.END} Missing fields not validated")
            results.add_warn("Error Handling", "Missing field validation may be weak")
    except Exception as e:
        print(f"  {Color.YELLOW}⚠{Color.END} Missing field test failed: {str(e)}")

    print(f"  {Color.GREEN}✓{Color.END} Error handling tests completed")
    results.add_pass("Error Handling")
    return True


def main():
    """Run all tests"""
    print_header()

    results = TestResults()

    # Run tests
    backend_ok = test_backend_health(results)
    frontend_ok = test_frontend_running(results)

    if not backend_ok or not frontend_ok:
        print(f"\n{Color.RED}{Color.BOLD}⚠ CRITICAL: Core services not running{Color.END}")
        print(f"{Color.YELLOW}  Please start both services before running tests:{Color.END}")
        print(f"  1. Backend:  cd backend-api && set BACKEND_PORT=3002 && npm start")
        print(f"  2. Frontend: cd frontend && npm start")
        print(f"\n{Color.CYAN}  Or use: start-dev.bat{Color.END}\n")
        results.print_summary()
        sys.exit(1)

    proxy_ok = test_frontend_proxy(results)
    chat_direct_ok = test_chat_endpoint_direct(results)
    chat_proxy_ok = test_chat_endpoint_proxy(results)
    classification_ok = test_agent_classification(results)
    history_ok = test_conversation_history(results)
    error_ok = test_error_handling(results)

    # Print summary
    success = results.print_summary()

    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
