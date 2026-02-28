#!/usr/bin/env python3
import sys
import json
import os

# Mock vision script for Panda Chat Vision Core

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No image file provided"}))
        return

    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(json.dumps({"error": f"File not found: {image_path}"}))
        return

    filename = os.path.basename(image_path).lower()
    
    # Mock analysis based on context
    if "vscode" in filename:
        description = "A screenshot of Visual Studio Code editor showing some Python scripts."
    elif "latest" in filename:
        description = "A system screenshot showing open windows and the taskbar."
    else:
        description = "Visual data analyzed. [Mock Analysis]"
        
    result = {
        "file": image_path,
        "description": description,
        "objects": ["window", "text", "editor"],
        "model": "Panda-Vision-v1 (Mock)"
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
