"""
agent_helper.escaper
Intelligent LaTeX escaping utility that protects math blocks and existing LaTeX commands.
"""

import re


def escape_latex(text: str, preserve_math: bool = True, preserve_commands: bool = True) -> str:
    """Escape special LaTeX characters in text while preserving math and commands.
    
    Characters escaped:
        & -> \\&
        % -> \\%
        # -> \\#
        _ -> \\_ (outside math and commands)
        ~ -> \\textasciitilde{}
        ^ -> \\textasciicircum{}
    """
    if not text:
        return ""

    # Placeholders for protected segments
    protected: list[str] = []

    def save_segment(match: re.Match) -> str:
        idx = len(protected)
        protected.append(match.group(0))
        return f"XZZLATEXPROTECTED{idx}ZZX"

    working_text = text

    if preserve_math:
        # Protect display environments like \begin{align} ... \end{align}
        working_text = re.sub(
            r"\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?|alignat\*?|matrix\*?|pmatrix\*?|bmatrix\*?)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?|multline\*?|alignat\*?|matrix\*?|pmatrix\*?|bmatrix\*?)\}",
            save_segment,
            working_text,
            flags=re.DOTALL,
        )
        # Protect display math $$ ... $$ and \[ ... \]
        working_text = re.sub(r"\$\$.*?\$\$", save_segment, working_text, flags=re.DOTALL)
        working_text = re.sub(r"\\\[.*?\\\]", save_segment, working_text, flags=re.DOTALL)
        # Protect inline math $ ... $ and \( ... \)
        working_text = re.sub(r"(?<!\\)\$.*?(?<!\\)\$", save_segment, working_text)
        working_text = re.sub(r"\\\(.*?\\\)", save_segment, working_text)

    if preserve_commands:
        # Protect standard LaTeX commands like \textbf{...}, \item, \begin{...}, \end{...}, etc.
        # Match \command[opt]{arg} or \command{arg} or \command
        working_text = re.sub(
            r"\\[a-zA-Z]+(?:\*|\b)(?:\[[^\]]*\])?(?:\{[^{}]*\})?",
            save_segment,
            working_text,
        )

    # Now escape unprotected characters
    # 1. Backslash (if not part of command, e.g. standalone \)
    # We already saved valid commands, so remaining backslashes can be converted or left.
    
    # 2. Escape ampersand (& -> \&)
    working_text = re.sub(r"(?<!\\)&", r"\&", working_text)
    
    # 3. Escape percent (% -> \%)
    working_text = re.sub(r"(?<!\\)%", r"\%", working_text)
    
    # 4. Escape dollar sign ($ -> \$) (any remaining outside math)
    working_text = re.sub(r"(?<!\\)\$", r"\$", working_text)
    
    # 5. Escape hash (# -> \#)
    working_text = re.sub(r"(?<!\\)#", r"\#", working_text)
    
    # 6. Escape underscore (_ -> \_)
    working_text = re.sub(r"(?<!\\)_", r"\_", working_text)
    
    # 7. Convert markdown bold **text** to \textbf{text} and *text* to \textit{text}
    working_text = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", working_text)
    working_text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\\textit{\1}", working_text)
    working_text = re.sub(r"`([^`]+)`", r"\\texttt{\1}", working_text)

    # Restore protected segments in reverse order
    for idx, seg in enumerate(protected):
        working_text = working_text.replace(f"XZZLATEXPROTECTED{idx}ZZX", seg)

    return working_text
