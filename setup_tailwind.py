import subprocess
import os

def setup_tailwind():
    frontend_dir = r"c:\Work Space\BellStudios\Frontend"
    os.chdir(frontend_dir)
    
    node_dir = r"C:\Program Files\nodejs"
    npm_path = os.path.join(node_dir, "npm.cmd")
    npx_path = os.path.join(node_dir, "npx.cmd")
    
    env = os.environ.copy()
    env["PATH"] = node_dir + os.pathsep + env.get("PATH", "")
    
    try:
        # Install tailwind
        subprocess.run([npm_path, "install", "-D", "tailwindcss", "postcss", "autoprefixer"], check=True, env=env, shell=True)
        # Initialize tailwind
        subprocess.run([npx_path, "tailwindcss", "init", "-p"], check=True, env=env, shell=True)
        print("Tailwind installed and initialized.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    setup_tailwind()
