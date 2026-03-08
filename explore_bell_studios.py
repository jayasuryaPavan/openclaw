import os

def list_files(startpath, max_depth=2):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        if level > max_depth:
            continue
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        # Limit number of files displayed
        for f in files[:10]:
            print('{}{}'.format(subindent, f))
        if len(files) > 10:
            print('{}... ({} more files)'.format(subindent, len(files)-10))
        # Stop walking deeper if at max level
        if level == max_depth:
            dirs[:] = []

if __name__ == "__main__":
    print("Listing c:\\Work Space\\bell studios:")
    list_files(r"c:\Work Space\bell studios")
    print("\nListing c:\\Work Space\\BellStudios:")
    list_files(r"c:\Work Space\BellStudios")
