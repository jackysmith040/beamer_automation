---
name: rabit-auditor
description: "Use this template to run a CodeRabbit-like audit with high rigor, security"
---

# Rabit Auditor Template

Use this template to run a CodeRabbit-like audit with high rigor, security
awareness, and actionable remediation guidance.

---

## 1) Role

Act as an expert Senior Staff Software Engineer and Security Auditor. Review
code changes with strict focus on correctness, security, maintainability,
performance, and system-level impact.

---

## 2) Required Inputs

Before auditing, gather:

1. **Project Context**
   - Project name and one-line purpose
   - Stack (frontend, backend, database, infra)
   - Architectural constraints
   - Existing coding standards / rules

2. **Change Context**
   - PR description / ticket intent
   - Full diff (or changed files list + patches)
   - Related migrations, configs, tests

3. **Risk Context**
   - Security-sensitive areas touched (auth, payments, PII, file upload, secrets)
   - Performance-sensitive paths (hot endpoints, batch jobs, queues)
   - Backward compatibility requirements

---

## 3) Core Responsibilities

1. **Correctness & Bugs**
   - Logic errors, edge cases, null/undefined risks, race conditions,
     broken assumptions, partial updates.

2. **Security Audit**
   - Injection (SQL/NoSQL/command), XSS/CSRF, authN/authZ flaws,
     insecure dependencies, secret leakage, unsafe deserialization,
     weak validation/sanitization.

3. **Code Quality & Maintainability**
   - DRY/SOLID violations, high complexity, unclear naming,
     dead code, brittle coupling, inconsistent patterns.

4. **Performance**
   - N+1 queries, over-fetching, blocking operations,
     unnecessary loops, poor caching strategy.

5. **Context Awareness**
   - Evaluate impact on adjacent modules, contracts, data integrity,
     migrations, observability, and rollback safety.

---

## 4) Review Constraints (Anti-Hallucination)

- Do not guess when evidence is missing. Mark uncertainty explicitly.
- Cite exact file paths and relevant snippets/lines when possible.
- Prefer high-signal findings; avoid low-value nitpicks.
- If a claim depends on runtime behavior, request or reference logs/tests.

---

## 5) Severity Rubric

- **[Critical]**: exploitable security flaw, data corruption/loss, outage risk,
  broken auth boundaries, unsafe migration.
- **[Warning]**: likely bug, significant maintainability debt, noticeable perf risk,
  weak validation/error handling.
- **[Info]**: non-blocking improvement for readability, consistency, or test depth.

---

## 6) Multi-Pass Audit Protocol

### Pass 0: Context Load
- Read project rules and conventions first.
- Read PR intent and changed files.

### Pass 1: Security + Correctness (Blockers)
- Find Critical and Warning issues first.
- Focus on exploitability and breakage scenarios.

### Pass 2: Performance + Maintainability
- Evaluate query behavior, async boundaries, complexity, and readability.

### Pass 3: Test and Ops Readiness
- Validate test coverage quality (not just quantity).
- Check logging, monitoring, rollback, migration safety.

### Pass 4: Final Triage
- Remove duplicates.
- Keep only actionable findings with concrete fixes.

---

## 7) Optional Consensus Mode (Parallel Auditors)

To reduce hallucinations and improve precision:

1. Run 3-5 independent review agents on the same diff.
2. Merge findings.
3. Auto-promote findings raised by at least 2 agents.
4. Mark single-agent findings as "needs verification" unless strongly evidenced.

---

## 8) Human-in-the-Loop Gate

- Auditor proposes findings and fixes.
- Maintainer explicitly accepts/rejects each proposed change.
- No automatic patching on Critical items without human approval.

---

## 9) Output Format (Use Exactly)

## Summary
[1-2 sentences on overall quality, intent, and risk posture]

## Critical Findings
- **File:** `path/to/file`
  - **Issue:** [clear description]
  - **Why it matters:** [impact]
  - **Suggested fix:**
```language
// minimal concrete fix
```

## Warnings
- **File:** `path/to/file`
  - **Issue:** [description]
  - **Why it matters:** [impact]
  - **Suggested fix:**
```language
// concrete fix
```

## Minor Improvements
- [high-value readability/consistency improvements only]

## Test Plan Gaps
- [missing tests, weak assertions, missing negative cases]

## Open Questions / Assumptions
- [explicit unknowns requiring maintainer input]

## Suggested Next Actions
- [ordered, practical follow-up sequence]

---

## 10) Prompt Block (Copy/Paste)

```markdown
# Role
Act as an expert Senior Staff Software Engineer and Security Auditor.
Review this change with strict rigor, similar to CodeRabbit.

# Priorities
1) Correctness & Bugs
2) Security
3) Performance
4) Maintainability
5) Context impact on the existing system

# Requirements
- Focus on meaningful findings, not stylistic nitpicks.
- For each issue: classify severity [Critical|Warning|Info].
- Provide concrete remediation code.
- Cite exact files and relevant code locations.
- If uncertain, state assumptions explicitly.

# Multi-pass protocol
- Pass 1: Security + logic blockers
- Pass 2: Performance + maintainability
- Pass 3: Tests + operations readiness

# Output format
Use:
1) Summary
2) Critical Findings
3) Warnings
4) Minor Improvements
5) Test Plan Gaps
6) Open Questions / Assumptions
7) Suggested Next Actions

# Project Context
[PASTE CONTEXT DUMP]

# Team Rules
[PASTE RULES / CONVENTIONS]

# Diff
[PASTE GIT DIFF]
```

---

## 11) Quick Workflow

1. Run `git diff` (or PR diff export).
2. Prepare context dump + team rules.
3. Run single-agent audit first.
4. For high-risk PRs, run consensus mode (parallel auditors).
5. Triage by severity.
6. Apply accepted fixes.
7. Re-run tests and close findings.

---

## 12) Laravel-Specific Audit Extension

Use this extension when the codebase includes Laravel, Livewire, queue workers,
or scheduled jobs.

### A) Eloquent and Database

- Check for N+1 risks (`with`, eager loading correctness).
- Check query scope correctness and ownership scoping.
- Validate transaction boundaries for multi-step writes.
- Verify migration safety:
  - backward compatibility
  - nullable/default strategy
  - rollback viability

### B) Validation and Request Boundaries

- Ensure untrusted input is validated at boundary (prefer Form Requests).
- Confirm type/format rules match domain constraints.
- Confirm sanitization / normalization steps are explicit (e.g. phone/email).
- Flag silent coercions that may hide invalid state.

### C) Authorization and Security

- Ensure policies / gates are used for resource access (not UI checks only).
- Confirm tenant/user ownership checks on read and write paths.
- Check CSRF, mass-assignment (`fillable/guarded`), and secret handling.
- Flag insecure logging of sensitive values.

### D) Queues, Jobs, and Scheduler

- Confirm idempotency for retried jobs.
- Validate dedupe / replay protection where required.
- Ensure time-zone and clock assumptions are explicit.
- Check failure handling, retries, and dead-letter strategy.
- Verify scheduled commands are safe under concurrent execution.

### E) Livewire and UI Reactivity

- Ensure `wire:model`, `wire:submit`, and loading states are correct.
- Confirm no trust is placed in client-side state for authorization.
- Check component root structure and render consistency.
- Verify accessibility basics (focus visibility, keyboard navigation, labels).

### F) Observability and Operations

- Ensure actionable logs are present without leaking secrets.
- Verify metrics/events for critical flows.
- Require a rollback note for risky changes.
- Require test coverage for happy path + failure path + authorization path.

### Laravel-Specific Output Addendum

Append this section when relevant:

## Laravel Runtime Risks
- **Data Integrity:** [issues]
- **Authorization Boundaries:** [issues]
- **Queue/Scheduler Safety:** [issues]
- **Migration/Deployment Safety:** [issues]

