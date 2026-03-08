import os
for root, dirs, files in os.walk('.'):
    for file in files:
        if 'quota' in file.lower():
            print(os.path.join(root, file))
