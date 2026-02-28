#!/usr/bin/env python3
"""Screenshot utility for desktop automation."""
import sys
import time
import pyautogui

def main():
    if len(sys.argv) < 2:
        print("Usage: python screenshot.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    
    # Ensure screenshots are saved to screenshots directory
    # Find the openclaw root directory (2 levels up from this script)
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    openclaw_root = os.path.dirname(os.path.dirname(script_dir))
    screenshots_dir = os.path.join(openclaw_root, "screenshots")
    
    # Create screenshots directory if it doesn't exist
    os.makedirs(screenshots_dir, exist_ok=True)
    
    # If the output path doesn't already include the screenshots directory, prepend it
    if not os.path.isabs(output_path) and "screenshots" not in output_path:
        output_path = os.path.join(screenshots_dir, output_path)
    
    # Give the OS a moment to settle (helps with "screen grab failed" errors)
    time.sleep(0.5)
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(output_path)
            
            # Output MEDIA: token with relative path (expected by OpenClaw engine for Telegram delivery)
            rel_path = os.path.relpath(output_path, openclaw_root).replace("\\", "/")
            print(f"MEDIA:./{rel_path}")
            return
        except OSError as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Screen grab failed ({e}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Error: Screenshot failed after {max_retries} attempts: {e}")
                print("\nTIP: If this persists, try installing the 'mss' library:")
                print("pip install mss")
                sys.exit(1)

if __name__ == "__main__":
    main()
