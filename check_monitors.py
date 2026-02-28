import pyautogui
try:
    import mss
    with mss.mss() as sct:
        print(f"Monitors: {sct.monitors}")
        for i, monitor in enumerate(sct.monitors):
            if i == 0: continue
            output = f"screenshots/display_{i}.png"
            sct_img = sct.grab(monitor)
            import mss.tools
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
            print(f"Captured Display {i}: {output}")
except Exception as e:
    print(f"Error: {e}")
