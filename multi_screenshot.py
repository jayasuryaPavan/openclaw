import pyautogui
import os

def main():
    screens = pyautogui.getScreens() if hasattr(pyautogui, 'getScreens') else []
    # PyAutoGUI doesn't have a direct multi-screen screenshot in the standard version easily.
    # But we can try to find the number of monitors via screen dimensions or just use mss if available.
    
    try:
        from mss import mss
        with mss() as sct:
            for i, monitor in enumerate(sct.monitors):
                if i == 0: continue # Monitor 0 is the "all in one"
                output = f"screenshots/display_{i}.png"
                sct_img = sct.grab(monitor)
                import mss.tools
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)
                print(f"MEDIA:./screenshots/display_{i}.png")
    except ImportError:
        # Fallback to pyautogui for primary
        pyautogui.screenshot("screenshots/display_1.png")
        print("MEDIA:./screenshots/display_1.png")

if __name__ == '__main__':
    main()
