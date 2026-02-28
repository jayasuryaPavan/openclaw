import pygetwindow as gw
target = "Antigravity"
for win in gw.getAllWindows():
    if target in win.title:
        print(f"Title: {win.title}, Left: {win.left}, Top: {win.top}, Width: {win.width}, Height: {win.height}")
