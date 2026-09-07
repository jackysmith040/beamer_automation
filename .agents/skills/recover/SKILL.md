---
name: recover
description: When things break, diagnose first, fix fast.
use_case: Debugging, Error Resolution
---

# /recover

## What it does
`/recover` diagnoses which failure mode you're in and gives you the right corrective response. There are three common failure modes: a targeted bug, a polluted context, or a wrong assumption from earlier. `/recover` figures out which one it is and fixes it. One prompt instead of an afternoon of spiraling.

## When to run it
When something is completely broken and `/review` didn't fix it. When you've tried one corrective prompt and it didn't work. When you have a specific terminal error you need diagnosed. 
*Golden Rule: If the same problem persists after one corrective prompt, stop immediately and run `/recover`.*

## Protocol for the AI Agent
1. Read the raw terminal error log provided by the user. Do not accept paraphrased errors.
2. Diagnose the root cause by mapping the error to one of the three failure modes:
   - Targeted Bug (Syntax/Logic)
   - Polluted Context (State mismatch)
   - Wrong Assumption (Architecture flaw)
3. Explain the exact diagnosis to the user.
4. Provide the definitive, single-shot fix.

## Example Prompts
- `/recover [paste exact terminal error here]`
- `/recover Feature 13 is not persisting data. After saving, the DB still shows the field as null. POST /api/agent/research is either not being called or failing silently.`
