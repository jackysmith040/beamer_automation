"""
agent_helper.template_engine
Preamble extraction, archetype detection, and body injection for arbitrary Beamer templates.
"""

import re
from typing import Any
from agent_helper.escaper import escape_latex


def extract_preamble(template_code: str) -> str:
    """Extract everything before \\begin{document} in a LaTeX template."""
    match = re.search(r"\\begin\{document\}", template_code)
    if match:
        return template_code[: match.start()].strip()
    return template_code.strip()


def extract_postamble(template_code: str) -> str:
    """Extract \\end{document} and any subsequent commands."""
    match = re.search(r"\\end\{document\}", template_code)
    if match:
        return template_code[match.start():].strip()
    return "\\end{document}"


def detect_archetypes(template_code: str) -> dict[str, Any]:
    """Inspect a template to detect used packages, theme, and macro conventions."""
    info: dict[str, Any] = {
        "theme": "default",
        "colortheme": "default",
        "has_listings": "\\usepackage{listings}" in template_code or "\\usepackage{minted}" in template_code,
        "has_tcolorbox": "\\usepackage{tcolorbox}" in template_code,
        "has_tikz": "\\usepackage{tikz}" in template_code,
        "has_aspectratio": "aspectratio=" in template_code,
        "has_placeholder": "% {{SLIDES}}" in template_code or "% [[CONTENT]]" in template_code,
    }

    theme_match = re.search(r"\\usetheme(?:\[[^\]]*\])?\{([^}]+)\}", template_code)
    if theme_match:
        info["theme"] = theme_match.group(1).strip()

    color_match = re.search(r"\\usecolortheme(?:\[[^\]]*\])?\{([^}]+)\}", template_code)
    if color_match:
        info["colortheme"] = color_match.group(1).strip()

    return info


def inject_content(template_code: str, slides_latex: str, metadata: dict[str, Any] | None = None) -> str:
    """Inject generated slides LaTeX into a template."""
    meta = metadata or {}
    working_template = template_code

    def _set_meta_cmd(text: str, cmd: str, val: str) -> str:
        escaped = escape_latex(str(val))
        safe_val = escaped.replace("\\", "\\\\")
        pat = rf"\\{cmd}(?:\[[^\]]*\])?\{{[^}}]*\}}"
        if re.search(pat, text):
            return re.sub(pat, f"\\\\{cmd}{{{safe_val}}}", text)
        idx = text.find(r"\begin{document}")
        if idx != -1:
            return text[:idx] + f"\\{cmd}{{{escaped}}}\n" + text[idx:]
        doc_idx = text.find(r"\documentclass")
        if doc_idx != -1:
            newline_after = text.find("\n", doc_idx)
            return text[:newline_after + 1] + f"\n\\{cmd}{{{escaped}}}\n" + text[newline_after + 1:]
        return f"\\{cmd}{{{escaped}}}\n" + text

    if "title" in meta:
        working_template = _set_meta_cmd(working_template, "title", meta["title"])
    if "subtitle" in meta:
        working_template = _set_meta_cmd(working_template, "subtitle", meta["subtitle"])
    if "author" in meta:
        working_template = _set_meta_cmd(working_template, "author", meta["author"])
    if "institute" in meta:
        working_template = _set_meta_cmd(working_template, "institute", meta["institute"])
    if "date" in meta:
        working_template = _set_meta_cmd(working_template, "date", meta["date"])

    # 1. Check for explicit placeholder tag
    placeholder_pattern = r"%\s*(\{\{SLIDES\}\}|\[\[CONTENT\]\]|%%SLIDES_HERE%%)"
    if re.search(placeholder_pattern, working_template):
        return re.sub(placeholder_pattern, lambda _: slides_latex, working_template, count=1)

    # 2. Otherwise, preserve preamble and replace document body
    preamble = extract_preamble(working_template)
    postamble = extract_postamble(working_template)

    output = f"{preamble}\n\n\\begin{{document}}\n\n{slides_latex}\n\n{postamble}\n"
    return output
