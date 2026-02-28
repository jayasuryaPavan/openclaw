import os
common_paths = [
    r"C:\ffmpeg\bin",
    r"C:\Program Files\ffmpeg\bin",
    r"C:\Program Files (x86)\ffmpeg\bin",
    r"C:\Work Space\ffmpeg\bin",
    r"C:\Work Space\Panda Chat\openclaw\ffmpeg\bin"
]
for p in common_paths:
    exe = os.path.join(p, "ffmpeg.exe")
    if os.path.exists(exe):
        print(f"Found ffmpeg at: {exe}")
