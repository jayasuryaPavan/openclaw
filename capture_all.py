from PIL import ImageGrab
import win32api
import win32con

# Get the bounding box of all monitors
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

print(f"Virtual screen: {left}, {top}, {width}, {height}")

# Capture the entire virtual screen
img = ImageGrab.grab(bbox=(left, top, left + width, top + height), all_screens=True)
img.save("all_screens.png")
print("Saved all_screens.png")
