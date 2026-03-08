import os
p = r"c:\Work Space\BellStudios\Frontend\templates"
if os.path.exists(p):
    print(os.listdir(p))
