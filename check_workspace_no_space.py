import os
print(f"C:\\Workspace exists: {os.path.exists('C:\\Workspace')}")
if os.path.exists('C:\\Workspace'):
    print(os.listdir('C:\\Workspace'))
