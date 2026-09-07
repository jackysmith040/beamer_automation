---
name: beamer-lecturer
description: Specialized guidance and pedagogical structures for lecturers, professors, and workshop instructors building lecture slide decks, theorem boxes, and interactive class notes.
---

# Beamer Lecturer & Educator Guide

This skill helps educators and instructors rapidly build pedagogically structured lecture slides using Markdown and modern LaTeX Beamer.

## Pedagogical Slide Patterns

### 1. Definition - Theorem - Proof Flow
Structure mathematical and technical lectures using semantic callout blocks:

```markdown
## Fundamental Theorem of Calculus

::: block Definition: Continuity
A function $f$ is continuous at $c$ if $\lim_{x \to c} f(x) = f(c)$.
:::

::: block Theorem: Part 1
If $f$ is continuous on $[a, b]$ and $F(x) = \int_a^x f(t)dt$, then:
$$F'(x) = f(x)$$
:::
```

### 2. Side-by-Side Worked Examples
Keep problem statements on the left and derivations on the right:

```markdown
## Worked Example: Eigenvalue Decomposition

::: columns
::: column 0.50
### Problem
Find eigenvalues of matrix:
$$A = \begin{pmatrix} 4 & 1 \\ 2 & 3 \end{pmatrix}$$
:::
::: column 0.50
### Solution Steps
1. Compute $\det(A - \lambda I) = 0$
2. $(4 - \lambda)(3 - \lambda) - 2 = 0$
3. $\lambda^2 - 7\lambda + 10 = 0$
4. Factors: $(\lambda - 5)(\lambda - 2) = 0$
5. $\lambda_1 = 5, \lambda_2 = 2$
:::
```

### 3. Step-by-Step Bullet Unveiling (`pause`)
Control student attention by revealing concepts incrementally:

```markdown
## Algorithmic Complexity

- Linear Search: $\mathcal{O}(n)$
- Binary Search: $\mathcal{O}(\log n)$
- Merge Sort: $\mathcal{O}(n \log n)$
```

## Recommended Workflow for Course Decks

1. **Keep raw course notes in Markdown**:
   Students can read the markdown notes directly; you compile the same file to PDF slides for lecture.
2. **Pre-flight Syntax Linting**:
   ```bash
   uv run beamer review lecture_01.md
   ```
3. **Generate Lecture Slides**:
   ```bash
   uv run beamer build -i lecture_01.md -t samples/templates/modern_clean.tex -o output/lectures/
   ```
4. **Distribute to Class**:
   Distribute the generated PDF from `output/lectures/`.
