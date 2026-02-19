#!/usr/bin/env python3
"""Mouse control utility for desktop automation."""
import sys
import pyautogui
pyautogui.FAILSAFE = False

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python mouse.py move <x> <y>")
        print("  python mouse.py click [x] [y]")
        print("  python mouse.py rightclick [x] [y]")
        print("  python mouse.py doubleclick [x] [y]")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "move":
        if len(sys.argv) < 4:
            print("Error: move requires x and y coordinates")
            sys.exit(1)
        x, y = int(sys.argv[2]), int(sys.argv[3])
        pyautogui.moveTo(x, y, duration=0.2)
        print(f"Moved mouse to ({x}, {y})")
    
    elif action == "click":
        if len(sys.argv) >= 4:
            x, y = int(sys.argv[2]), int(sys.argv[3])
            pyautogui.click(x, y)
            print(f"Clicked at ({x}, {y})")
        else:
            pyautogui.click()
            print("Clicked at current position")
    
    elif action == "rightclick":
        if len(sys.argv) >= 4:
            x, y = int(sys.argv[2]), int(sys.argv[3])
            pyautogui.rightClick(x, y)
            print(f"Right-clicked at ({x}, {y})")
        else:
            pyautogui.rightClick()
            print("Right-clicked at current position")
    
    elif action == "doubleclick":
        if len(sys.argv) >= 4:
            x, y = int(sys.argv[2]), int(sys.argv[3])
            pyautogui.doubleClick(x, y)
            print(f"Double-clicked at ({x}, {y})")
        else:
            pyautogui.doubleClick()
            print("Double-clicked at current position")
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

if __name__ == "__main__":
    main()
