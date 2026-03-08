import subprocess
import sys

node_exe = r"C:\Program Files\nodejs\node.exe"
command = [node_exe, "scripts/run-node.mjs", "status", "--deep"]

try:
    # Use utf-8 and ignore errors to avoid decoding issues
    res = subprocess.run(command, capture_output=True, text=False)
    stdout = res.stdout.decode('utf-8', errors='ignore')
    stderr = res.stderr.decode('utf-8', errors='ignore')
    print("STDOUT:")
    print(stdout)
    print("STDERR:")
    print(stderr)
except Exception as e:
    print(f"Error: {e}")
