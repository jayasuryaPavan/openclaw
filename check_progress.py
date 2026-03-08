import os

def check_structure():
    root = r"c:\Work Space\BellStudios"
    print(f"Backend Files: {os.listdir(os.path.join(root, 'Backend'))}")
    print(f"Frontend Files: {os.listdir(os.path.join(root, 'Frontend'))}")
    
    # Check if logic exists in apps
    apps_dir = os.path.join(root, 'Backend', 'apps')
    for app in ['users', 'bookings', 'resources', 'payments']:
        app_path = os.path.join(apps_dir, app)
        if os.path.exists(app_path):
            print(f"App {app} files: {os.listdir(app_path)}")

if __name__ == "__main__":
    check_structure()
