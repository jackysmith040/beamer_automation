---
name: remember
description: Never lose context between sessions.
use_case: Session Management, Memory
---

# /remember

## What it does
`/remember` has two modes. 
- `/remember save` compresses what happened in the current session, including decisions made, patterns established, and progress completed, into a memory file. 
- `/remember restore` loads that file at the start of a new session so the agent picks up exactly where you left off.

## When to run it
- **`/remember save`**: Run at the end of every session where real work happened. Especially important when a feature spans multiple sessions.
- **`/remember restore`**: Run at the start of any session that continues work from a previous one. Replaces the need to re-explain what was built.

## Protocol for the AI Agent
### On `/remember save`:
1. Synthesize all key decisions, newly established architectural patterns, and the exact state of progress from the current session.
2. Write this compressed summary to the `memory/` directory as a session state file.

### On `/remember restore`:
1. Immediately read the most recent session state file from the `memory/` directory.
2. Acknowledge the restored context to the user and seamlessly resume the implementation. 
3. *Note: Do not ask the user to explain the project again.*
