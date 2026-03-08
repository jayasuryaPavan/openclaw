import subprocess
res = subprocess.run([r"C:\Program Files\nodejs\node.exe", r"C:\Users\jayas\clawd\skills\antigravity-quota\check-quota.js"], capture_output=True)
with open("quota_result.txt", "w", encoding="utf-8") as f:
    f.write(res.stdout.decode('utf-8', errors='ignore'))
