import os

def list_deep(startpath, depth=3):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        if level > depth:
            continue
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files[:5]:
            print('{}{}'.format(subindent, f))

if __name__ == "__main__":
    list_deep(r"c:\Work Space\bell studios\services\auth-service")
