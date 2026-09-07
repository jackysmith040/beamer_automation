"""
agent_helper.normalizer
Composable text normalization and metadata extraction utility.
"""

import re
from typing import Any


def normalize_text(raw_text: str) -> str:
    """Normalize line breaks, BOM, and trailing whitespace."""
    if not raw_text:
        return ""
    # Strip UTF-8 BOM if present
    text = raw_text.lstrip("\ufeff")
    # Normalize CRLF and CR to LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace on each line
    lines = [line.rstrip() for line in text.split("\n")]
    # Strip leading/trailing empty lines
    return "\n".join(lines).strip()


def extract_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract YAML-style frontmatter from markdown text if present.
    
    Returns:
        tuple of (metadata_dict, remaining_body_text)
    """
    metadata: dict[str, Any] = {}
    normalized = normalize_text(text)
    
    if not normalized.startswith("---"):
        return metadata, normalized
        
    parts = normalized.split("---", 2)
    if len(parts) < 3:
        return metadata, normalized
        
    frontmatter_block = parts[1].strip()
    body = parts[2].strip()
    
    for line in frontmatter_block.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().lower()
            val = val.strip().strip("\"'")
            metadata[key] = val
            
    return metadata, body
