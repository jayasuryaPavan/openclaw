import os
def check_dirs(paths):
    for p in paths:
        if os.path.exists(p):
            print(f"Path: {p}")
            print(f"Contents: {os.listdir(p)}")
            print("-" * 20)

check_dirs([r"c:\Work Space\bell studios", r"c:\Work Space\BellStudios", r"C:\Workspace\Classyy"])
