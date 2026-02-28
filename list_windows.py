import pygetwindow as gw
for window in gw.getAllWindows():
    if window.title:
        print(window.title)
