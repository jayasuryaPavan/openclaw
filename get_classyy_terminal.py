import pyautogui
import time
import pyperclip

def main():
    # Window is at -7, -7. Size is 1453x865.
    # Terminal is around bottom (y=800).
    pyautogui.click(500, 800)
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    text = pyperclip.paste()
    with open("classyy_terminal.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Done")

if __name__ == "__main__":
    main()
