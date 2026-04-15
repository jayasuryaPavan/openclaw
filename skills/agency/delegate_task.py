import sys
import json
import urllib.request
import urllib.error
import time

API_URL = "http://localhost:12345/a2a"

def delegate_task(workflow_csv, task_description):
    """Send task to GURU A2A Orchestrator."""
    workflow = [w.strip() for w in workflow_csv.split(",")]
    
    payload = {
        "jsonrpc": "2.0",
        "id": int(time.time()),
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": task_description}]
            },
            "metadata": {
                "workflow": workflow
            }
        }
    }
    
    try:
        req = urllib.request.Request(
            API_URL, 
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if "error" in result:
                print(f"GURU Error: {result['error']}")
                return 1
            else:
                task_id = result["result"]["id"]
                print(f"Task successfully submitted to GURU!")
                print(f"Task ID: {task_id}")
                print(f"Workflow: {' -> '.join(workflow)}")
                print(f"Track progress at: http://localhost:12345/dashboard/")
                return 0
    except urllib.error.URLError as e:
        print(f"Error connecting to GURU (is it running on port 12345?): {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python delegate_task.py <workflow_csv> <task_description>")
        print("Example: python delegate_task.py coder,tester \"Build a calculator\"")
        print("Roles available: coder, tester, documenter")
        sys.exit(1)
        
    workflow_csv = sys.argv[1]
    task = " ".join(sys.argv[2:])
    
    sys.exit(delegate_task(workflow_csv, task))
