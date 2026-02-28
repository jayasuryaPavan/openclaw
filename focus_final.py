import pyautogui
import time
import pygetwindow as gw

def main():
    target = "Panda Chat - Antigravity"
    wins = [w for w in gw.getAllWindows() if target in w.title]
    if wins:
        win = wins[0]
        win.restore()
        win.moveTo(0,0)
        win.resizeTo(1920, 1080)
        time.sleep(1)
        # Brute force click on the title bar area
        pyautogui.click(500, 10) 
        time.sleep(1)

    screenshot = pyautogui.screenshot(region=(0, 0, 1920, 1080))
    screenshot.save("screenshots/antigravity_final_try.png")
    print("MEDIA:./screenshots/antigravity_final_try.png")

if __name__ == "__main__":
    main()
