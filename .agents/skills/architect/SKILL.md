---
name: architect
description: Plan before you build. Every time.
use_case: Planning, Architecture
---

# /architect

## What it does
`/architect` reads your context files, asks focused questions one at a time, surfaces the decisions you haven't made yet, and produces a plan. It's the conversation you should be having before every serious feature, and now it happens automatically.

## When to run it
Before any feature that involves complex logic, multiple systems talking to each other, or decisions that are hard to reverse. If you're unsure, run it. The two minutes it takes is nothing compared to an afternoon of refactoring.

## Protocol for the AI Agent
1. **Pause execution.** Do NOT write any code yet.
2. Read the project's context files.
3. Ask the user focused clarifying questions, **one at a time**.
4. Explicitly highlight any decisions the user has not yet made (e.g., auth methods, database schema choices).
5. Produce a comprehensive implementation plan.
6. **Wait for approval.** The plan is a starting point, and the user must explicitly approve it before implementation begins.

## Example Prompts
- `/architect feature 12`
- `Check @context/library-docs.md for the Browserbase patterns, then /architect feature 13.`
