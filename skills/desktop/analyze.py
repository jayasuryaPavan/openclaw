#!/usr/bin/env python3
"""
Vision analysis for desktop screenshots.
Takes a screenshot and analyzes it using the Antigravity vision model.
"""
import sys
import os
import json
import base64
import time
import requests
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent.absolute()
OPENCLAW_ROOT = SCRIPT_DIR.parent.parent
SCREENSHOTS_DIR = OPENCLAW_ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Gateway config (routes to panda agent's Antigravity auth via x-openclaw-agent-id header)
GATEWAY_URL = "http://localhost:18789/v1"
MODELS = [
    "google-antigravity/gemini-3-pro-low",
    "google-antigravity/gemini-3-flash",
]

def get_gateway_config():
    """Read gateway URL and token from openclaw.json."""
    config_path = OPENCLAW_ROOT / "openclaw.json"
    try:
        with open(config_path) as f:
            config = json.load(f)
        token = config.get("gateway", {}).get("auth", {}).get("token", "")
        return GATEWAY_URL, token
    except Exception:
        return GATEWAY_URL, ""

def take_screenshot(name="analyze_view"):
    """Capture the screen and save as compressed JPEG."""
    import pyautogui
    from PIL import Image
    
    time.sleep(0.3)
    screenshot = pyautogui.screenshot()
    
    path = SCREENSHOTS_DIR / f"{name}.jpg"
    
    # Resize to max 900px wide for smaller payload
    w, h = screenshot.size
    if w > 900:
        ratio = 900 / w
        screenshot = screenshot.resize((900, int(h * ratio)), Image.Resampling.LANCZOS)
    
    screenshot.save(path, "JPEG", quality=55, optimize=True)
    return path

def call_vision_api(endpoint, token, model, b64_image, question, agent_id=None):
    """Make a single vision API call."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    if agent_id:
        headers["x-openclaw-agent-id"] = agent_id
    
    response = requests.post(
        f"{endpoint}/chat/completions",
        headers=headers,
        json={
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}
                    }
                ]
            }],
            "max_tokens": 1000
        },
        timeout=90
    )
    return response

def analyze_image(image_path, question):
    """Send image to vision model via gateway with panda agent routing."""
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    
    gw_url, gw_token = get_gateway_config()
    
    for model in MODELS:
        try:
            # Pass x-openclaw-agent-id: panda so gateway uses panda's Antigravity auth
            r = call_vision_api(gw_url, gw_token, model, b64, question, agent_id="panda")
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            print(f"Gateway {model} failed ({r.status_code}): {r.text[:150]}", file=sys.stderr)
        except requests.exceptions.Timeout:
            print(f"Gateway {model} timed out", file=sys.stderr)
        except Exception as e:
            print(f"Gateway {model} error: {e}", file=sys.stderr)
    
    print("All vision models failed.", file=sys.stderr)
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py \"What do you see on screen?\"")
        print("       python analyze.py \"What do you see?\" --screenshot screenshots/existing.jpg")
        sys.exit(1)
    
    question = sys.argv[1]
    
    # Check if a specific screenshot path was provided
    screenshot_path = None
    if "--screenshot" in sys.argv:
        idx = sys.argv.index("--screenshot")
        if idx + 1 < len(sys.argv):
            screenshot_path = Path(sys.argv[idx + 1])
    
    if screenshot_path is None:
        screenshot_path = take_screenshot()
        rel = os.path.relpath(screenshot_path, OPENCLAW_ROOT).replace("\\", "/")
        print(f"MEDIA:./{rel}")
    
    # Analyze with vision model
    answer = analyze_image(screenshot_path, question)
    print(answer)

if __name__ == "__main__":
    main()
