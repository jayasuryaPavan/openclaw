import mss
import mss.tools

with mss.mss() as sct:
    # Monitor 0 is all monitors
    monitor = sct.monitors[0]
    screenshot = sct.grab(monitor)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output="screenshots/combined_desktop.png")
    print("MEDIA:./screenshots/combined_desktop.png")
