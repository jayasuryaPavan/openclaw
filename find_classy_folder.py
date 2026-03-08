import os

def find_classy(root):
    matches = []
    for root, dirs, files in os.walk(root):
        if 'classy' in root.lower() or any('classy' in d.lower() for d in dirs):
            matches.append(root)
        if len(matches) > 10: break
    return matches

print(find_classy(r"c:\Work Space"))
