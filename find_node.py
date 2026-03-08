import os

possible_paths = [
    r"C:\Program Files\nodejs\node.exe",
    r"C:\Program Files (x86)\nodejs\node.exe",
    r"C:\Work Space\nodejs\node.exe",
    r"C:\Users\jayas\AppData\Local\nvs\default\node.exe",
    r"C:\Users\jayas\AppData\Roaming\npm\node.exe"
]

for p in possible_paths:
    if os.path.exists(p):
        print(f"Found Node at: {p}")
