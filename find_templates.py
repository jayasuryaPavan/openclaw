import os

def list_templates(root):
    for root, dirs, files in os.walk(root):
        if 'templates' in root.lower():
            print(f"Templates in {root}:")
            for f in files[:5]:
                print(f"  {f}")
            break

list_templates(r"c:\Work Space\BellStudios")
