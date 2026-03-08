import subprocess
import os

def main():
    git_exe = r"C:\Program Files\Git\cmd\git.exe"
    try:
        os.chdir(r"C:\Workspace\Classyy")
        res = subprocess.run([git_exe, "status"], capture_output=True, text=True)
        print(res.stdout)
        print(res.stderr)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
