import os

possible_git_paths = [
    r"C:\Program Files\Git\cmd\git.exe",
    r"C:\Program Files\Git\bin\git.exe",
    r"C:\Program Files (x86)\Git\cmd\git.exe",
    r"C:\Users\jayas\AppData\Local\Programs\Git\cmd\git.exe"
]

for p in possible_git_paths:
    if os.path.exists(p):
        print(f"Found Git at: {p}")
