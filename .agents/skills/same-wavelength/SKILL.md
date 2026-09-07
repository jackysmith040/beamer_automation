---
name: same-wavelength
description: >-
  Pre-work alignment grill (stronger than casual clarifying questions): lock
  requirements, architecture tradeoffs, non-goals, risk appetite, and definition
  of done before coding. User-invoked only—say "same wavelength" or attach skill.
  Use before substantial or ambiguous features in any project.
---

# Same Wavelength

## What

A **structured alignment session** before implementation—like a rigorous “grill me,” but oriented toward **shipping safely**, not debate for its own sake.

Output is **written locks**: scope, non-goals, decisions, open questions (resolved or explicitly deferred), and what “done” looks like.

## Why

| Without | With |
|---------|------|
| Agent assumes missing requirements | Ambiguities surface early |
| Architecture chosen mid-coding | Tradeoffs recorded before diff |
| Persona mismatch (speed vs safety) | Risk appetite and tone explicit |
| Creep discovered late | Non-goals listed upfront |

## When

- **Only when the user invokes** — e.g. “same wavelength,” “align with me,” or @-mention this skill.
- **Do not** run on every message or every plan mode entry.
- **Suggested** before: new features, AI surfaces, auth/payments, migrations, multi-file refactors.

**After alignment:** switch to **senior-stable-delivery** for Rabit plan table + implementation pipeline.

## Where

- Produces a short **Alignment brief** (markdown) the user can paste into the ticket or plan.
- Optional file: `project-plan/alignment/YYYY-MM-DD-{slug}.md` if the repo uses `project-plan/`.

---

## How — session flow

### 1. Mirror (1 paragraph)

Restate the user’s goal in plain language. Ask: **“Is this the problem we’re solving?”**

Stop if wrong; do not proceed.

### 2. Grill blocks (use AskQuestion when available)

Ask in **batches of 3** until these blocks are filled. Max ~10 questions total unless user wants deeper.

| Block | Force answers on |
|-------|------------------|
| **Scope** | In / out; MVP vs later; single ticket boundary |
| **Users & context** | Who, environment, constraints (mobile, public, admin) |
| **Architecture** | Data flow, boundaries, what must not couple |
| **Failure & security** | AuthZ, abuse, invalid input, fail-open vs closed |
| **Done** | Verifiable checklist; tests; smoke steps |
| **Persona** | Stability vs speed; creep policy; review depth |

### 3. Challenge pass (senior dev voice)

Push on:

- Hidden assumptions (“we’ll add cache later” → Reject or ticket?)
- Duplicate systems (second way to do the same thing)
- AI/tool temptation without harness boundaries
- Missing non-goals (what stakeholders might *assume* is included)

Use **Ship / Reject / Defer** per idea—not implementation yet.

### 4. Alignment brief (required output)

Use this template:

```markdown
## Alignment brief — {title}
**Date:** {date}
**Problem:** {one sentence}

### Locked IN
- ...

### Locked OUT (non-goals)
- ...

### Decisions
| Topic | Decision | Rationale |
|-------|----------|-----------|

### Risks & mitigations
| Risk | Mitigation |
|------|------------|

### Definition of done
- [ ] ...

### Open questions
- {None — or list with owner}

### Persona sync
- Stability: {high/med}
- Feature creep: {defer unless explicit expand}
- Next skill: senior-stable-delivery → Rabit plan table → implement
```

### 5. Explicit consent

End with: **“Confirm this brief (or edit), then I’ll proceed under senior-stable-delivery.”**

Do **not** write production code until the user confirms—or edits the brief in the same thread.

---

## Rules

1. **Questions before code** — No drive-by implementation during same-wavelength.
2. **Prefer structured choices** — AskQuestion with options when possible; allow “other” via follow-up.
3. **No noise** — Do not recap entire chat history; only deltas and locks.
4. **Defer ≠ reject** — Defer must name a follow-up ticket or phase.
5. **Powerful, not hostile** — Direct challenges, respectful tone; goal is shared truth.

---

## What this is not

- Not a code review (use Rabit pre-PR in senior-stable-delivery).
- Not a handoff (use session-handoff).
- Not automatic—user must invoke.

---

## Intelligent routing

Follow the State 2 Intent Classification in `CONSCIENCE.md` when alignment depth is ambiguous.

**User-invoked only** — do not auto-run on every message. (Design UI work may separately trigger **i-am-impeccable** with its own confirm gate.)

### Routing catalog — alignment depth

| Mode | ELI5 | Pick when | Skip when |
|------|------|-----------|-----------|
| **light** | Quick scope lock (~3 questions) | Small ticket; user named clear boundaries | Auth, payments, migrations, multi-file refactors |
| **standard** | Full grill blocks (default) | New feature; some ambiguity | User already pasted a complete spec |
| **deep** | Standard + extra challenge pass | High risk; AI surfaces; persona mismatch likely | Trivial config change |

### Procedure

1. **Mirror** the goal in one sentence.
2. If user said **light**, **standard**, or **deep** explicitly → skip menu, use that mode.
3. Else **present + STOP** — max 3 depth options with ELI5; wait for pick.
4. Run grill blocks appropriate to depth (light: Scope + Done + Persona only).
5. Produce alignment brief; explicit consent before **senior-stable-delivery**.

### Guardrails

- No production code during alignment — unchanged.
- No skipping consent after brief — unchanged.
- Cite signal: "you said small CSS tweak → light alignment".
