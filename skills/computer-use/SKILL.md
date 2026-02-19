---
name: computer-use
description: Autonomous computer control - gives Panda the ability to autonomously control the desktop through vision-guided loops (screenshot → analyze → act → repeat).
homepage: https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo
metadata:
  {
    "openclaw":
      {
        "emoji": "🤖",
        "requires": { "bins": ["python"], "skills": ["desktop"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "manual",
              "label": "Install dependencies: pip install openai pillow pyautogui",
            },
          ],
      },
  }
---

# Autonomous Computer Control

Enables Panda to autonomously control the desktop through vision-guided action loops.

> **CRITICAL**: This skill depends on the `desktop` skill. Ensure that skill is available and properly configured.

## Requirements

- Python 3.x
- `pyautogui`, `pillow`, and `openai` installed
  ```bash
  pip install pyautogui pillow openai
  ```
- OpenClaw gateway running (for vision model access)
- Desktop skill properly configured

## Commands

### Autonomous Execution
```bash
python autonomous.py "<objective>" [--max-steps N]
```

Executes an objective autonomously by looping:
1. Take screenshot
2. Analyze with vision model (what should I do next?)
3. Execute action (click, type, key press)
4. Repeat until objective complete or max steps reached

**Arguments:**
- `objective`: The goal to accomplish (e.g., "open calculator and compute 5+7")
- `--max-steps`: Maximum number of action loops (default: 20)

**Example:**
```bash
python autonomous.py "open notepad and type hello world"
python autonomous.py "find and open WhatsApp" --max-steps 15
```

## How It Works

The autonomous agent:
1. Captures screen using desktop skill's screenshot capability
2. Sends screenshot to Gemini vision model via OpenClaw gateway
3. Model analyzes screen and decides next action
4. Executes action using desktop skill (mouse/keyboard)
5. Continues loop until objective is met or max steps reached

## Actions Supported

- **Click**: `{"action": "click", "x": 100, "y": 200}`
- **Type**: `{"action": "type", "text": "hello world"}`
- **Key Press**: `{"action": "key", "key": "enter"}` (enter, tab, esc, etc.)
- **Done**: `{"action": "done"}` (signals completion)

## Screenshots

All screenshots are saved to `openclaw/screenshots/computer_use_*.png` for debugging and review.

## Limitations

- Can only interact with visible windows/elements
- Limited to 20 steps by default (configurable)
- Requires clear, specific objectives
- May need multiple attempts for complex tasks
