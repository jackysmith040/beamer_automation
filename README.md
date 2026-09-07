# 🚀 Beamer & Thesis Automation Framework

> **Agent-Driven, Zero-Config LaTeX Automation for Students, Lecturers, and Researchers.**

An open-source automation framework designed to make creating academic presentations (Beamer) and theses effortless and joyful. The tools power an AI agent under the hood, so humans can focus on ideas while the system handles formatting, compilation, and error recovery.

---

## 🌟 Features

- **⚡ Zero-Config LaTeX Compilation**: Built on [Tectonic](https://tectonic-typesetting.github.io/), which automatically downloads required TeX packages and fonts dynamically. No 5GB TeXLive or MiKTeX installation required.
- **💻 True Cross-Platform**: Works out of the box on **Windows**, **macOS** (Apple Silicon & Intel), and **Ubuntu / Linux**.
- **🤖 Agent-First Architecture**: Machine-readable `--json` modes for AI coding assistants (Axon, Claude, ChatGPT, Gemini) paired with rich, colorized terminal UI for human developers.
- **🛡️ Fault-Tolerant & Self-Healing**: Automated pre-flight linting, `\IfFileExists` safety guards, bracket balance checking, and automatic compilation error recovery.
- **📂 Clean 4-Stage Workflow**:
  1. `input/`: Your rough markdown notes, draft `.tex`, or compartmental figures.
  2. `digestion/`: Safe AST analysis, normalization, and sandbox validation.
  3. `template_override/`: Apply university/conference branding without touching template code.
  4. `output/`: Clean, standalone, ready-to-share PDFs, master LaTeX files, figures, and zip packages.
- **🔄 Safe Lifecycle Reset**: Single-command workspace reset that automatically creates a timestamped zip backup in `archive/` before clearing directories.

---

## 🚀 Quick Start

### 1. Installation
Using [`uv`](https://github.com/astral-sh/uv) (recommended):
```bash
# Clone the repository
git clone git@github.com:jackysmith040/beamer_automation.git
cd beamer_automation

# Install dependencies and sync virtual environment
uv sync
```

### 2. Run the Demo (5 Seconds)
Build the sample presentation to verify everything works:
```bash
uv run beamer demo
```
Your compiled PDF will be ready in `output/demo/demo_presentation.pdf`!

---

## 🛠️ CLI Reference

```bash
# Build a presentation or thesis through the 4-stage pipeline
uv run beamer build --input input/beamer/slides.md --template template_override/modern_clean.tex

# Machine-readable output for AI agents
uv run beamer build --input input/beamer/slides.md --json

# Run pre-flight linting and syntax checks
uv run beamer review input/beamer/slides.tex

# Compile any TeX file with self-healing Tectonic engine
uv run beamer compile input/thesis/thesis_merged.tex --outdir output/thesis

# Reset workspace safely for a new project (auto-backs up to archive/)
uv run beamer reset
# Or preview without touching files:
uv run beamer reset --dry-run
```

---

## 📁 Repository Layout

```text
beamer_automation/
├── agent_helper/          # Composable Python automation engine
│   ├── cli.py             # Rich Typer CLI (beamer)
│   ├── compiler.py        # Cross-platform Tectonic bootstrapper & self-healer
│   ├── normalizer.py      # Frontmatter & text normalization
│   ├── parser.py          # Markdown slide chunking & archetype detection
│   ├── reset.py           # Atomic workspace reset & zip backup engine
│   ├── reviewer.py        # Pre-flight syntax and environment linting
│   ├── runner.py          # 4-stage pipeline orchestrator
│   ├── slide_builder.py   # Beamer frame code generator
│   └── template_engine.py # Preamble extraction & archetype injection
├── input/                 # User project files (untracked)
├── digestion/             # Normalized sandbox cache (untracked)
├── template_override/     # University / custom LaTeX templates
├── output/                # Finished PDFs, standalone TeX, and zips (untracked)
├── samples/               # Pristine starter samples for Beamer & Thesis
├── tests/                 # Comprehensive test suite (12+ tests)
├── pyproject.toml         # Packaging configuration
├── reset.ps1              # Windows PowerShell reset shortcut
└── reset.sh               # Unix (macOS / Ubuntu) reset shortcut
```

---

## 🔒 Privacy & Git Tracking

This repository is configured with privacy guardrails in `.gitignore`. Your personal slides, thesis chapters, student names, and output PDFs placed inside `input/`, `digestion/`, `output/`, and `archive/` are **never committed to Git**.

---

## 📄 License

MIT License. Designed for students, lecturers, and researchers worldwide.
