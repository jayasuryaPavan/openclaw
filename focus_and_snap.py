import pygetwindow as gw
import pyautogui
import time
import os

def main():
    target = "Panda Chat - Antigravity"
    windows = gw.getWindowsWithTitle(target)
    if not windows:
        print(f"No window found with title: {target}")
        return
    
    win = windows[0]
    try:
        win.restore()
        win.activate()
        time.sleep(1)
        
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
        output = "screenshots/antigravity_focused.png"
        os.makedirs("screenshots", exist_ok=True)
        screenshot.save(output)
        print(f"MEDIA:./{output}")
    except Exception as e:
        print(f"Error focusing/screenshotting: {e}")

if __name__ == "__main__":
    main()
