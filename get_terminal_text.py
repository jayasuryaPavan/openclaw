import pyautogui
import time
import pyperclip
import pygetwindow as gw

def main():
    target = "Panda Chat - Antigravity"
    wins = [w for w in gw.getAllWindows() if target in w.title]
    if not wins:
        print("Not found")
        return
    
    win = wins[0]
    win.activate()
    time.sleep(1)
    
    # VS Code terminal usually has focus if it was the last thing used.
    # Try to copy all from terminal: Ctrl+A (if it's focused) then Ctrl+C
    # Or try to click in the terminal area first.
    # Terminal is usually at the bottom.
    pyautogui.click(win.left + 500, win.top + win.height - 100)
    time.sleep(0.5)
    
    # Try to select and copy
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(1)
    
    text = pyperclip.paste()
    with open("terminal_clipboard.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Done")

if __name__ == "__main__":
    main()
