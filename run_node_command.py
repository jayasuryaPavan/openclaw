import subprocess

node_exe = r"C:\Program Files\nodejs\node.exe"
command = [node_exe, "scripts/run-node.mjs", "status", "--deep"]

try:
    res = subprocess.run(command, capture_output=True, text=True)
    print("STDOUT:")
    print(res.stdout)
    print("STDERR:")
    print(res.stderr)
except Exception as e:
    print(f"Error: {e}")
