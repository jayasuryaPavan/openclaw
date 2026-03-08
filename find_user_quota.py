import os
user_path = r"C:\Users\jayas"
for root, dirs, files in os.walk(user_path):
    for file in files:
        if 'quota' in file.lower():
            print(os.path.join(root, file))
    if root.count(os.sep) - user_path.count(os.sep) > 3: # Limit depth
        del dirs[:]
