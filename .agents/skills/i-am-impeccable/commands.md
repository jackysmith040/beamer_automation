# Impeccable command catalog — ELI5 reference

Load this file **only when `i-am-impeccable` runs**. Upstream command bodies live in `.agents/skills/impeccable/` after install.

Source: [Impeccable docs](https://impeccable.style/docs/) — 23 commands, 6 categories.

---

## Create — build something new

| Command | ELI5 | Pick when | Skip when |
|---------|------|-----------|-----------|
| **craft** | Blueprint + build in one go | New page/feature from scratch; you want shape then code | Small tweak to existing UI |
| **impeccable** | The design brain behind all commands | You want general design fluency loaded, not one discipline | You need a specific fix (use Refine) |
| **shape** | Interview before any pixels | Starting brand/page direction; need a brief first | UI exists; you know what to fix |

---

## Evaluate — review what you have

| Command | ELI5 | Pick when | Skip when |
|---------|------|-----------|-----------|
| **audit** | Five-area technical check with severity grades | Pre-ship quality pass; want P0–P3 issues | You want aesthetic opinion, not checklist |
| **critique** | Design report card with scores | "Feels like AI slop" or "something's off" | You already know it's spacing/fonts |

---

## Refine — improve one dimension

| Command | ELI5 | Pick when | Skip when |
|---------|------|-----------|-----------|
| **animate** | Motion that explains state | Loading, success, transitions feel dead | Layout or color is the problem |
| **bolder** | Turn up visual impact safely | Too plain, safe, forgettable | Already loud/busy |
| **colorize** | Add color without clown palette | Monochrome feels flat | Colors already clash |
| **delight** | Small personality moments | Functional but forgettable | Core UX broken |
| **layout** | Fix spacing, grid, rhythm | Cramped, misaligned, uneven | Copy or color is wrong |
| **overdrive** | Cinematic / shader-level effects | Marketing hero needs wow | App dashboard; keep boring |
| **quieter** | Turn down visual noise | Too busy, shouting, cluttered | Already minimal |
| **typeset** | Fix fonts and text hierarchy | Inter everywhere, weak headings | Layout grid is broken |

---

## Simplify — remove complexity

| Command | ELI5 | Pick when | Skip when |
|---------|------|-----------|-----------|
| **adapt** | Works on phone, tablet, desktop | Responsive breakpoints wrong | Desktop-only internal tool |
| **clarify** | Rewrite confusing UI copy | Labels/buttons confuse users | Visual design is the issue |
| **distill** | Remove what doesn't earn its place | Too many sections/elements | Page is already minimal |

---

## Harden — production-ready

| Command | ELI5 | Pick when | Skip when |
|---------|------|-----------|-----------|
| **harden** | Edge cases, errors, empty states, overflow | Shipping to real users soon | Still exploring direction |
| **onboard** | First-run and empty-state UX | New users see blank screens | Feature is admin-only |
| **optimize** | Speed and performance | Slow LCP, heavy bundle | Visual polish pass |
| **polish** | Final pass from good to great | Works but feels rough | Need diagnosis first (use critique) |

---

## System — setup and tooling

| Command | ELI5 | Pick when | Skip when |
|---------|------|-----------|-----------|
| **document** | Write DESIGN.md from your codebase | Tokens exist but no design spec file | No UI in repo yet |
| **extract** | Pull patterns into design system | Repeated one-offs should become components | Greenfield page |
| **live** | Try 3 variants in browser, accept one | Iterating on one component visually | Whole-page rethink (use shape/craft) |
| **teach** | Tell Impeccable who this product is for | No PRODUCT.md; brand/marketing work | Internal tool with existing DESIGN.md |

---

## Intent → command quick map

| User says (signals) | Top picks (ranked) |
|---------------------|-------------------|
| "Build a new landing page" | shape → craft (confirm each step) |
| "Looks like AI slop / generic SaaS" | critique, audit, typeset |
| "Fix the fonts / typography" | typeset, layout |
| "Too busy / too loud" | quieter, distill |
| "Too plain / boring" | bolder, colorize, delight |
| "Spacing / grid feels wrong" | layout, polish |
| "Add motion / animations" | animate |
| "Ready to ship" | polish, harden, audit |
| "Try different versions in browser" | live |
| "Set up design rules for project" | teach, document |
| "Mobile looks broken" | adapt, layout |
| "Confusing labels / copy" | clarify |
| "Make it faster" | optimize |
| "Empty state / first visit" | onboard, harden |
| "Pull this into our design system" | extract, document |
| "Wow factor / cinematic" | overdrive (brand only) |

---

## Multi-step sequences (confirm each step)

| Goal | Sequence |
|------|----------|
| New marketing site | teach → shape → craft → polish |
| Fix slop on existing page | critique → polish |
| Establish design memory | teach → document |
| Browser iteration loop | live → polish |

Present step 1 only. After it completes, offer step 2 with a fresh confirm round.

---

## Preflight signals

| Condition | Surface in menu |
|-----------|-----------------|
| No `PRODUCT.md` + marketing/brand signals
 | **teach** as setup option |
| Tokens/components exist, no `DESIGN.md` | **document** as setup option |
| User attached same-wavelength brief | Prefer commands matching locked IN scope |
| Plan mode active | Prefer **shape**, **critique**, **audit** over **craft** until brief confirmed |
