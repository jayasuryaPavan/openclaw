import shutil
import os
import subprocess

node_path = shutil.which("node")
print(f"Node path: {node_path}")

if node_path:
    try:
        # Try to run node and capture output
        res = subprocess.run([node_path, "scripts/run-node.mjs", "status", "--deep"], capture_output=True, text=True)
        print("STDOUT:")
        print(res.stdout)
        print("STDERR:")
        print(res.stderr)
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Node not found in PATH")
