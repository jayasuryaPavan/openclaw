import os

possible_npm_paths = [
    r"C:\Program Files\nodejs\npm.cmd",
    r"C:\Program Files (x86)\nodejs\npm.cmd",
    r"C:\Users\jayas\AppData\Roaming\npm\npm.cmd"
]

for p in possible_npm_paths:
    if os.path.exists(p):
        print(f"Found npm at: {p}")
