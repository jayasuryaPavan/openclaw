import pygetwindow as gw
import time
from PIL import ImageGrab
import win32api
import win32con

def show_window(title_part):
    windows = [w for w in gw.getAllWindows() if title_part.lower() in w.title.lower()]
    if not windows:
        return False
    
    win = windows[0]
    if win.isMinimized:
        win.restore()
    win.activate()
    time.sleep(1)
    return True

show_window("OpenClaw Control")
show_window("Panda Chat - Antigravity")
show_window("Classyy - Antigravity")

left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

img = ImageGrab.grab(bbox=(left, top, left + width, top + height), all_screens=True)
img.save("antigravity_virtual_check.png")
print("Saved antigravity_virtual_check.png")
