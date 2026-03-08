import subprocess
res = subprocess.run([r"C:\Program Files\nodejs\node.exe", r"C:\Users\jayas\clawd\skills\antigravity-quota\check-quota.js"], capture_output=True)
print(res.stdout.decode('utf-8', errors='ignore'))
print(res.stderr.decode('utf-8', errors='ignore'))
