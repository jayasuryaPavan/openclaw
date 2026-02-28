import os
import subprocess

def main():
    paths = os.environ.get("PATH", "").split(os.pathsep)
    for path in paths:
        exe = os.path.join(path, "ffmpeg.exe")
        if os.path.exists(exe):
            print(f"Found ffmpeg at: {exe}")
            return
    print("ffmpeg.exe not found in PATH")

if __name__ == "__main__":
    main()
