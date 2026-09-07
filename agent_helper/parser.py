"""
agent_helper.parser
Composable parsing utility that chunks raw text/markdown into structured Slide models.
"""

from dataclasses import dataclass, field, asdict
import json
import re
from typing import Any

from agent_helper.normalizer import normalize_text, extract_frontmatter
from agent_helper.escaper import escape_latex


@dataclass
class Slide:
    title: str = ""
    subtitle: str = ""
    layout: str = "standard"  # 'title', 'standard', 'columns', 'block', 'code'
    bullets: list[str] = field(default_factory=list)
    paragraphs: list[str] = field(default_factory=list)
    columns: list[list[str]] = field(default_factory=list)
    block_type: str = "block"  # 'block', 'alertblock', 'exampleblock'
    block_title: str = ""
    block_content: list[str] = field(default_factory=list)
    code_lang: str = ""
    code_content: str = ""
    notes: str = ""
    is_fragile: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Slide":
        return cls(**data)


def parse_slides(raw_content: str) -> tuple[dict[str, Any], list[Slide]]:
    """Parse raw markdown or outline text into metadata and a list of Slide objects."""
    metadata, body = extract_frontmatter(raw_content)
    normalized = normalize_text(body)

    slides: list[Slide] = []
    
    # Check if there's a top-level H1 that can serve as the presentation title slide
    h1_match = re.search(r"^#\s+(.+)$", normalized, flags=re.MULTILINE)
    if h1_match:
        doc_title = h1_match.group(1).strip()
        if "title" not in metadata:
            metadata["title"] = doc_title
        # Check for immediate subtitle
        lines = normalized.split("\n")
        h1_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("# "):
                h1_idx = i
                break
        subtitle = ""
        if h1_idx != -1 and h1_idx + 1 < len(lines):
            next_line = lines[h1_idx + 1].strip()
            if next_line and not next_line.startswith("#"):
                subtitle = next_line
                if "subtitle" not in metadata:
                    metadata["subtitle"] = subtitle

    # Split document by slide delimiters: '## ' or '---' (slide separator)
    slide_chunks = _split_into_slide_chunks(normalized)

    for chunk in slide_chunks:
        if not chunk.strip():
            continue
        slide = _parse_single_slide(chunk)
        if slide:
            slides.append(slide)

    return metadata, slides


def _split_into_slide_chunks(text: str) -> list[str]:
    """Split text into raw slide chunks using ## headers or --- horizontal rules."""
    lines = text.split("\n")
    chunks: list[str] = []
    current_chunk: list[str] = []

    for line in lines:
        # Check for H2 slide header
        if line.startswith("## "):
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
            current_chunk.append(line)
        # Check for horizontal rule slide separator '---'
        elif line.strip() == "---" and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def _parse_single_slide(chunk: str) -> Slide | None:
    """Parse a single slide chunk into a Slide model."""
    lines = chunk.strip().split("\n")
    if not lines:
        return None

    slide = Slide()
    content_lines: list[str] = []

    # First line might be title: ## Title: Subtitle or ## Title
    first_line = lines[0].strip()
    if first_line.startswith("## "):
        header = first_line[3:].strip()
        if ":" in header:
            t, st = header.split(":", 1)
            slide.title = t.strip()
            slide.subtitle = st.strip()
        elif " - " in header:
            t, st = header.split(" - ", 1)
            slide.title = t.strip()
            slide.subtitle = st.strip()
        else:
            slide.title = header
        content_lines = lines[1:]
    elif first_line.startswith("# "):
        # H1 title chunk: if it only contains the document title/subtitle, don't generate duplicate body frame
        body_non_empty = [l for l in lines[1:] if l.strip()]
        if not body_non_empty:
            return None
        slide.title = first_line[2:].strip()
        content_lines = lines[1:]
    else:
        slide.title = "Overview"
        content_lines = lines

    # Check for code blocks
    code_match = re.search(r"```([a-zA-Z0-9_-]*)\n(.*?)```", "\n".join(content_lines), flags=re.DOTALL)
    if code_match:
        slide.layout = "code"
        slide.is_fragile = True
        slide.code_lang = code_match.group(1).strip()
        slide.code_content = code_match.group(2)
        # Remove code from lines to parse any remaining bullets
        cleaned_text = "\n".join(content_lines).replace(code_match.group(0), "")
        content_lines = cleaned_text.strip().split("\n")

    # Check for 2-column dividers: ::: columns / ::: column or | left | right | or Left: / Right:
    full_content = "\n".join(content_lines)
    if "::: column" in full_content or "---col---" in full_content or "|||" in full_content:
        slide.layout = "columns"
        slide.columns = _extract_columns(full_content)
        return slide

    # Check for block callouts: > [!NOTE], > [!ALERT], > [!TIP], > [!EXAMPLE]
    block_match = re.search(r">\s*\[!(NOTE|TIP|ALERT|WARNING|EXAMPLE|IMPORTANT)\]\s*(.*)", full_content)
    if block_match:
        slide.layout = "block"
        kind = block_match.group(1).upper()
        custom_title = block_match.group(2).strip()
        if kind in ["ALERT", "WARNING"]:
            slide.block_type = "alertblock"
            slide.block_title = custom_title or "Alert"
        elif kind == "EXAMPLE":
            slide.block_type = "exampleblock"
            slide.block_title = custom_title or "Example"
        else:
            slide.block_type = "block"
            slide.block_title = custom_title or "Key Takeaway"

        # Gather block content lines, skipping the callout header line
        b_content: list[str] = []
        for line in content_lines:
            line_str = line.strip()
            if line_str.startswith(">"):
                if re.match(r"^>\s*\[!", line_str):
                    continue  # Skip header line that provided block_title
                cleaned = re.sub(r"^>\s*", "", line_str).strip()
                if cleaned:
                    b_content.append(cleaned)
            elif line_str:
                slide.paragraphs.append(line_str)
        slide.block_content = b_content
        return slide

    # Standard bullet points & paragraphs (preserving multi-line environments)
    i = 0
    while i < len(content_lines):
        line = content_lines[i]
        line_s = line.strip()
        if not line_s:
            i += 1
            continue
        # Speaker notes
        if line_s.lower().startswith("note:"):
            slide.notes = line_s[5:].strip()
            i += 1
            continue
        # Check for LaTeX environment start \begin{...}
        env_match = re.match(r"^\\begin\{([a-zA-Z0-9_\*]+)\}", line_s)
        if env_match:
            env_name = env_match.group(1)
            env_lines = [line_s]
            i += 1
            while i < len(content_lines):
                cur_line = content_lines[i]
                cur_s = cur_line.strip()
                if cur_s:
                    env_lines.append(cur_s)
                if f"\\end{{{env_name}}}" in cur_s:
                    i += 1
                    break
                i += 1
            slide.paragraphs.append("\n".join(env_lines))
            continue
        # Bullet items
        if line_s.startswith(("- ", "* ", "+ ")) or re.match(r"^\d+\.\s+", line_s):
            bullet = re.sub(r"^([-\*+]|\d+\.)\s+", "", line_s)
            slide.bullets.append(bullet)
            i += 1
        else:
            slide.paragraphs.append(line_s)
            i += 1

    return slide


def _extract_columns(content: str) -> list[list[str]]:
    """Extract columns from column-delimited markdown."""
    col_parts: list[str] = []
    if "::: column" in content:
        # Strip container opening tag
        cleaned = re.sub(r":::\s*columns\b", "", content)
        # Split on ::: column with optional width argument (e.g. 0.48 or 0.5\textwidth)
        raw_cols = re.split(r":::\s*column(?:\s+[\d\.]+\w*)?", cleaned)
        # Strip any closing :::
        col_parts = [c.replace(":::", "").strip() for c in raw_cols if c.strip()]
    elif "---col---" in content:
        col_parts = [c.strip() for c in content.split("---col---") if c.strip()]
    elif "|||" in content:
        col_parts = [c.strip() for c in content.split("|||") if c.strip()]

    result: list[list[str]] = []
    for part in col_parts:
        items: list[str] = []
        for line in part.split("\n"):
            line_s = line.strip()
            if line_s and not line_s.startswith(":::"):
                items.append(line_s)
        if items:
            result.append(items)

    # Ensure at least 2 columns
    while len(result) < 2:
        result.append([])

    return result
