import os
path = r"C:\Users\jayas\.openclaw\media\inbound\file_14---a27168fd-8ce3-4569-8d13-48978b1f863e.ogg"
print(f"Exists: {os.path.exists(path)}")
print(f"Size: {os.path.getsize(path) if os.path.exists(path) else 'N/A'}")
