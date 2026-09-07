"""
agent_helper.slide_builder
Frame compositor that generates robust, styled Beamer LaTeX frames from Slide models.
"""

import re
from typing import Any
from agent_helper.parser import Slide
from agent_helper.escaper import escape_latex


def build_frame(slide: Slide, archetype: dict[str, Any] | None = None) -> str:
    """Render a single Slide object into a Beamer LaTeX frame block."""
    options: list[str] = []
    
    # Code frames must be marked [fragile]
    if slide.is_fragile or slide.layout == "code":
        options.append("fragile")

    # Overflow guard: if bullet points exceed 7, add allowframebreaks
    if len(slide.bullets) > 7:
        options.append("allowframebreaks")

    opts_str = f"[{', '.join(options)}]" if options else ""
    lines: list[str] = [f"\\begin{{frame}}{opts_str}"]

    # Title & Subtitle
    if slide.title and slide.layout != "title":
        safe_title = escape_latex(slide.title)
        lines.append(f"  \\frametitle{{{safe_title}}}")
        if slide.subtitle:
            safe_subtitle = escape_latex(slide.subtitle)
            lines.append(f"  \\framesubtitle{{{safe_subtitle}}}")

    # Layout rendering
    if slide.layout == "title":
        lines.append("  \\titlepage")

    elif slide.layout == "columns":
        lines.append("  \\begin{columns}[T]")
        col_width = "0.48\\textwidth"
        num_cols = len(slide.columns)
        if num_cols > 2:
            col_width = f"{round(0.96 / num_cols, 2)}\\textwidth"

        for col_items in slide.columns:
            lines.append(f"    \\begin{{column}}{{{col_width}}}")
            in_itemize = False
            for item in col_items:
                clean_item = item.strip()
                if clean_item.startswith(("### ", "## ")):
                    if in_itemize:
                        lines.append("      \\end{itemize}")
                        in_itemize = False
                    header_text = clean_item.lstrip("#").strip()
                    lines.append(f"      {{\\large \\textbf{{{escape_latex(header_text)}}}}}\\par\\vspace{{0.2cm}}")
                else:
                    if not in_itemize:
                        lines.append("      \\begin{itemize}")
                        in_itemize = True
                    b_text = re.sub(r"^([-\*+]|\d+\.)\s+", "", clean_item)
                    lines.append(f"        \\item {escape_latex(b_text)}")
            if in_itemize:
                lines.append("      \\end{itemize}")
            lines.append("    \\end{column}")
        lines.append("  \\end{columns}")

    elif slide.layout == "block":
        # Render any introductory paragraphs
        for p in slide.paragraphs:
            lines.append(f"  {escape_latex(p)}\n")

        block_env = slide.block_type or "block"
        b_title = escape_latex(slide.block_title or "Note")
        lines.append(f"  \\begin{{{block_env}}}{{{b_title}}}")
        for item in slide.block_content:
            lines.append(f"    {escape_latex(item)}")
        lines.append(f"  \\end{{{block_env}}}")

    elif slide.layout == "code":
        for p in slide.paragraphs:
            lines.append(f"  {escape_latex(p)}\n")
        
        # Wrap code in semiverbatim or verbatim block
        lines.append("  \\begin{semiverbatim}")
        # Clean lines in code
        for c_line in slide.code_content.strip().split("\n"):
            lines.append(f"  {c_line}")
        lines.append("  \\end{semiverbatim}")

        if slide.bullets:
            lines.append("  \\begin{itemize}")
            for b in slide.bullets:
                lines.append(f"    \\item {escape_latex(b)}")
            lines.append("  \\end{itemize}")

    else:  # Standard layout
        for p in slide.paragraphs:
            lines.append(f"  {escape_latex(p)}\n")

        if slide.bullets:
            lines.append("  \\begin{itemize}")
            for b in slide.bullets:
                lines.append(f"    \\item {escape_latex(b)}")
            lines.append("  \\end{itemize}")

    # Speaker notes
    if slide.notes:
        lines.append(f"  \\note{{{escape_latex(slide.notes)}}}")

    lines.append("\\end{frame}\n")
    return "\n".join(lines)


def build_presentation(metadata: dict[str, Any], slides: list[Slide], archetype: dict[str, Any] | None = None) -> str:
    """Compose all slides into a sequence of LaTeX frame blocks."""
    frame_blocks: list[str] = []

    # If title metadata is provided and first slide is not explicitly a title slide, prepend \maketitle frame
    has_title_slide = any(s.layout == "title" for s in slides)
    if "title" in metadata and not has_title_slide:
        frame_blocks.append("\\begin{frame}\n  \\titlepage\n\\end{frame}\n")

    for slide in slides:
        frame_blocks.append(build_frame(slide, archetype))

    return "\n".join(frame_blocks)
