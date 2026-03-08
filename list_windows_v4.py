import pygetwindow as gw
for win in gw.getAllWindows():
    if win.title:
        print(f"Title: {win.title} | Size: {win.width}x{win.height} | Pos: {win.left},{win.top}")
