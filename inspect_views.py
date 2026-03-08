import os

def find_views(root):
    for root, dirs, files in os.walk(root):
        if 'views.py' in files:
            print(f"Views in {root}:")
            # Read first 50 lines of views.py
            try:
                with open(os.path.join(root, 'views.py'), 'r') as f:
                    lines = f.readlines()
                    print("".join(lines[:30]))
            except:
                pass
            print("-" * 30)

find_views(r"c:\Work Space\BellStudios\Backend\apps")
