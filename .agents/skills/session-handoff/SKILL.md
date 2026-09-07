---
name: session-handoff
description: >-
  End-of-session compact handoff for human skim and next agent: relevance filter
  removes noise, keeps decisions/state/next actions. Tiered like Cursor/Claude
  continuation—a paste block plus optional HANDOFF.md. Invoke when stopping
  mid-task or switching chats.
---

# Session Handoff

## What

A **relevance-filtered snapshot** of the session so the next human or agent can continue **without context pollution**—not a transcript dump.

Modeled after how **Cursor** and **Claude** continue work: tight executive context, explicit next actions, no tool spam or abandoned explorations.

## Why

| Dump entire chat | Handoff |
|------------------|---------|
| Token waste | ~paste block + optional file |
| Dead ends confuse next agent | Only paths that matter now |
| Decisions buried | Locked decisions up front |
| “What was I doing?” | Current state + next 3 actions |

## When

- User says **handoff**, **continue later**, or ends a long session mid-ticket.
- Before switching to a **new chat** in the same repo.
- After a milestone (tests green, PR ready) even if not merging yet.

**Do not** handoff on trivial one-shot Q&A with no ongoing work.

## Where

**Tiered output (always both layers when handoff runs):**

| Layer | Format | Audience |
|-------|--------|----------|
| **A — Paste block** | Markdown, **≤ ~120 lines** or ~800–1.2k tokens | New chat system/user preamble |
| **B — File** | `HANDOFF.md` (repo root) or `project-plan/handoff/latest.md` | Human skim + agent file read |

Overwrite `latest.md` each handoff; optional dated archive `handoff/YYYY-MM-DD-HHmm.md` if user asks.

---

## Relevance filter (strict)

### INCLUDE

- **Objective** — what we’re trying to finish (one sentence).
- **Locked decisions** — from alignment brief or Rabit (table or bullets).
- **Current state** — branch, ticket id, % done, what works vs not.
- **Files touched** — paths only, grouped by role (not full diffs).
- **Tests** — last command, pass/fail, failing test names if any.
- **Blockers** — env, API keys, human approval, CI.
- **Next actions** — ordered, max **5**, each actionable in one session.
- **Explicit rejects** — creep items deferred (prevents re-proposal).

### EXCLUDE (noise)

- Full tool call logs, MCP schemas, search result dumps.
- Failed approaches unless the failure **informs** the next step.
- Large code blocks — pointer to file:line only.
- Generic framework tutorials, AGENTS.md wholesale paste.
- Plan file verbatim — summarize deltas only.
- Repeated context from earlier in chat already in repo docs.

**Compression tactic:** If it’s in git diff or `spec/00N.md`, **reference the path**, don’t repeat content.

---

## Paste block template (Layer A)

```markdown
## HANDOFF — {project} — {ticket or topic}
**Status:** {in progress | blocked | ready for PR | done}
**Branch:** {name or unknown}

### Objective
{one sentence}

### Locked decisions
- ...

### Current state
{2–5 bullets: what was implemented, what was not}

### Files (high signal)
- `path` — {why}

### Tests
- Last: `{command}` → {pass | fail: test names}

### Blockers
- {none | list}

### Next session (do these first)
1. ...
2. ...
3. ...

### Out of scope / rejected this session
- ...

### Skills for next agent
- senior-stable-delivery (implement/review)
- same-wavelength (only if scope still fuzzy)
- i-am-impeccable (if mid-design iteration)
```

---

## HANDOFF.md template (Layer B)

Same sections as Layer A, plus optional:

```markdown
### Context pointers (read first)
- `{spec ticket path}`
- `{decisions.md or AGENTS.md}`

### Open questions (need human)
- ...

### Rabit status
- Plan audit: {done | N/A}
- Pre-PR audit: {pending | done — link to RABIT-AUDIT file}
```

---

## How — agent procedure

1. **Scan** session for decisions, final state, not abandoned drafts.
2. **Apply filter** — drop excluded categories aggressively.
3. **Write Layer A** — user can copy-paste into new chat.
4. **Write Layer B** — save to agreed path; tell user the path.
5. **One line close:** “Paste block above into next chat; optional file at `{path}`.”

If git is available, prefer `git status` / branch name for accuracy—do not invent branch names.

---

## Quality bar

- Next agent should answer **“what do I do first?”** in **30 seconds**.
- Human should see **no paragraph longer than 3 lines** in the paste block.
- If handoff exceeds size cap, **cut examples first**, never cut decisions or next actions.

---

## Relationship to other skills

| Skill | When relative to handoff |
|-------|-------------------------|
| **same-wavelength** | Ran earlier → decisions appear under Locked decisions |
| **senior-stable-delivery** | Ongoing → Rabit/test status in handoff |
| **i-am-impeccable** | Mid-design → note last confirmed Impeccable command |
| **session-handoff** | **Last** step of session |

---

## Intelligent routing

Follow the State 2 Intent Classification in `CONSCIENCE.md` when handoff depth is ambiguous.

**User-invoked only** — run when user says handoff or ends a long session.

### Routing catalog — handoff depth

| Mode | ELI5 | Pick when | Skip when |
|------|------|-----------|-----------|
| **paste-only** | Copy-paste block in chat | Quick context switch; no file needed | User wants file for next agent |
| **paste-and-file** | Paste block + `project-plan/handoff/latest.md` | Default for this repo; next agent should read file | Trivial Q&A with no ongoing work |
| **archive** | paste-and-file + dated copy | User asks to keep history | One-off handoff |

### Procedure

1. **Mirror** what work remains unfinished.
2. If user said **paste only** or **save to file** → skip menu.
3. Else **present + STOP** — max 3 depth options; wait for pick.
4. Apply relevance filter; write Layer A (always); Layer B per mode.
5. One-line close with file path if written.

### Guardrails

- Never dump transcript — unchanged.
- paste-only still includes full paste block template — just skips file write.
- Cite signal: "you said switching chats → paste-and-file".
