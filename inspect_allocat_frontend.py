import os
path = r"c:\Work Space\Allocat\Frontend\package.json"
if os.path.exists(path):
    with open(path, 'r') as f:
        print(f.read())
else:
    print("Not found")
