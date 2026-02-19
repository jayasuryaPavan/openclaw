import mss
import mss.tools

with mss.mss() as sct:
    for i, monitor in enumerate(sct.monitors[1:], 1):
        output = f"monitor-{i}.png"
        sct_img = sct.shot(monitor=i, output=output)
        print(f"Monitor {i} saved to {output}")
