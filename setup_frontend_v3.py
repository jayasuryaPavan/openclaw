import subprocess
import os

def setup_frontend():
    frontend_dir = r"c:\Work Space\BellStudios\Frontend"
    os.chdir(frontend_dir)
    
    node_dir = r"C:\Program Files\nodejs"
    npm_path = os.path.join(node_dir, "npm.cmd")
    
    # Update environment PATH
    env = os.environ.copy()
    env["PATH"] = node_dir + os.pathsep + env.get("PATH", "")
    
    try:
        subprocess.run([npm_path, "create", "vite@latest", ".", "--", "--template", "react"], 
                       check=True, input="y\n", text=True, shell=True, env=env)
        print("Frontend scaffolded with Vite/React.")
    except Exception as e:
        print(f"Error scaffolding: {e}")

if __name__ == "__main__":
    setup_frontend()
