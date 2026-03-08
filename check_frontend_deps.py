import os

def check_frontend(frontend_path):
    # Check package.json for dependencies
    pkg_path = os.path.join(frontend_path, 'package.json')
    if os.path.exists(pkg_path):
        with open(pkg_path, 'r') as f:
            print(f"Dependencies in frontend:\n{f.read()}")
            
    # Check for api directory
    api_path = os.path.join(frontend_path, 'src', 'api')
    if os.path.exists(api_path):
        print(f"Files in src/api:\n{os.listdir(api_path)}")

if __name__ == "__main__":
    check_frontend(r"c:\Work Space\bell studios\frontend")
