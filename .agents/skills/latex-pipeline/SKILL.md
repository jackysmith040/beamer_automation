---
name: latex-pipeline
description: Workflow cheatsheet and command reference for the 4-stage Beamer and Thesis automation pipeline.
---

# LaTeX & Beamer Automation Pipeline

## Pipeline Workflow
1. **Input (`input/`)**: Place raw markdown or LaTeX notes into `input/beamer/` or `input/thesis/`, and images into `input/assets/`.
2. **Digestion (`digestion/`)**: Normalized intermediary JSON representations and syntax linting passes.
3. **Template Override (`template_override/`)**: Injects content into custom university or conference templates without modifying the original template files.
4. **Output (`output/`)**: Standalone deliverables (`.pdf`, master `.tex`, local `figures/`, `.zip` bundles, and manifest).

## Pipeline Execution Commands (Typer CLI)
The pipeline provides a modern CLI interface powered by `typer` and `rich`:

- **Compile a Presentation with Self-Healing**:
  ```bash
  uv run beamer build --input input/beamer/defense_slides.md --template samples/templates/modern_clean.tex
  ```
- **Review Pre-flight Quality**:
  ```bash
  uv run beamer review input/beamer/defense_slides.md
  ```
- **Instant Demo**:
  ```bash
  uv run beamer demo
  ```
- **Compile Directly**:
  ```bash
  uv run beamer compile input/beamer/defense_slides.tex
  ```
- **Initialize Fresh Workspace**:
  ```bash
  uv run beamer init --type beamer
  ```

## Machine-Readable JSON Mode for AI Agents
Every command supports `--json` for automated agent orchestration:
```bash
uv run beamer build --input input/slides.md --template samples/templates/modern_clean.tex --json
uv run beamer review input/slides.md --json
```

## Resetting for New Projects
- **Via CLI**:
  ```bash
  uv run beamer reset
  uv run beamer reset --dry-run
  uv run beamer reset --no-backup
  ```
- **Via Scripts**:
  - Windows: `.\reset.ps1`
  - macOS / Linux: `./reset.sh`
