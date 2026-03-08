import pygetwindow as gw
import time
import pyautogui
import os

def main():
    target = "Panda Chat - Antigravity"
    wins = [w for w in gw.getAllWindows() if target in w.title]
    if not wins:
        print(f"No window found with title containing: {target}")
        return
    
    win = wins[0]
    print(f"Found window: {win.title}")
    
    try:
        win.restore()
        win.moveTo(100, 100) # Move to a known monitor (Monitor 1)
        win.resizeTo(1920, 1080)
        time.sleep(1)
        # Click on the title bar area to ensure it's truly active
        pyautogui.click(win.left + 200, win.top + 10) 
        time.sleep(1)
        
        # Take screenshot of the window
        screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
        output_path = "screenshots/terminal_check.png"
        os.makedirs("screenshots", exist_ok=True)
        screenshot.save(output_path)
        print(f"MEDIA:./{output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
