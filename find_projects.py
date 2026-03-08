import os

def find_project_dirs(root_dir):
    project_keywords = ['bell', 'studios', 'classyy', 'allocat']
    found_dirs = []
    
    try:
        # Check Work Space first
        for item in os.listdir(root_dir):
            full_path = os.path.join(root_dir, item)
            if os.path.isdir(full_path):
                if any(keyword in item.lower() for keyword in project_keywords):
                    found_dirs.append(full_path)
                    
        # Check for Antigravity-related workspaces if any
        user_path = r"C:\Users\jayas"
        for item in os.listdir(user_path):
            if item.startswith('.') and 'claw' in item:
                full_path = os.path.join(user_path, item)
                if os.path.isdir(full_path):
                    # Look deeper in typical workspace locations
                    ws_path = os.path.join(full_path, 'workspace')
                    if os.path.exists(ws_path):
                        for sub in os.listdir(ws_path):
                            if any(keyword in sub.lower() for keyword in project_keywords):
                                found_dirs.append(os.path.join(ws_path, sub))
    except Exception as e:
        print(f"Error: {e}")
        
    return found_dirs

if __name__ == "__main__":
    work_space = r"c:\Work Space"
    projects = find_project_dirs(work_space)
    if projects:
        for p in projects:
            print(p)
    else:
        print("No project directories found with keywords.")
