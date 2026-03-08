import subprocess
res = subprocess.run([r"C:\Program Files\nodejs\node.exe", r"C:\Users\jayas\clawd\skills\antigravity-quota\check-quota.js"], capture_output=True, text=True)
print(res.stdout)
print(res.stderr)
