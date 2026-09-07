---
name: i-am-impeccable
description: >-
  Natural-language router for Impeccable design commands: infers intent from
  prompts or alignment briefs, presents up to 3 ELI5 choices, and delegates to
  pbakaus/impeccable only after user confirms. Auto-suggests on UI/design work.
  Use for typography, layout, color, motion, anti-AI-slop, polish, critique,
  audit, shape, craft, live mode, or when user says i_am_impeccable or
  /impeccable without a command name. Router only—does not replace upstream skill.
---

# I Am Impeccable

**Alias:** `i_am_impeccable`  
**Role:** Middle agent — intent inference, ELI5 menu, confirm gate, then delegate to [Impeccable](https://impeccable.style/).

## What

You describe design problems in plain language. This skill picks the right Impeccable command(s), explains each option simply, and **waits for your pick** before anything runs.

## Why

Impeccable has 23 commands across six categories. You should not need to memorize them. The router teaches you by showing **what / why / when** for each pick.

## When

| Trigger | Behavior |
|---------|----------|
| User says **i am impeccable**, **i_am_impeccable**, or attaches this skill | Full router loop |
| User says **/impeccable** without a command name | Full router loop |
| UI/design prompt (hero, layout, typography, slop, polish, etc.) | **Auto-suggest** ELI5 menu — still **must confirm** before execution |
| User names command explicitly (`/impeccable polish`) | Skip router; delegate directly |

## Where

| Artifact | Path |
|----------|------|
| This skill (canonical) | `project-plan/templates/context_methodology/i-am-impeccable/SKILL.md` |
| Command catalog | [commands.md](commands.md) |
| Shared harness | CONSCIENCE.md |
| Upstream Impeccable | `.agents/skills/impeccable/` (after `npx skills add pbakaus/impeccable`) |

---

## How — router procedure

Follow CONSCIENCE.md exactly. Skill-specific additions:

### Preflight

1. Check upstream install:
   - Look for `.agents/skills/impeccable/SKILL.md`.
   - If missing → tell user: `npx skills add pbakaus/impeccable` — **STOP** (no delegation).
2. Read [commands.md](commands.md) for the full 23-command ELI5 table.
3. Scan `PRODUCT.md`, `DESIGN.md` if present — adjust setup recommendations.

### Classify

Use the **Intent → command quick map** in [commands.md](commands.md). Rank top 3 for the user's signals.

**Context boosts:**

| Signal | Boost |
|--------|-------|
| Same-wavelength brief in thread | Match locked IN scope (e.g. "polish only" → no craft) |
| Plan mode | Prefer evaluate/create brief commands over craft |
| "Generic" / "slop" / "AI-looking" | critique, audit, typeset |
| Existing page, small complaint | Refine or Harden — not shape/craft |

### Present + STOP (mandatory)

Never run an Impeccable command, edit UI files, or invoke `npx impeccable detect` until the user confirms.

Example:

```markdown
Sounds like you want a design review before changing the compare page hero.

### Pick one (I won't run anything until you choose)

1. **critique** — "Design report card" — best when something feels off but you're not sure what
2. **typeset** — "Fix fonts and hierarchy" — best if it's mostly typography (Inter, weak headings)
3. **bolder** — "Turn up visual impact" — best if structure is fine but bland

Or name another command / **none of these** / **stop**.
```

Use **AskQuestion** when available (max 3 options + "other").

### Delegate

After user confirms:

1. Read upstream Impeccable skill at `.agents/skills/impeccable/SKILL.md`.
2. Load the command reference: `.agents/skills/impeccable/reference/{command}.md` (e.g. `critique.md`, `polish.md`).
3. Execute **only** that command's workflow — do not duplicate command bodies in this skill.
4. Summarize outcomes.
5. If a logical next command exists (e.g. critique → polish), present a **new** confirm round — no auto-chains.

### Verify

- State which command ran and why it matched the user's pick.
- Note any setup gaps (`PRODUCT.md`, `DESIGN.md`) for future sessions.
- Suggest **session-handoff** if stopping mid-design work.

---

## Guardrails (non-negotiable)

1. **No execution before confirm** — absolute.
2. **Max 3 recommendations** + escape hatch every time.
3. **No command chains** without per-step confirm.
4. **Fail closed** — low confidence → one clarifying question, not a guess.
5. **Router only** — never reimplement Impeccable command logic here.
6. **Bounded re-presentation** — max 2 menu rounds, then ask user to type intent.
7. **Cite signals** — "you said hero + generic → critique".

---

## Relationship to other methodology skills

| Skill | When relative to this router |
|-------|------------------------------|
| **same-wavelength** | Run **before** big new UI if scope fuzzy; router reads alignment brief |
| **senior-stable-delivery** | Run **after** design command if implementing backend/tests |
| **session-handoff** | Run when pausing mid-design iteration |

---

## Install (one-time per repo)

```bash
npx skills add pbakaus/impeccable
```

Update upstream periodically:

```bash
npx impeccable skills update
```

This router skill is copied separately into `context_methodology/` — it is **not** installed by the command above.

---

## What this is not

- Not a replacement for Impeccable — install upstream separately.
- Not auto-execution on design prompts — always confirm first.
- Not Laravel/backend work — pair with **senior-stable-delivery** for code changes outside UI design commands.
