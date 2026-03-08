import mss
import mss.tools

with mss.mss() as sct:
    # Monitor 1 is index 1
    monitor = sct.monitors[1]
    screenshot = sct.grab(monitor)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output="screenshots/classyy_monitor_1.png")
    print("MEDIA:./screenshots/classyy_monitor_1.png")
