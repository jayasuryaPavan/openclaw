# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## ⛔ Desktop Automation — MANDATORY RULES

**NEVER generate raw PowerShell, C#, WScript.Shell, SendKeys, SendMessageW, Add-Type, DllImport, or any native Windows scripting for desktop control.** These WILL FAIL due to Windows UIPI security restrictions and PowerShell parsing issues.

**ALWAYS use the Python scripts** in `skills/desktop/`:

| Task | Command |
|---|---|
| Screenshot | `python skills/desktop/screenshot.py output.png` |
| Move mouse | `python skills/desktop/mouse.py move X Y` |
| Click | `python skills/desktop/mouse.py click X Y` |
| Right-click | `python skills/desktop/mouse.py rightclick X Y` |
| Double-click | `python skills/desktop/mouse.py doubleclick X Y` |
| Type text | `python skills/desktop/keyboard.py type "text"` |
| Press key | `python skills/desktop/keyboard.py press enter` |
| Hotkey | `python skills/desktop/keyboard.py hotkey ctrl c` |
| **Play/Pause** | `python skills/desktop/keyboard.py media playpause` |
| **Next track** | `python skills/desktop/keyboard.py media next` |
| **Prev track** | `python skills/desktop/keyboard.py media prev` |
| **Volume up** | `python skills/desktop/keyboard.py media volumeup` |
| **Volume down** | `python skills/desktop/keyboard.py media volumedown` |
| **Mute** | `python skills/desktop/keyboard.py media mute` |
| **Focus window** | `python skills/desktop/keyboard.py focus "Brave"` |

If a command fails, report the error. Do NOT try alternative PowerShell/C# approaches.

---

## 💬 Telegram Response Style

Keep Telegram responses **short and concise**. Maximum 2-3 sentences. No walls of text, no numbered approach lists, no verbose explanations. Just do the thing and report the result briefly.

