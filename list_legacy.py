import os

def list_legacy_apps():
    legacy_root = r"c:\Work Space\BellStudios\Archive_Legacy\Backend\apps"
    if os.path.exists(legacy_root):
        print(f"Legacy Apps: {os.listdir(legacy_root)}")
        for app in ['users', 'bookings', 'resources', 'payments']:
            app_path = os.path.join(legacy_root, app)
            if os.path.exists(app_path):
                print(f"Legacy {app} models: {os.listdir(app_path)}")
    else:
        print("Legacy apps not found.")

list_legacy_apps()
