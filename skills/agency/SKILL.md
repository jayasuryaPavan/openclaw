---
name: agency
description: Collaborate with the GURU A2A Orchestrator for complex software development tasks using specialized agents.
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
            "description": "Delegate a complex multi-step coding task to the GURU orchestrator.",
            "parameters":
              {
                "type": "object",
                "properties":
                  {
                    "workflow":
                      {
                        "type": "string",
                        "description": "Comma-separated list of agents to use. Options: coder, tester, documenter. Usually 'coder,tester,documenter'.",
                        "default": "coder,tester,documenter"
                      },
                    "task":
                      {
                        "type": "string",
                        "description": "Detailed description of the programming task to perform.",
                      },
                  },
                "required": ["workflow", "task"],
              },
            "cmd": "python delegate_task.py '{{workflow}}' '{{task}}'",
          },
      }
  }
---

# Freelancer Agency (GURU)

Use this skill to delegate complex coding, testing, and documentation tasks to the standalone GURU A2A Orchestrator running on port 12345.

## Usage

Run the python script `delegate_task.py` located in this skill's directory.

```bash
python delegate_task.py [workflow_csv] [task description]
```

## Workflows

The workflow is a comma-separated list of agents you want to run sequentially. Available agents:

*   **coder**: Writes Python code based on requirements.
*   **tester**: Writes pytest tests for the code.
*   **documenter**: Writes a README.md explaining the code.

Examples:
*   Full Pipeline: `python delegate_task.py coder,tester,documenter "Write a snake game in python"`
*   Just Coding: `python delegate_task.py coder "Build a JWT verifier"`
*   Code + Tests: `python delegate_task.py coder,tester "Create a quicksort function"`

## Behavior

*   The command sends an A2A task via JSON-RPC to **GURU Orchestrator** running on `localhost:12345`.
*   The orchestrator runs the specified workflow in the background. Artifacts are saved to `guru/data/artifacts/[task_id]`.
*   Do NOT wait for GURU to finish. It runs asynchronously.
*   Tell the user "I have delegated this task to the GURU orchestrator." and provide them with the Task ID output by the script so they can track it on the dashboard.
