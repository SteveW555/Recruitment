"""
URL Validator for sources.md
Checks each URL and reports status
"""

import re
import urllib.request
import urllib.error
import ssl
from urllib.parse import urlparse

def extract_urls_from_file(filepath):
    """Extract all URLs from markdown file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all markdown links [text](url)
    urls = re.findall(r'\[https?://[^\]]+\]', content)
    # Clean up the URLs
    urls = [url.strip('[]') for url in urls]

    # Get unique URLs while preserving order
    seen = set()
    unique_urls = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    return unique_urls

def check_url(url, timeout=10):
    """
    Check if URL is accessible
    Returns: (status_code, status_message)
    """
    try:
        # Create SSL context that doesn't verify certificates (for testing)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        # Create request with headers to avoid being blocked
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )

        # Try to open the URL
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            return (response.status, "OK")

    except urllib.error.HTTPError as e:
        return (e.code, f"HTTP {e.code}")
    except urllib.error.URLError as e:
        return (0, f"URL Error: {str(e.reason)[:50]}")
    except Exception as e:
        return (0, f"Error: {str(e)[:50]}")

def main():
    filepath = r'd:\Recruitment\sources.md'

    print("Extracting URLs from sources.md...")
    urls = extract_urls_from_file(filepath)

    print(f"\nFound {len(urls)} unique URLs")
    print("\nChecking URLs (this may take a few minutes)...\n")

    results = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Checking {url}...", end=' ')
        status_code, status_msg = check_url(url)
        results.append({
            'url': url,
            'domain': urlparse(url).netloc,
            'status_code': status_code,
            'status': status_msg
        })
        print(status_msg)

    # Print summary table
    print("\n" + "="*100)
    print("VALIDATION RESULTS")
    print("="*100)
    print(f"{'#':<4} {'Domain':<40} {'Status':<12} {'URL':<40}")
    print("-"*100)

    for i, result in enumerate(results, 1):
        print(f"{i:<4} {result['domain']:<40} {result['status']:<12} {result['url']:<40}")

    # Summary statistics
    ok_count = sum(1 for r in results if r['status_code'] == 200)
    error_count = len(results) - ok_count

    print("\n" + "="*100)
    print(f"SUMMARY: {ok_count} OK | {error_count} ERRORS | {len(results)} TOTAL")
    print("="*100)

    # Save results to file
    output_file = r'd:\Recruitment\url_validation_results.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("URL VALIDATION RESULTS\n")
        f.write("="*100 + "\n\n")
        f.write(f"{'#':<4} {'Domain':<40} {'Status':<12} {'URL':<40}\n")
        f.write("-"*100 + "\n")
        for i, result in enumerate(results, 1):
            f.write(f"{i:<4} {result['domain']:<40} {result['status']:<12} {result['url']:<40}\n")
        f.write("\n" + "="*100 + "\n")
        f.write(f"SUMMARY: {ok_count} OK | {error_count} ERRORS | {len(results)} TOTAL\n")
        f.write("="*100 + "\n")

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
