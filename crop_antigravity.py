import pygetwindow as gw
import pyautogui
import time
import os
from PIL import Image

def main():
    target = "Panda Chat - Antigravity"
    windows = gw.getWindowsWithTitle(target)
    if not windows:
        print("Not found")
        return
    
    win = windows[0]
    win.restore()
    time.sleep(0.5)
    # Don't use activate() if it's failing with 'error 0'
    
    # Take screenshot of display 1 and crop
    # Display 1 is at 0,0 2880x1800
    # Window is at 0,0 1440x852
    screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
    output = "screenshots/antigravity_crop.png"
    screenshot.save(output)
    print(f"MEDIA:./{output}")

if __name__ == "__main__":
    main()
