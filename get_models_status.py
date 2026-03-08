import subprocess
import os

node_exe = r"C:\Program Files\nodejs\node.exe"
command = [node_exe, "scripts/run-node.mjs", "models", "status"]

try:
    res = subprocess.run(command, capture_output=True, text=False)
    stdout = res.stdout.decode('utf-8', errors='ignore')
    
    with open("current_models_status.txt", "w", encoding="utf-8") as f:
        f.write(stdout)
    
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
