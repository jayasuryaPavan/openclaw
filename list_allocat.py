import os
p = r"c:\Work Space\Allocat"
if os.path.exists(p):
    print(os.listdir(p))
