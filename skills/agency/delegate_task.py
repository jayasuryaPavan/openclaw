import sys
import json
import urllib.request
import urllib.error

API_URL = "http://localhost:12345/assign"

def delegate_task(role, task_description):
    """Send task to Agency Manager."""
    data = {
        "role": role,
        "task": task_description
    }
    
    try:
        req = urllib.request.Request(
            API_URL, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            print(json.dumps(result, indent=2))
            return 0
    except urllib.error.URLError as e:
        print(f"Error connecting to Agency Manager: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python delegate_task.py <role> <task_description>")
        print("Roles: coder, tester, documenter")
        sys.exit(1)
        
    role = sys.argv[1]
    task = " ".join(sys.argv[2:])
    
    sys.exit(delegate_task(role, task))
