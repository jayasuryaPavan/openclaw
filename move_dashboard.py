import pygetwindow as gw
import time

def main():
    target = "Influencer Dashboard - BELL Studios"
    wins = [w for w in gw.getAllWindows() if target in w.title]
    if wins:
        win = wins[0]
        win.restore()
        win.moveTo(100, 100) # Move to top left of Display 1
        win.resizeTo(1440, 900)
        time.sleep(1)
        print("Moved window to Display 1")
    else:
        print("Not found")

if __name__ == "__main__":
    main()
