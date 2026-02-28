import pyautogui
import time
import pygetwindow as gw

def main():
    target = "Panda Chat - Antigravity"
    # Minimize other windows
    for win in gw.getAllWindows():
        if win.title and target not in win.title and "Watch" not in win.title and "WhatsApp" not in win.title:
             try:
                 win.minimize()
             except:
                 pass
    
    time.sleep(1)
    
    # Now find and restore target
    wins = [w for w in gw.getAllWindows() if target in w.title]
    if wins:
        win = wins[0]
        win.restore()
        time.sleep(1)
        win.activate()
        time.sleep(1)

    screenshot = pyautogui.screenshot(region=(0, 0, 2880, 1800))
    screenshot.save("screenshots/antigravity_attempt_4.png")
    print("MEDIA:./screenshots/antigravity_attempt_4.png")

if __name__ == "__main__":
    main()
