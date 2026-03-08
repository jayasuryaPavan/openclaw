import os
matches = []
for root, dirs, files in os.walk('c:\\Work Space'):
    for file in files:
        if 'quota' in file.lower() or 'check' in file.lower():
            matches.append(os.path.join(root, file))
print("\n".join(matches[:20]))
