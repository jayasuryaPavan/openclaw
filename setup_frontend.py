import subprocess
import os

def setup_frontend():
    frontend_dir = r"c:\Work Space\BellStudios\Frontend"
    os.chdir(frontend_dir)
    
    # Create vite app non-interactively
    # Note: using 'npx' might be safer
    try:
        subprocess.run(["npm", "create", "vite@latest", ".", "--", "--template", "react"], check=True, input="y\n", text=True)
        print("Frontend scaffolded with Vite/React.")
    except Exception as e:
        print(f"Error scaffolding: {e}")

if __name__ == "__main__":
    setup_frontend()
