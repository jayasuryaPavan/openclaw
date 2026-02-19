#!/usr/bin/env python3
"""Test vision request with a small test image."""
import requests
import json
import base64
from PIL import Image
import io

# Create a small test image (100x100 pixels)
print("Creating small test image...")
img = Image.new('RGB', (100, 100), color='red')
buffer = io.BytesIO()
img.save(buffer, format='PNG')
base64_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

print(f"Image size: {len(base64_image)} characters")

# Gateway config
GATEWAY_URL = "http://localhost:18789/v1"
TOKEN = "25415d2e7014ed8afc5d00a7b464934477ef73512dffb2bb"

print(f"\nTesting vision request to: {GATEWAY_URL}")

try:
    response = requests.post(
        f"{GATEWAY_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "model": "google-antigravity/gemini-3-pro-high",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What color is this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 50
        },
        timeout=60
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Error (status {response.status_code})")
        error_text = response.text
        print(f"Error length: {len(error_text)} chars")
        
        # Save to file for inspection
        with open("vision_error.txt", "w", encoding="utf-8") as f:
            f.write(error_text)
        print("Full error saved to: vision_error.txt")
        
        # Try to parse as JSON
        try:
            error_json = response.json()
            print(f"Error JSON: {json.dumps(error_json, indent=2)}")
        except:
            print("Could not parse as JSON")
        
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except requests.exceptions.Timeout as e:
    print(f"❌ Timeout: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
