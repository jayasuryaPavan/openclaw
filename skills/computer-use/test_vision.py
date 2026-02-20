import os
import requests
import json
import base64
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
OPENCLAW_ROOT = SCRIPT_DIR.parent.parent
SCREENSHOTS_DIR = OPENCLAW_ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Gateway Configuration
def get_gateway_config():
    """Read gateway configuration."""
    url = "http://localhost:18789/v1"
    
    # 1. Try environment variable first
    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN")
    if token:
        return url, token.strip().strip('"').strip("'")

    # 2. Try reading .env file directly if env var is missing
    env_path = OPENCLAW_ROOT / ".env"
    if env_path.exists():
        try:
            with open(env_path) as f:
                for line in f:
                    if line.startswith("OPENCLAW_GATEWAY_TOKEN="):
                        token = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if token:
                            return url, token
        except Exception:
            pass

    # 3. Fallback to openclaw.json
    config_path = OPENCLAW_ROOT / "openclaw.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)
                token = config.get("gateway", {}).get("auth", {}).get("token", "")
                if token:
                    return url, token
        except Exception:
            pass

    return url, ""

GATEWAY_URL, GATEWAY_TOKEN = get_gateway_config()
MODEL_ID = "google/gemini-1.5-flash"

print(f"Testing vision model: {MODEL_ID}")
print(f"Using gateway: {GATEWAY_URL}")

try:
    response = requests.post(
        f"{GATEWAY_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {GATEWAY_TOKEN}",
            "Content-Type": "application/json"
        },
        json={
            "model": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": "Is this working? Just say YES."
                }
            ],
            "max_tokens": 10
        },
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")

except Exception as e:
    print(f"Error: {e}")
