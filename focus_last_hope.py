import pygetwindow as gw
import time
import pyautogui

def main():
    # Minimize everything that might be on top
    for title in ["WhatsApp", "Chrome", "Brave", "Settings"]:
        for win in gw.getWindowsWithTitle(title):
            try:
                win.minimize()
            except:
                pass
    
    time.sleep(1)
    # Restore Antigravity
    for win in gw.getWindowsWithTitle("Antigravity"):
        try:
            win.restore()
            win.moveTo(0,0)
            time.sleep(1)
        except:
            pass
            
    screenshot = pyautogui.screenshot(region=(0, 0, 1920, 1080))
    screenshot.save("screenshots/antigravity_last_hope.png")
    print("MEDIA:./screenshots/antigravity_last_hope.png")

if __name__ == "__main__":
    main()
