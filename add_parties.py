import subprocess
import os
import shutil

def add_parties_app():
    backend_dir = r"c:\Work Space\BellStudios\Backend"
    os.chdir(backend_dir)
    
    subprocess.run(["python", "manage.py", "startapp", "parties"], check=True)
    app_dir = os.path.join(backend_dir, "apps")
    shutil.move(os.path.join(backend_dir, "parties"), os.path.join(app_dir, "parties"))
    print("Parties app added.")

if __name__ == "__main__":
    add_parties_app()
