import subprocess
import os

def run_migrations():
    backend_dir = r"c:\Work Space\BellStudios\Backend"
    os.chdir(backend_dir)
    
    apps = ["users", "parties", "resources", "bookings"]
    
    # Makemigrations
    subprocess.run(["python", "manage.py", "makemigrations"] + apps, check=True)
    
    # Migrate
    subprocess.run(["python", "manage.py", "migrate"], check=True)
    
    print("Database migrations completed.")

if __name__ == "__main__":
    run_migrations()
