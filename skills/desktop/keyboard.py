#!/usr/bin/env python3
"""Keyboard control utility for desktop automation."""
import sys
import pyautogui
pyautogui.FAILSAFE = False

# Media key mappings for pyautogui
MEDIA_KEYS = {
    "playpause": "playpause",
    "play": "playpause",
    "pause": "playpause",
    "nexttrack": "nexttrack",
    "next": "nexttrack",
    "prevtrack": "prevtrack",
    "previous": "prevtrack",
    "prev": "prevtrack",
    "volumeup": "volumeup",
    "volumedown": "volumedown",
    "volumemute": "volumemute",
    "mute": "volumemute",
}

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python keyboard.py type <text>")
        print("  python keyboard.py press <key>")
        print("  python keyboard.py hotkey <key1> <key2> [key3...]")
        print("  python keyboard.py media <action>")
        print("    actions: playpause, next, prev, volumeup, volumedown, mute")
        print("  python keyboard.py focus <window_title>")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "type":
        if len(sys.argv) < 3:
            print("Error: type requires text argument")
            sys.exit(1)
        text = " ".join(sys.argv[2:])
        pyautogui.write(text, interval=0.05)
        print(f"Typed: {text}")
    
    elif action == "press":
        if len(sys.argv) < 3:
            print("Error: press requires key argument")
            sys.exit(1)
        key = sys.argv[2]
        pyautogui.press(key)
        print(f"Pressed: {key}")
    
    elif action == "hotkey":
        if len(sys.argv) < 3:
            print("Error: hotkey requires at least one key")
            sys.exit(1)
        keys = sys.argv[2:]
        pyautogui.hotkey(*keys)
        print(f"Pressed hotkey: {'+'.join(keys)}")
    
    elif action == "media":
        if len(sys.argv) < 3:
            print("Error: media requires an action (playpause, next, prev, volumeup, volumedown, mute)")
            sys.exit(1)
        media_action = sys.argv[2].lower()
        key = MEDIA_KEYS.get(media_action)
        if not key:
            print(f"Unknown media action: {media_action}")
            print(f"Valid actions: {', '.join(MEDIA_KEYS.keys())}")
            sys.exit(1)
        pyautogui.press(key)
        print(f"Media: {media_action}")
    
    elif action == "focus":
        if len(sys.argv) < 3:
            print("Error: focus requires a window title")
            sys.exit(1)
        title = " ".join(sys.argv[2:])
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(title)
            if windows:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                print(f"Focused window: {win.title}")
            else:
                print(f"No window found matching: {title}")
                all_windows = gw.getAllWindows()
                titles = [w.title for w in all_windows if w.title.strip()]
                if titles:
                    print("\nAvailable windows:")
                    for t in sorted(set(titles)):
                        print(f"  - {t}")
                sys.exit(1)
        except ImportError:
            # Fallback: use pyautogui hotkey to alt-tab (less precise)
            print("pygetwindow not installed. Install with: pip install pygetwindow")
            sys.exit(1)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
