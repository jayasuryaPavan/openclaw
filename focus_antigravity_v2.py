import pygetwindow as gw
import time
import pyautogui

def main():
    title = "Panda Chat - Antigravity"
    wins = [w for w in gw.getAllWindows() if title in w.title]
    if not wins:
        print("Window not found")
        return
    
    win = wins[0]
    print(f"Found: {win.title}")
    
    # Try multiple ways to bring to front
    try:
        win.restore()
        time.sleep(0.5)
        win.moveTo(0, 0)
        time.sleep(0.5)
        win.activate()
    except Exception as e:
        print(f"Focus error: {e}")
    
    time.sleep(1)
    # Take screenshot of primary display (Display 1)
    # Based on check_monitors.py: {'left': 0, 'top': 0, 'width': 2880, 'height': 1800}
    screenshot = pyautogui.screenshot(region=(0, 0, 2880, 1800))
    screenshot.save("screenshots/antigravity_attempt_2.png")
    print("MEDIA:./screenshots/antigravity_attempt_2.png")

if __name__ == "__main__":
    main()
