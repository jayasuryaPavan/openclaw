import subprocess
import os

def setup_frontend():
    frontend_dir = r"c:\Work Space\BellStudios\Frontend"
    os.chdir(frontend_dir)
    
    npm_path = r"C:\Program Files\nodejs\npm.cmd"
    
    # Create vite app non-interactively using 'npm create'
    # The command is: npm create vite@latest . -- --template react
    try:
        # On Windows, we often need shell=True for .cmd files
        subprocess.run([npm_path, "create", "vite@latest", ".", "--", "--template", "react"], 
                       check=True, input="y\n", text=True, shell=True)
        print("Frontend scaffolded with Vite/React.")
    except Exception as e:
        print(f"Error scaffolding: {e}")

if __name__ == "__main__":
    setup_frontend()
