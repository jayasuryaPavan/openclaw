import pygetwindow as gw
import time
import pyautogui

def show_window(title_part):
    windows = [w for w in gw.getAllWindows() if title_part.lower() in w.title.lower()]
    if not windows:
        print(f"No window found for: {title_part}")
        return False
    
    win = windows[0]
    print(f"Bringing to front: {win.title}")
    if win.isMinimized:
        win.restore()
    win.activate()
    time.sleep(1)
    return True

# Try to show all relevant windows
show_window("OpenClaw Control")
show_window("Panda Chat - Antigravity")
show_window("Classyy - Antigravity")

# Take a fresh screenshot
screenshot = pyautogui.screenshot()
screenshot.save("antigravity_showcase.png")
print("Screenshot saved to antigravity_showcase.png")
