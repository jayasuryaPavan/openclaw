import os

def find_settings(root):
    for root, dirs, files in os.walk(root):
        if 'settings.py' in files:
            print(os.path.join(root, 'settings.py'))

find_settings(r"c:\Work Space\Allocat")
