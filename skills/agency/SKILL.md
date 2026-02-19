---
name: agency
description: Collaborate with specialized AI agents (Coder, Tester, Documenter) for complex software development tasks.
metadata:
  {
    "openclaw":
      {
        "emoji": "🏢",
        "requires": { "bins": ["python"] }
      },
    "tools":
      {
        "agency":
          {
            "description": "Delegate a complex task to a specialized background agent.",
            "parameters":
              {
                "type": "object",
                "properties":
                  {
                    "role":
                      {
                        "type": "string",
                        "enum": ["coder", "tester", "documenter", "computer_user"],
                        "description": "The agent role/specialization.",
                      },
                    "task":
                      {
                        "type": "string",
                        "description": "Detailed description of the task to perform.",
                      },
                  },
                "required": ["role", "task"],
              },
            "cmd": "python delegate_task.py '{{role}}' '{{task}}'",
          },
      }
  }
---

# Freelancer Agency

Use this skill to delegate complex coding, testing, and documentation tasks to specialized background agents.

## Usage

Run the python script `delegate_task.py` located in this skill's directory.

```bash
python delegate_task.py [role] [task description]
```

## Roles

*   **coder**: Writes code (Python, etc.) based on requirements.
    *   Example: `python delegate_task.py coder "Write a snake game in python"`
*   **tester**: Writes and runs tests for existing code.
    *   Example: `python delegate_task.py tester "Test the snake game logic"`
*   **documenter**: Writes documentation (README.md) for the project.
    *   Example: `python delegate_task.py documenter "Create documentation for the project"`

## Behavior

*   The command sends a request to the **Agency Manager** running on `localhost:12345`.
*   The agent runs in the background and saves output to `workspace/code/` or `workspace/logs/`.
*   Do NOT wait for the agent to finish. It runs asynchronously.
*   Tell the user "I have delegated this task to the [role] agent."
