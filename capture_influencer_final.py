import mss
import mss.tools

with mss.mss() as sct:
    region = {'left': 100, 'top': 100, 'width': 1440, 'height': 900}
    screenshot = sct.grab(region)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output="screenshots/influencer_final.png")
    print("MEDIA:./screenshots/influencer_final.png")
