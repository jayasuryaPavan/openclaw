import sys
import os
import time
import json
import base64
import argparse
import requests
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
OPENCLAW_ROOT = SCRIPT_DIR.parent.parent
SCREENSHOTS_DIR = OPENCLAW_ROOT / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Desktop skill paths
DESKTOP_SKILL_DIR = OPENCLAW_ROOT / "skills" / "desktop"
SCREENSHOT_SCRIPT = DESKTOP_SKILL_DIR / "screenshot.py"
MOUSE_SCRIPT = DESKTOP_SKILL_DIR / "mouse.py"
KEYBOARD_SCRIPT = DESKTOP_SKILL_DIR / "keyboard.py"

# Gateway Configuration (read from openclaw.json)
def get_gateway_config():
    """Read gateway configuration."""
    url = "http://localhost:18789/v1"
    
    # 1. Try environment variable first (highest priority)
    token = os.environ.get("OPENCLAW_GATEWAY_TOKEN")
    if token:
        return url, token.strip().strip('"').strip("'")

    # 2. Try reading .env from root (security best practice)
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

    # 3. Fallback to searching openclaw.json in multiple locations
    config_paths = [
        OPENCLAW_ROOT / "openclaw.json",
        Path.home() / ".openclaw" / "openclaw.json",
        Path("C:/Users/jayas/.openclaw/openclaw.json")
    ]
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    token = config.get("gateway", {}).get("auth", {}).get("token")
                    if token:
                        print(f"Found token in config at {config_path}")
                        return url, token
            except Exception as e:
                print(f"Error reading config at {config_path}: {e}")
                
    print("Config token not found, using empty default")
    return url, ""

GATEWAY_URL, GATEWAY_TOKEN = get_gateway_config()
MODEL_ID = "google-antigravity/gemini-3-pro-high"

print(f"Using gateway: {GATEWAY_URL}")
print(f"Using model: {MODEL_ID}")

def call_vision_model(image_path, objective, step_num, action_history=None):
    """Call vision model via direct HTTP request to gateway."""
    
    # Encode and compress image
    base64_image, mime_type = encode_image(image_path)
    
    # Build history context
    history_text = ""
    if action_history:
        history_text = "\n\nPrevious actions taken so far:\n"
        for i, act in enumerate(action_history, 1):
            history_text += f"  Step {i}: {json.dumps(act)}\n"
        history_text += "\nDo NOT repeat the same action. Progress toward the objective.\n"
    
    prompt = f"""You are an autonomous computer control agent on Windows. Your objective: "{objective}"
{history_text}
Look at the current screenshot. What is the NEXT SINGLE ACTION to take?

Return ONLY a JSON object (no markdown, no explanation) with ONE of these actions:
- {{"action": "click", "x": 100, "y": 200}} - Click at pixel coordinates
- {{"action": "type",  "text": "calculator"}} - Type text (used after clicking a text field or search box)
- {{"action": "key", "key": "enter"}} - Press a key (enter, tab, esc, etc.)
- {{"action": "done"}} - Objective is complete

Strategy tips:
- To open an app: press Windows key, then type the app name, then press enter
- After pressing Windows key, the Start menu/search opens - type the app name next
- Do NOT repeat the same action twice in a row
"""
    
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
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 300
            },
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"  API Error ({response.status_code}): {response.text[:200]}")
            return None
            
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        if not content:
            print(f"  Empty response from model")
            return None
            
        # Parse JSON from response
        text = content.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        return json.loads(text)
        
    except requests.exceptions.ConnectionError as e:
        print(f"  Connection error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        print(f"  Raw response: {content[:200]}")
        return None
    except Exception as e:
        print(f"  Unexpected error: {e}")
        return None

def take_screenshot(step_num):
    """Capture screen using desktop skill."""
    screenshot_path = SCREENSHOTS_DIR / f"computer_use_step_{step_num:03d}.png"
    
    try:
        # Use desktop skill's screenshot.py
        import subprocess
        result = subprocess.run(
            ["python", str(SCREENSHOT_SCRIPT), str(screenshot_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return screenshot_path
        else:
            print(f"Screenshot error: {result.stderr}")
            return None
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return None

def resize_screenshot(image_path, max_width=800):
    """Resize and compress screenshot to reduce payload size."""
    from PIL import Image
    
    try:
        img = Image.open(image_path)
        
        # Calculate new dimensions maintaining aspect ratio
        width, height = img.size
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save as JPEG for much better compression
        compressed_path = image_path.parent / "compressed_view.jpg"
        img.save(compressed_path, "JPEG", quality=50, optimize=True)
        return compressed_path
        
    except Exception as e:
        print(f"  Failed to resize screenshot: {e}")
        return image_path

def encode_image(image_path):
    """Encode image to base64 after compressing."""
    resized_path = resize_screenshot(image_path)
    
    with open(resized_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
    
    size_kb = len(encoded) / 1024
    print(f"  Image payload: {size_kb:.1f} KB")
    
    # Use jpeg mime type
    return encoded, "image/jpeg"

def execute_action(action_json, step_num):
    """Execute the action decided by the vision model."""
    import subprocess
    
    action_type = action_json.get("action")
    
    if action_type == "click":
        x = action_json.get("x")
        y = action_json.get("y")
        print(f"  -> Clicking at ({x}, {y})")
        subprocess.run(["python", str(MOUSE_SCRIPT), "click", str(x), str(y)])
        
    elif action_type == "type":
        text = action_json.get("text")
        print(f"  -> Typing: {text}")
        subprocess.run(["python", str(KEYBOARD_SCRIPT), "type", text])
        
    elif action_type == "key":
        key = action_json.get("key")
        print(f"  -> Pressing key: {key}")
        subprocess.run(["python", str(KEYBOARD_SCRIPT), "press", key])
        
    elif action_type == "done":
        print("  [OK] Task completed!")
        return True
        
    else:
        print(f"  [WARN] Unknown action: {action_type}")
        
    return False

def run_autonomous_agent(objective, max_steps=20):
    """Run the autonomous vision-guided loop."""
    print(f"Starting Autonomous Computer Control")
    print(f"Objective: {objective}")
    print(f"Max steps: {max_steps}")
    print(f"Screenshots: {SCREENSHOTS_DIR}")
    print("-" * 60)
    
    step = 0
    action_history = []
    
    while step < max_steps:
        step += 1
        print(f"\n[Step {step}/{max_steps}]")
        
        # 1. SEE - Take screenshot
        print("  Capturing screen...")
        image_path = take_screenshot(step)
        if not image_path:
            print("  Screenshot failed, retrying...")
            time.sleep(1)
            continue
            
        # 2. THINK - Analyze with vision model (with history)
        print("  Analyzing screen...")
        action = call_vision_model(image_path, objective, step, action_history)
        
        if not action:
            print("  Vision model failed, retrying...")
            time.sleep(2)
            continue
        
        # Track action history
        action_history.append(action)
            
        # 3. ACT - Execute the action
        is_done = execute_action(action, step)
        if is_done:
            print(f"\nObjective completed in {step} steps!")
            return True
            
        # Pause for stability
        time.sleep(1.5)
        
    print(f"\n⚠️  Reached maximum steps ({max_steps})")
    return False

def main():
    parser = argparse.ArgumentParser(description="Autonomous Computer Control Agent")
    parser.add_argument("objective", help="The objective to accomplish")
    parser.add_argument("--max-steps", type=int, default=20, help="Maximum number of steps (default: 20)")
    
    args = parser.parse_args()
    
    try:
        success = run_autonomous_agent(args.objective, args.max_steps)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
