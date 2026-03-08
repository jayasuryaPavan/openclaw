import subprocess

node_exe = r"C:\Program Files\nodejs\node.exe"
command = [node_exe, "scripts/run-node.mjs", "usage"]

try:
    res = subprocess.run(command, capture_output=True, text=False)
    stdout = res.stdout.decode('utf-8', errors='ignore')
    stderr = res.stderr.decode('utf-8', errors='ignore')
    
    with open("usage_output.txt", "w", encoding="utf-8") as f:
        f.write("STDOUT:\n")
        f.write(stdout)
        f.write("\nSTDERR:\n")
        f.write(stderr)
    
    print("Done. Output written to usage_output.txt")
except Exception as e:
    print(f"Error: {e}")
