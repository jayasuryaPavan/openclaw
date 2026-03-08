import subprocess

node_exe = r"C:\Program Files\nodejs\node.exe"
command = [node_exe, "scripts/run-node.mjs", "--help"]

try:
    res = subprocess.run(command, capture_output=True, text=False)
    stdout = res.stdout.decode('utf-8', errors='ignore')
    
    with open("help_output.txt", "w", encoding="utf-8") as f:
        f.write(stdout)
    
    print("Done.")
except Exception as e:
    print(f"Error: {e}")
