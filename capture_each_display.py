from PIL import ImageGrab
import win32api
import win32con

monitors = win32api.EnumDisplayMonitors()
for i, monitor in enumerate(monitors):
    hMonitor, hdcMonitor, rect = monitor
    left, top, right, bottom = rect
    print(f"Monitor {i+1}: {left}, {top}, {right}, {bottom}")
    img = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
    filename = f"display_{i+1}.png"
    img.save(filename)
    print(f"Saved {filename}")
