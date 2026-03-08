import os
apps_path = r"c:\Work Space\BellStudios\Backend\apps"
if os.path.exists(apps_path):
    print(os.listdir(apps_path))
else:
    print("Not found")
