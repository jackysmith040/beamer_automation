---
name: imprint
description: Keep your UI consistent across every session.
use_case: UI Consistency, Design Systems
---

# /imprint

## What it does
`/imprint` captures the new component's pattern into your UI registry. Run it across the codebase and it finds inconsistencies and produces a fix list. Your design system stays coherent across every session, without you having to explain it every time.

## When to run it
After building any new UI component or page. Especially important when starting a new page that needs to match patterns established in previous sessions. If you're ever unsure whether a new component matches the existing design system, run `/imprint`.

## Protocol for the AI Agent
1. Analyze the newly created UI component (HTML, CSS classes, structure).
2. Capture this established pattern and write it automatically to `ui-registry.md`.
3. (Optional) If requested, scan existing components in the repository and flag any that do not match the newly established UI tokens or layouts in the registry.

## Example Prompts
- `/imprint`
