import os

def search_classy_files(root):
    for root, dirs, files in os.walk(root):
        for f in files:
            if 'classy' in f.lower():
                print(os.path.join(root, f))
        if 'classy' in root.lower():
            print(f"FOLDER: {root}")

search_classy_files(r"c:\Work Space\BellStudios")
