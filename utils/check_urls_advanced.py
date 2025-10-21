"""
Advanced URL Validator with better bot detection avoidance
Uses requests library with full browser headers
"""

import re
from urllib.parse import urlparse

def extract_urls_from_file(filepath):
    """Extract all URLs from markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    urls = re.findall(r'\[https?://[^\]]+\]', content)
    urls = [url.strip('[]') for url in urls]

    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    return unique_urls

def check_url_with_requests(url, timeout=10):
    """
    Check URL using requests library with full browser simulation
    Requires: pip install requests
    """
    try:
        import requests

        # Full browser headers to avoid bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        # Make request with SSL verification disabled and allow redirects
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            verify=False,  # Skip SSL verification
            allow_redirects=True
        )

        return (response.status_code, f"OK (Status {response.status_code})")

    except requests.exceptions.SSLError as e:
        return (0, f"SSL Error: {str(e)[:50]}")
    except requests.exceptions.ConnectionError as e:
        return (0, f"Connection Error: {str(e)[:50]}")
    except requests.exceptions.Timeout:
        return (0, "Timeout")
    except requests.exceptions.RequestException as e:
        return (0, f"Error: {str(e)[:50]}")
    except ImportError:
        return (0, "Error: requests library not installed")

def main():
    # First, check if requests is installed
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except ImportError:
        print("ERROR: This script requires the 'requests' library.")
        print("Install it with: pip install requests")
        return

    filepath = r'd:\Recruitment\sources.md'

    print("Extracting URLs from sources.md...")
    urls = extract_urls_from_file(filepath)

    # Test just the first 3 "failed" URLs from your question
    test_urls = [
        'https://www.staffingindustry.com',
        'https://www.startuploans.co.uk',
        'https://uk.businessesforsale.com'
    ]

    print("\n" + "="*100)
    print("TESTING PREVIOUSLY FAILED URLs WITH ADVANCED HEADERS")
    print("="*100)

    for url in test_urls:
        print(f"\nChecking: {url}")
        status_code, status_msg = check_url_with_requests(url)
        print(f"Result: {status_msg}")

        if status_code == 200:
            print("  [OK] Successfully accessed!")
        elif 200 < status_code < 400:
            print(f"  [OK] Successful redirect (Status {status_code})")
        else:
            print(f"  [FAIL] Still blocked or unreachable")

    print("\n" + "="*100)
    print("\nExplanation:")
    print("- If these now show 200/OK: The sites block simple scripts but allow browser-like requests")
    print("- If still 403: They use JavaScript challenges or more advanced bot detection")
    print("- If still fail: There may be a genuine issue with the site")
    print("="*100)

if __name__ == "__main__":
    main()
