#!/usr/bin/env python3
"""Screenshot utility for desktop automation."""
import sys
import pyautogui

def main():
    if len(sys.argv) < 2:
        print("Usage: python screenshot.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    screenshot = pyautogui.screenshot()
    screenshot.save(output_path)
    print(f"Screenshot saved to {output_path}")

if __name__ == "__main__":
    main()
