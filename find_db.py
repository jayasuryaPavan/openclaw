import os
for root, dirs, files in os.walk(r"c:\Work Space\Classyy"):
    if 'db.sqlite3' in files:
        print(os.path.join(root, 'db.sqlite3'))
