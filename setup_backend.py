import subprocess
import os

def setup_backend():
    backend_dir = r"c:\Work Space\BellStudios\Backend"
    os.chdir(backend_dir)
    
    # Start project
    subprocess.run(["python", "-m", "django", "startproject", "core", "."], check=True)
    
    # Create apps
    apps = ["users", "bookings", "resources", "payments"]
    for app in apps:
        subprocess.run(["python", "manage.py", "startapp", app], check=True)
        # Move apps to an 'apps' folder for better organization
        app_dir = os.path.join(backend_dir, "apps")
        if not os.path.exists(app_dir):
            os.makedirs(app_dir)
        
        shutil.move(os.path.join(backend_dir, app), os.path.join(app_dir, app))

    print("Backend initialized with core and apps.")

if __name__ == "__main__":
    import shutil
    setup_backend()
