import subprocess
import os

def install_frontend():
    frontend_dir = r"c:\Work Space\BellStudios\Frontend"
    os.chdir(frontend_dir)
    
    node_dir = r"C:\Program Files\nodejs"
    npm_path = os.path.join(node_dir, "npm.cmd")
    
    env = os.environ.copy()
    env["PATH"] = node_dir + os.pathsep + env.get("PATH", "")
    
    try:
        # npm install
        subprocess.run([npm_path, "install"], check=True, env=env, shell=True)
        # Install axios for API calls
        subprocess.run([npm_path, "install", "axios"], check=True, env=env, shell=True)
        print("Frontend dependencies installed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    install_frontend()
