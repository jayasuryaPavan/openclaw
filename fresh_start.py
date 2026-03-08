import os
import shutil

def fresh_start():
    root = r"c:\Work Space\BellStudios"
    archive_dir = os.path.join(root, "Archive_Legacy")
    
    if not os.path.exists(archive_dir):
        os.makedirs(archive_dir)
    
    items = os.listdir(root)
    for item in items:
        if item == "Archive_Legacy" or item == ".git":
            continue
        
        src = os.path.join(root, item)
        dst = os.path.join(archive_dir, item)
        try:
            shutil.move(src, dst)
        except Exception as e:
            print(f"Error moving {item}: {e}")

    # Create new structure
    os.makedirs(os.path.join(root, "Backend"))
    os.makedirs(os.path.join(root, "Frontend"))
    
    print("Cleaned and initialized fresh structure.")

if __name__ == "__main__":
    fresh_start()
