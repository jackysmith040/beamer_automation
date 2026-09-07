---
name: beamer-student
description: Specialized guidance and best practices for students preparing undergraduate or graduate thesis defenses, project presentations, and academic paper talks using the Beamer pipeline.
---

# Beamer Student Defense & Seminar Guide

This skill guides students through designing clear, high-scoring thesis defense and project presentations.

## Defense Slide Architecture (15–20 Minute Rule)

A classic 15–20 minute defense typically consists of 15–20 slides:
1. **Title Slide**: Project Title, Student Name, Student ID/Index, Supervisor(s), Department, Head of Department (HOD), University Logo.
2. **Context & Problem Statement**: What is broken, inefficient, or unsolved?
3. **Research Objectives**: General and specific objectives (bulleted, unambiguous).
4. **Scope & Significance**: Who benefits and what boundaries were set.
5. **Literature Review / Theoretical Grounding**: Key prior work and knowledge gaps.
6. **Methodology / System Architecture**: Flow diagrams, formulas, system block diagrams.
7. **Implementation & Experiments**: Key parameters, datasets, testbed configuration.
8. **Results & Evaluation**: High-resolution graphs, side-by-side comparison tables.
9. **Discussion**: Interpretation of results and error analysis.
10. **Conclusion & Future Work**: Key takeaway and tangible next steps.
11. **Acknowledgements & References**: Funders, faculty, lab mates.
12. **Thank You & Q&A Slide**: Contact info and prompt for committee questions.

## Formatting Guidelines for High Grades

### 1. Math & Equations
Always use standard LaTeX math blocks in your Markdown:
```markdown
$$E = mc^2$$

\begin{equation}
\label{eq:sefr}
R_0 = \beta \times \frac{S(0)}{\gamma}
\end{equation}
```
Equations are automatically preserved and numbered.

### 2. Split Columns for Figures and Explanations
Place images next to bulleted observations rather than stacking them vertically:
```markdown
## System Architecture

::: columns
::: column 0.55
- Dual-channel convolution block
- Residual skip-connection to prevent gradient decay
- Softmax output across $K$ classes
:::
::: column 0.45
![](assets/system_diagram.png)
:::
```

### 3. Emphasizing Key Findings
Use block environments:
```markdown
::: block Key Discovery
The proposed algorithm reduced latency by 34.2% while maintaining 99.1% accuracy.
:::
```

## Quick CLI Commands for Students

- **Initialize Starter Workspace**:
  ```bash
  uv run beamer init --type beamer
  # or for thesis
  uv run beamer init --type thesis
  ```
- **Build Presentation**:
  ```bash
  uv run beamer build --input input/beamer/slides.md --template samples/templates/modern_clean.tex
  ```
- **Review Pre-flight Quality**:
  ```bash
  uv run beamer review input/beamer/slides.md
  ```
- **Zip for Submission / Supervisor Review**:
  After generating your PDF in `output/`, compile or zip your assets to submit to your supervisor.
