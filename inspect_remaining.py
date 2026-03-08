import os
def list_bell_studios():
    root = r"c:\Work Space\BellStudios"
    print(f"Root: {os.listdir(root)}")
    if 'Frontend' in os.listdir(root):
        print(f"Frontend: {os.listdir(os.path.join(root, 'Frontend'))[:20]}")
    if 'Backend' in os.listdir(root):
        print(f"Backend: {os.listdir(os.path.join(root, 'Backend'))[:20]}")

list_bell_studios()
