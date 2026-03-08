import subprocess
import re

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

node_exe = r"C:\Program Files\nodejs\node.exe"
command = [node_exe, "scripts/run-node.mjs", "status", "--deep"]

try:
    res = subprocess.run(command, capture_output=True, text=False)
    stdout = res.stdout.decode('utf-8', errors='ignore')
    stderr = res.stderr.decode('utf-8', errors='ignore')
    
    clean_stdout = strip_ansi(stdout)
    clean_stderr = strip_ansi(stderr)
    
    print("STDOUT:")
    print(clean_stdout)
    print("STDERR:")
    print(clean_stderr)
except Exception as e:
    print(f"Error: {e}")
