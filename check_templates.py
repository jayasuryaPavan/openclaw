import os

def check_templates(root):
    for root, dirs, files in os.walk(root):
        if 'templates' in root:
            for f in files:
                if f.endswith('.html'):
                    path = os.path.join(root, f)
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # Check for hardcoded styles or excessive JS
                        if 'style="' in content:
                            print(f"HARDCODED STYLE: {path}")
                        if '<script>' in content and len(content.split('<script>')) > 2:
                            print(f"EXCESSIVE INLINE JS: {path}")

check_templates(r"C:\Workspace\Classyy\Frontend\templates")
