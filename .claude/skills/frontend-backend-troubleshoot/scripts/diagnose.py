#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick diagnostic script for frontend-backend communication issues.
Provides rapid diagnosis without running full test suite.
"""

import sys
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


def check_port(port, name):
    """Check if a service is running on a port"""
    try:
        response = requests.get(f'http://localhost:{port}', timeout=2)
        print(f"[OK] {name} is running on port {port}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"[!!] {name} is NOT running on port {port}")

        # Additional check using platform-specific tools
        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['powershell', '-Command',
                     f'Test-NetConnection -ComputerName localhost -Port {port} -InformationLevel Quiet'],
                    capture_output=True, text=True, timeout=5
                )
                if 'False' in result.stdout:
                    print(f"     Port {port} is confirmed NOT listening (PowerShell check)")
            except:
                pass
        return False
    except Exception as e:
        print(f"[??] {name} check failed: {e}")
        return False


def check_backend_health(port):
    """Check backend health endpoint"""
    try:
        response = requests.get(f'http://localhost:{port}/health', timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] Backend health check passed")
            print(f"     Service: {data.get('service', 'Unknown')}")
            return True
        else:
            print(f"[!!] Backend health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"[!!] Backend health check error: {e}")
        return False


def check_proxy(frontend_port, backend_port):
    """Check if frontend proxy is working"""
    try:
        # Test direct backend
        direct = requests.get(f'http://localhost:{backend_port}/health', timeout=2)

        # Test through proxy
        proxied = requests.get(f'http://localhost:{frontend_port}/api/health', timeout=2)

        if proxied.status_code == 200:
            print(f"[OK] Proxy is working (frontend → backend)")
            return True
        elif proxied.status_code == 404:
            print(f"[!!] Proxy returns 404 - Check vite.config.js proxy settings")
            return False
        else:
            print(f"[!!] Proxy error: HTTP {proxied.status_code}")
            return False
    except Exception as e:
        print(f"[!!] Proxy check failed: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("  FRONTEND-BACKEND COMMUNICATION DIAGNOSTIC")
    print("="*60 + "\n")

    frontend_port = 3000
    backend_port = 3002

    print("Step 1: Checking if servers are running...")
    print("-" * 60)
    backend_running = check_port(backend_port, "Backend")
    frontend_running = check_port(frontend_port, "Frontend")
    print()

    if not backend_running or not frontend_running:
        print("DIAGNOSIS: Core services not running")
        print("\nRECOMMENDED ACTION:")
        print("  1. Start backend: cd backend-api && set BACKEND_PORT=3002 && npm start")
        print("  2. Start frontend: cd frontend && npm start")
        print("  Or use: start-dev.bat\n")
        return

    print("Step 2: Checking backend health...")
    print("-" * 60)
    backend_healthy = check_backend_health(backend_port)
    print()

    print("Step 3: Checking proxy configuration...")
    print("-" * 60)
    proxy_working = check_proxy(frontend_port, backend_port)
    print()

    print("="*60)
    if backend_running and frontend_running and backend_healthy:
        if proxy_working:
            print("STATUS: All systems operational!")
        else:
            print("STATUS: Servers running, but proxy needs attention")
            print("\nRECOMMENDED ACTION:")
            print("  1. Check frontend/vite.config.js for proxy configuration")
            print("  2. Clear Vite cache: rm -rf frontend/node_modules/.vite")
            print("  3. Restart frontend: cd frontend && npm start")
    else:
        print("STATUS: Issues detected")
        print("\nRECOMMENDED ACTION:")
        print("  Run full test suite: python testends.py")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
