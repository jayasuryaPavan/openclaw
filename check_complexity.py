import os

def check_views_complexity(root):
    for root, dirs, files in os.walk(root):
        if 'views.py' in files:
            path = os.path.join(root, 'views.py')
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                if len(lines) > 300:
                    print(f"HIGH COMPLEXITY: {path} ({len(lines)} lines)")
                
                # Check for direct DB queries without select_related
                if '.objects.filter' in content and 'select_related' not in content and 'prefetch_related' not in content:
                    print(f"POTENTIAL N+1: {path}")

check_views_complexity(r"C:\Workspace\Classyy\Backend\apps")
