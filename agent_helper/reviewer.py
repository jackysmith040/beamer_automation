"""
agent_helper.reviewer
Pre-flight review and syntax verification utility for Beamer presentations.
"""

from dataclasses import dataclass, field
import re
from typing import Any
from agent_helper.parser import Slide


@dataclass
class ReviewReport:
    valid: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.valid

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "is_valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


def review_presentation(tex_code: str, slides: list[Slide] | None = None) -> ReviewReport:
    """Audit the generated LaTeX code and slide models for syntax correctness and overflow."""
    report = ReviewReport()
    
    # 1. Metric calculations
    frames = re.findall(r"\\begin\{frame\}(.*?)\\end\{frame\}", tex_code, flags=re.DOTALL)
    report.metrics["frame_count"] = len(frames)
    report.metrics["line_count"] = len(tex_code.splitlines())

    # 2. Check brace balancing (excluding comments)
    code_without_comments = re.sub(r"(?<!\\)%.*$", "", tex_code, flags=re.MULTILINE)
    open_braces = code_without_comments.count("{")
    close_braces = code_without_comments.count("}")
    if open_braces != close_braces:
        report.errors.append(f"Mismatched curly braces detected: {open_braces} open '{{' vs {close_braces} close '}}'.")
        report.valid = False

    # 3. Check math delimiter balancing ($ ... $)
    unescaped_dollars = re.findall(r"(?<!\\)\$", code_without_comments)
    if len(unescaped_dollars) % 2 != 0:
        report.errors.append(f"Unbalanced inline math '$' delimiters detected (found {len(unescaped_dollars)}).")
        report.valid = False

    # 4. Check environment matching (\begin{x} matches \end{x})
    begins = re.findall(r"\\begin\{([a-zA-Z0-9_\*]+)\}", code_without_comments)
    ends = re.findall(r"\\end\{([a-zA-Z0-9_\*]+)\}", code_without_comments)
    
    begin_counts: dict[str, int] = {}
    end_counts: dict[str, int] = {}
    for b in begins:
        begin_counts[b] = begin_counts.get(b, 0) + 1
    for e in ends:
        end_counts[e] = end_counts.get(e, 0) + 1

    for env, count in begin_counts.items():
        e_count = end_counts.get(env, 0)
        if count != e_count:
            report.errors.append(f"Environment mismatch: '\\begin{{{env}}}' called {count} times, but '\\end{{{env}}}' called {e_count} times.")
            report.valid = False

    # 5. Check fragile flag for frames containing verbatim or semiverbatim
    frame_matches = re.finditer(r"(\\begin\{frame\}(?:\[([^\]]*)\])?)(.*?)\\end\{frame\}", tex_code, flags=re.DOTALL)
    for idx, fm in enumerate(frame_matches, 1):
        frame_decl = fm.group(1)
        frame_opts = fm.group(2) or ""
        frame_body = fm.group(3)

        has_verbatim = any(v in frame_body for v in ["semiverbatim", "verbatim", "lstlisting", "\\verb"])
        if has_verbatim and "fragile" not in frame_opts:
            report.errors.append(f"Slide #{idx} contains verbatim code but is missing the '[fragile]' option on \\begin{{frame}}.")
            report.valid = False

    # 6. Overflow warnings (check slides for >7 bullets or very long text)
    if slides:
        for idx, s in enumerate(slides, 1):
            if len(s.bullets) > 7:
                report.warnings.append(f"Slide #{idx} ('{s.title}') has {len(s.bullets)} bullets. Consider splitting or using allowframebreaks.")
            if len(s.paragraphs) > 5:
                report.warnings.append(f"Slide #{idx} ('{s.title}') has dense paragraph text. Consider converting to concise bullet points.")

    return report
