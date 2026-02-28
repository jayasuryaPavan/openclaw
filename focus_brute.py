import pyautogui
import time
import pygetwindow as gw

def main():
    target = "Panda Chat - Antigravity"
    wins = [w for w in gw.getAllWindows() if target in w.title]
    if wins:
        win = wins[0]
        win.restore()
        time.sleep(0.5)
        # Click in the middle of where the window should be
        pyautogui.click(win.left + win.width//2, win.top + win.height//2)
        time.sleep(1)
        
    screenshot = pyautogui.screenshot(region=(0, 0, 2880, 1800))
    screenshot.save("screenshots/antigravity_attempt_3.png")
    print("MEDIA:./screenshots/antigravity_attempt_3.png")

if __name__ == "__main__":
    main()
