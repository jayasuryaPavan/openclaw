import os
for root, dirs, files in os.walk(r"C:\Workspace\Classyy"):
    if 'db.sqlite3' in files:
        print(os.path.join(root, 'db.sqlite3'))
