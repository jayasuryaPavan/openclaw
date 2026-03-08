import pygetwindow as gw
import time
import pyautogui
import os

def main():
    target = "Influencer Dashboard - BELL Studios"
    wins = [w for w in gw.getAllWindows() if target in w.title]
    if not wins:
        print("Not found")
        return
    
    win = wins[0]
    win.restore()
    win.activate()
    time.sleep(2) # Give it time to render
    
    screenshot = pyautogui.screenshot(region=(win.left, win.top, win.width, win.height))
    output = "screenshots/influencer_dashboard_focus.png"
    os.makedirs("screenshots", exist_ok=True)
    screenshot.save(output)
    print(f"MEDIA:./{output}")

if __name__ == "__main__":
    main()
