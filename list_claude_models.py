import subprocess

node_exe = r"C:\Program Files\nodejs\node.exe"
command = [node_exe, "scripts/run-node.mjs", "models", "list"]

try:
    res = subprocess.run(command, capture_output=True, text=False)
    stdout = res.stdout.decode('utf-8', errors='ignore')
    print(stdout)
except Exception as e:
    print(f"Error: {e}")
