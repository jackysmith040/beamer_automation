# LaTeX & Beamer Automation Delivery Invariants

1. **Output Packaging Mandate**:
   - Always export final compiled documents to `output/` (e.g. `output/beamer/` and `output/thesis/`).
   - Every delivery in `output/` must include:
     - The compiled `.pdf`
     - The standalone `.tex` source
     - The local `figures/` directory containing all referenced assets
     - Ready-to-send `.zip` archives (consolidated and per-component)
     - A clear `README.md` manifest describing the files.

2. **Fault-Tolerant Asset Loading (`\IfFileExists`)**:
   - Any figure or simulation plot that may not yet be rendered or might be loaded on remote platforms (like Overleaf) must be wrapped in `\IfFileExists`:
     ```latex
     \IfFileExists{figures/plot.png}{%
         \includegraphics[width=\linewidth]{figures/plot.png}%
     }{%
         \fbox{\parbox[c][3cm][c]{\linewidth}{\centering\scriptsize \textbf{Figure Title}\\[0.3em]Upload \texttt{plot.png} to \texttt{figures/}}}%
     }
     ```
   - All underscores in fallback box file names must be escaped as `\_` to prevent LaTeX math subscript errors (`Missing $ inserted`).

3. **Academic Merging & Equation Normalization**:
   - Ensure all equations in merged theses follow uniform, chapter-prefixed sequential numbering (e.g., `(3.1)` to `(3.43)`).
   - Verify that all in-text equation citations (`\ref{...}` or referenced numbers) strictly match the live equation tags.

4. **Workspace Reset & Safety**:
   - Resetting the pipeline for a new project must always create a timestamped backup in `archive/` before clearing `input/`, `digestion/`, or `output/`.
   - Never wipe `agent_helper/bin/tectonic.exe` or `template_override/` during workspace resets.
