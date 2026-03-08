import mss
import mss.tools

with mss.mss() as sct:
    # Monitor 2 is index 2
    monitor = sct.monitors[2]
    screenshot = sct.grab(monitor)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output="screenshots/classyy_monitor_2.png")
    print("MEDIA:./screenshots/classyy_monitor_2.png")
