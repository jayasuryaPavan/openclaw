import mss
import mss.tools

with mss.mss() as sct:
    for i, monitor in enumerate(sct.monitors):
        if i == 0: continue
        screenshot = sct.grab(monitor)
        output = f"screenshots/full_display_{i}.png"
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=output)
        print(f"Captured Display {i}: {output}")
