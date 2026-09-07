---
title: Introduction to Modern Compartmental Modelling
subtitle: An Agent-Driven Beamer Automation Showcase
author: Dr. Jane Doe & Alex Smith
institute: Department of Applied Mathematics, Tech University
date: \today
theme: modern_clean
---

# Presentation Overview
- Welcome to the automated Beamer pipeline.
- Demonstrates zero-config compilation across Windows, macOS, and Linux.
- Supports formulas, split columns, alerts, and code blocks.

---

# Why Automate LaTeX Presentations?
- Traditional LaTeX authoring suffers from slow manual compile cycles.
- Package conflicts and font configuration waste valuable research time.
- Our pipeline bridges natural markdown with publication-quality output.

---

# Mathematical Formulation
The general compartmental flow is governed by:
\begin{align}
\frac{dS}{dt} &= \Lambda - \beta \frac{S I}{N} - \mu S \\
\frac{dI}{dt} &= \beta \frac{S I}{N} - (\gamma + \mu) I \\
\frac{dR}{dt} &= \gamma I - \mu R
\end{align}

- $\Lambda$: Natural recruitment rate into susceptible class.
- $\beta$: Contact rate per unit time.
- $\gamma$: Recovery rate from infection.

---

# Comparative Analysis
::: columns
::: column 0.48
### Classical Workflow
- Manual syntax debugging.
- Fragile environment management.
- Multi-step local installations.
:::
::: column 0.48
### Automated Pipeline
- Markdown-to-Beamer compiler.
- Self-healing error recovery.
- Portable Tectonic zero-config engine.
:::
:::

---

# Summary & Next Steps
- Drop your markdown or LaTeX files into `input/`.
- Let your AI agent format, verify, and compile.
- Deliverables are cleanly packaged in `output/` with ready-to-share ZIP archives.
