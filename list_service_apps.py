import os

def list_app_files(service_path):
    # Usually Django projects have 'apps' or the service name as the app
    # Let's find directories inside service_path
    try:
        items = os.listdir(service_path)
        print(f"Service: {os.path.basename(service_path)}")
        for item in items:
            item_path = os.path.join(service_path, item)
            if os.path.isdir(item_path):
                if item not in ['core', 'venv', '__pycache__', 'migrations']:
                    # Look for models.py or apps.py
                    if os.path.exists(os.path.join(item_path, 'models.py')):
                        print(f"  App: {item}")
                        # List some files
                        app_files = os.listdir(item_path)
                        for f in app_files:
                            if not f.startswith('__') and f.endswith('.py'):
                                print(f"    {f}")
        print("-" * 30)
    except Exception as e:
        print(f"Error listing {service_path}: {e}")

if __name__ == "__main__":
    services_root = r"c:\Work Space\bell studios\services"
    for service in os.listdir(services_root):
        service_path = os.path.join(services_root, service)
        if os.path.isdir(service_path):
            list_app_files(service_path)
