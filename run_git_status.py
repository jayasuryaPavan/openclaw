import subprocess
import os

def main():
    try:
        os.chdir(r"C:\Workspace\Classyy")
        res = subprocess.run(["git", "status"], capture_output=True, text=True)
        print("STDOUT:")
        print(res.stdout)
        print("STDERR:")
        print(res.stderr)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
