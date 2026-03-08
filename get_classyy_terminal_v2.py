import pygetwindow as gw
import time
import pyautogui
import pyperclip

def main():
    target = "Classyy - Antigravity"
    wins = [w for w in gw.getAllWindows() if target in w.title]
    if wins:
        win = wins[0]
        win.activate()
        time.sleep(1)
        # Click in terminal
        pyautogui.click(win.left + 500, win.top + win.height - 100)
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(1)
        text = pyperclip.paste()
        with open("classyy_terminal_v2.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Done")
    else:
        print("Not found")

if __name__ == "__main__":
    main()
