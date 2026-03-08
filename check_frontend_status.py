import os
frontend_dir = r"c:\Work Space\BellStudios\Frontend"
if os.path.exists(frontend_dir):
    print(f"Contents: {os.listdir(frontend_dir)}")
else:
    print("Frontend directory does not exist.")
