#!/usr/bin/env python3
"""Test OpenClaw gateway connectivity."""
import requests
import json

# Test configuration
GATEWAY_URL = "http://localhost:18789/v1"
TOKEN = "25415d2e7014ed8afc5d00a7b464934477ef73512dffb2bb"

print(f"Testing gateway at: {GATEWAY_URL}")
print(f"Using token: {TOKEN[:20]}...")

# Test 1: Check if gateway is reachable
try:
    response = requests.get(
        f"{GATEWAY_URL}/models",
        headers={"Authorization": f"Bearer {TOKEN}"},
        timeout=5
    )
    print(f"\n✅ Gateway reachable!")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        models = response.json()
        print(f"Available models: {json.dumps(models, indent=2)}")
except requests.exceptions.ConnectionError as e:
    print(f"\n❌ Connection failed: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")

# Test 2: Try a simple completion
print("\n" + "="*60)
print("Testing chat completion...")
try:
    response = requests.post(
        f"{GATEWAY_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "model": "google-antigravity/gemini-3-flash",
            "messages": [
                {"role": "user", "content": "Say hello"}
            ],
            "max_tokens": 10
        },
        timeout=30
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Chat completion successful!")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Error: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")
