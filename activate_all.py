import pygetwindow as gw
import time
import pyautogui

wins = gw.getWindowsWithTitle("WhatsApp")
for win in wins:
    print(f"Trying to activate: {win.title}")
    if win.isMinimized:
        win.restore()
    try:
        win.activate()
    except:
        pass
    time.sleep(1)

pyautogui.screenshot("whatsapp_all_attempts.png")
