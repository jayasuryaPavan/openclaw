import mss
import mss.tools

with mss.mss() as sct:
    # Capture the region where the window is supposed to be
    # Monitor 1 ends at 1800. Window starts at 1793.
    # It likely extends into the gap or the next monitor.
    region = {'left': 0, 'top': 1700, 'width': 1500, 'height': 1000}
    screenshot = sct.grab(region)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output="screenshots/influencer_zoom.png")
    print("MEDIA:./screenshots/influencer_zoom.png")
