import os
resume_path = r"c:\Work Space\Resume"
if os.path.exists(resume_path):
    print(os.listdir(resume_path))
else:
    print("Resume folder not found")
