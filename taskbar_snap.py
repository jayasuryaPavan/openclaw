import pyautogui
s = pyautogui.screenshot(region=(0, 1600, 2880, 200))
s.save("taskbar.png")
