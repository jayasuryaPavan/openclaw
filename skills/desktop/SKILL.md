---
name: desktop
description: Desktop automation - screenshot, mouse, keyboard, media control, and window focus for Windows GUI interaction.
homepage: https://pyautogui.readthedocs.io
metadata:
  {
    "openclaw":
      {
        "emoji": "🖥️",
        "requires": { "bins": ["python"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "manual",
              "label": "Install dependencies: pip install pyautogui pillow pygetwindow",
            },
          ],
      },
  }
---

# Desktop Automation

Use the Python scripts in this skill folder to control the desktop GUI.

> **CRITICAL**: You MUST use ONLY these Python scripts for desktop control.
> NEVER generate raw PowerShell, WScript.Shell, SendKeys, SendMessageW, or
> any other native Windows scripting commands. They will fail with syntax
> errors and permission issues. Always use the Python scripts below.

## Requirements

- Python 3.x
- `pyautogui`, `pillow`, and `pygetwindow` installed
  ```bash
  pip install pyautogui pillow pygetwindow
  ```

## Commands

All commands must be run from this skill's directory.

### Screenshot
```bash
python screenshot.py output.png
```
Captures the entire screen and saves to `output.png`. Outputs `MEDIA:./screenshots/output.png` for Telegram delivery.

### Vision Analysis (See + Understand Screen)
```bash
# Take a screenshot AND analyze what's on screen
python analyze.py "What do you see on screen?"
python analyze.py "Is WhatsApp open? What is the latest message?"
python analyze.py "What windows are open?"

# Analyze an existing screenshot
python analyze.py "Describe what you see" --screenshot screenshots/existing.png
```
Takes a screenshot and sends it to the vision model for analysis. Use this whenever you need to **understand** what's on screen, not just capture it. The output includes both `MEDIA:` for the image and the vision model's text analysis.

### Mouse Control
```bash
# Move mouse to coordinates
python mouse.py move 100 200

# Click at current position
python mouse.py click

# Click at specific coordinates
python mouse.py click 100 200

# Right-click
python mouse.py rightclick 100 200

# Double-click
python mouse.py doubleclick 100 200
```

### Keyboard Control
```bash
# Type text
python keyboard.py type "Hello World"

# Press a single key (enter, tab, space, escape, backspace, delete, etc.)
python keyboard.py press enter

# Press hotkey combination
python keyboard.py hotkey ctrl c
python keyboard.py hotkey alt tab
python keyboard.py hotkey ctrl shift esc
```

### Media Control
```bash
# Play/pause media
python keyboard.py media playpause

# Next/previous track
python keyboard.py media next
python keyboard.py media prev

# Volume up/down/mute
python keyboard.py media volumeup
python keyboard.py media volumedown
python keyboard.py media mute
```

### Window Focus
```bash
# Bring a window to the foreground by its title (partial match)
python keyboard.py focus "Brave"
python keyboard.py focus "Notepad"
python keyboard.py focus "Visual Studio Code"
```

## Notes

- Coordinates are in pixels from top-left (0,0).
- Use screenshot first to see what's on screen before clicking.
- For safety, pyautogui has a fail-safe: move mouse to top-left corner to abort.
- For media keys: the system must have a media player running for playpause/next/prev to work.
- For window focus: uses partial title matching, so "Brave" will match "Brave Browser - New Tab".

