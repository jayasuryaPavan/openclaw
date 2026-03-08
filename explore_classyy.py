import os

def list_deep(startpath, depth=2):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        if level > depth:
            continue
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files[:10]:
            print('{}{}'.format(subindent, f))
        if len(files) > 10:
            print('{}... ({} more files)'.format(subindent, len(files)-10))
        if level == depth:
            dirs[:] = []

if __name__ == "__main__":
    list_deep(r"C:\Workspace\Classyy")
