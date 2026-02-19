---
name: multi-agent-workflow
description: Multi-agent collaboration system for software development tasks. Use when you need to coordinate specialized agents (Reasoner, Developer, Tester) to handle coding, testing, and documentation tasks. Implements the workflow: User → Reasoner (task analysis) → Specialist Agent → Documentation.
---

# Multi-Agent Workflow Skill

This skill implements a multi-agent collaboration system for software development tasks within OpenClaw. The system consists of three specialized agents that work together through a shared workspace.

## Agent Types

### 1. Reasoner Agent
- **Model**: deepseek/deepseek-reasoner
- **Role**: Analyze incoming user requests, determine task type, route to appropriate specialist agent
- **Responsibilities**:
  - Task classification (coding, testing, documentation, other)
  - Context management
  - Agent coordination
  - Workflow orchestration

### 2. Developer Agent
- **Model**: deepseek/deepseek-coder (or deepseek/deepseek-chat if coder unavailable)
- **Role**: Handle coding tasks and create developer documentation
- **Responsibilities**:
  - Write implementation code in appropriate languages
  - Create comprehensive developer documentation (dev-doc.md)
  - Store output in shared workspace
  - Follow coding standards and best practices

### 3. Tester Agent
- **Model**: deepseek/deepseek-reasoner
- **Role**: Perform testing on developed code and create test documentation
- **Responsibilities**:
  - Read developer documentation (dev-doc.md)
  - Design and execute test cases
  - Create test documentation (test-doc.md)
  - Report bugs/issues back to Developer Agent

## Workflow

```
User Message → Reasoner Agent → Task Classification → Specialist Agent Selection → Agent Execution → Documentation Storage → Result Return
```

### Shared Workspace Structure
```
workspace/
├── tasks/          # Incoming task descriptions
├── dev-docs/       # Developer documentation (dev-doc.md files)
├── test-docs/      # Test documentation (test-doc.md files)
├── code/           # Generated code files
└── logs/           # Agent activity logs
```

## Implementation Guide

### 1. Setup Shared Workspace
Create the workspace directory structure if it doesn't exist:

```bash
mkdir -p workspace/{tasks,dev-docs,test-docs,code,logs}
```

### 2. Reasoner Agent Logic
The Reasoner agent should:
- Analyze user input for task type keywords
- Determine if task is coding, testing, or other
- Spawn appropriate specialist agent using `sessions_spawn`
- Monitor agent progress and handle coordination

### 3. Agent Spawning Patterns

#### Spawning Developer Agent
```javascript
sessions_spawn({
  task: "Write code for: [task description]. Create developer documentation in dev-docs/. Store code in code/.",
  label: "developer-agent",
  model: "deepseek/deepseek-coder",
  thinking: "high"
})
```

#### Spawning Tester Agent
```javascript
sessions_spawn({
  task: "Test the code described in dev-docs/[filename].md. Create test documentation in test-docs/. Report any issues.",
  label: "tester-agent", 
  model: "deepseek/deepseek-reasoner",
  thinking: "high"
})
```

### 4. Documentation Templates

#### dev-doc.md Template
```markdown
# Developer Documentation

## Task
[Task description]

## Implementation
[Code implementation details]

## Files Created
- `code/[filename].ext`: [Description]

## Dependencies
- [List of dependencies]

## Setup Instructions
[How to setup/run the code]

## Architecture Decisions
[Key decisions and reasoning]
```

#### test-doc.md Template
```markdown
# Test Documentation

## Tested Component
[Component name from dev-doc]

## Test Cases
1. [Test case 1]
   - Expected: 
   - Actual:
   - Result: Pass/Fail

## Issues Found
- [Issue 1 with severity]
- [Issue 2 with severity]

## Test Coverage
[Coverage metrics if available]

## Recommendations
[Suggestions for improvements]
```

## Usage Examples

### Example 1: Simple Coding Task
**User**: "Write a Python function to calculate factorial"

**Reasoner Analysis**: Coding task → spawn Developer Agent

**Developer Agent**: Creates factorial.py and dev-doc.md

**Tester Agent**: (optional) Can be spawned to test the function

### Example 2: Testing Request
**User**: "Test the authentication module"

**Reasoner Analysis**: Testing task → spawn Tester Agent

**Tester Agent**: Reads existing dev-doc for auth module, creates test-doc.md

### Example 3: Full Development Cycle
**User**: "Build a todo app with React"

**Reasoner Analysis**: Complex coding task → spawn Developer Agent with phased approach

**Developer Agent**: Creates components, dev-doc

**Tester Agent**: (auto-spawned or manual) Tests components

## Coordination Patterns

### 1. Sequential Coordination
Developer completes → Reasoner spawns Tester with reference to dev-doc

### 2. Parallel Coordination
For large tasks, multiple Developer agents can work on different components simultaneously

### 3. Feedback Loop
Tester finds issues → Reasoner spawns Developer with bug fix task

## Best Practices

1. **Clear Task Descriptions**: Provide specific, actionable tasks to spawned agents
2. **Workspace Organization**: Keep files well-organized in the workspace structure
3. **Documentation Links**: Reference relevant documentation files in agent tasks
4. **Progress Monitoring**: Check on spawned agents periodically
5. **Error Handling**: Handle cases where spawned agents fail or get stuck

## Troubleshooting

### Common Issues

1. **Agent fails to spawn**: Check model availability and session limits
2. **Documentation not found**: Verify file paths in shared workspace
3. **Task misclassification**: Improve Reasoner's classification logic
4. **Coordination failures**: Implement better state tracking

## Extension Points

The system can be extended with additional agent types:
- **Documentation Agent**: Specializes in creating user-facing documentation
- **DevOps Agent**: Handles deployment and infrastructure tasks
- **Review Agent**: Performs code review and quality assessment

---

**Note**: This skill provides the framework and patterns. Actual implementation requires adapting to specific OpenClaw configuration and available models.