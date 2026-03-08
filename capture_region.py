import mss
import mss.tools

with mss.mss() as sct:
    # Capture the specific region where the window is supposed to be
    region = {'left': -7, 'top': 1793, 'width': 1453, 'height': 865}
    screenshot = sct.grab(region)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output="screenshots/influencer_window_region.png")
    print("MEDIA:./screenshots/influencer_window_region.png")
