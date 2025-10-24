#!/usr/bin/env python3
"""
Minimal Groq API Test - sends "Hi" to test connectivity
"""

import os
import argparse
from dotenv import load_dotenv

load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test Groq API')
parser.add_argument('--msg', type=str, default='Hi', help='Message to send (default: Hi)')
args = parser.parse_args()

message = args.msg

# Check API key
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("Error: GROQ_API_KEY not found")
    exit(1)

print("API Key found")

# Import and test
try:
    from groq import Groq

    client = Groq(api_key=api_key)

    print(f"Sending: {message}")

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": message}],
        temperature=0.7,
        max_tokens=100
    )

    response = completion.choices[0].message.content

    print("\nResponse:")
    print(response)
    print("\nTokens used:", completion.usage.total_tokens)

except Exception as e:
    print(f"Error: {e}")
    exit(1)
