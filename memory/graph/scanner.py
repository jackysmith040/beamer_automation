"""
NeuroWiki Auto-Scanner v9.0 — Stable & Scalable Edition
========================================================

Scans the entire neurowiki directory tree, builds a force-directed graph
manifest (nodes + links), and bakes all markdown documents into a single
brain_data.js file for 100% offline browser usage.

Usage:
    python3 graph/scanner.py              # standard scan
    python3 graph/scanner.py --audit      # verbose output for debugging

Node ID strategy:
    Relative path from BASE_DIR (e.g. "neocortex/left_hemisphere/note.md").
    Can be overridden per-file with frontmatter:  neuron_id: custom-id

Link strategy (priority order):
    1. Explicit [[WikiLinks]] in content  → type: "wiki"
    2. corpus_callosum frontmatter key    → type: "callosum"
    3. Auto sibling chain (sorted) within each hemisphere cluster → type: "sibling"

Scalability guarantees:
    - Each file is read exactly once
    - Link deduplication is O(1) via a set of sorted pairs
    - Folder exclusions prevent binary/system file crashes
    - Handles vaults of 10,000+ notes without modification
"""

import os
import json
import re
import sys
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
GRAPH_DIR   = Path(__file__).resolve().parent
BASE_DIR    = GRAPH_DIR.parent.parent
OUTPUT_FILE = GRAPH_DIR / "brain_data.js"
SETTINGS_FILE = GRAPH_DIR / "settings.toml"

# ── Files/folders to skip ──────────────────────────────────────────────────
SKIP_DIRS = {
    ".git", ".github", "node_modules", "__pycache__",
    "graph",          # scanner lives here — skip libs/output
    "templates",      # blueprints, not knowledge nodes
    ".obsidian",
    "workspaces",
    "assets",
    "playground",
    ".agents",
}
SKIP_FILES = {
    "README.md",       # repo readme, not a knowledge node
}

# ── Core documents baked for the Hub (START_HERE.html) ────────────────────
BAKED_DOCS = [
    "memory/neocortex/INDEX.md",
    "memory/wiki/README.md",
    "CONSCIENCE.md",
    "memory/episodic_log.md",
]


# ══════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════

def read_file(path: Path) -> str:
    """Read a file safely, returning an error string on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"Error: {exc}"


def parse_frontmatter(content: str) -> dict:
    """
    Extract YAML/TOML-style frontmatter between --- delimiters.
    Returns a dict of key: value pairs. Values are always strings.
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return {}
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip().strip("\"'")
        elif "=" in line:
            key, _, val = line.partition("=")
            meta[key.strip()] = val.strip().strip("\"'")
    return meta


def parse_toml_settings(path: Path) -> dict:
    """Parse a simple TOML settings file into nested dicts."""
    settings = {"visuals": {}, "colors": {}, "physics": {}}
    if not path.exists():
        return settings
    current = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            if current not in settings:
                settings[current] = {}
        elif "=" in line and current:
            key, _, raw = line.partition("=")
            val = raw.strip().strip("\"'")
            if val.lower() == "true":
                val = True
            elif val.lower() == "false":
                val = False
            else:
                try:
                    val = float(val) if "." in val else int(val)
                except ValueError:
                    pass
            settings[current][key.strip()] = val
    return settings


def cluster_for(rel_path: str) -> str:
    """Map a relative file path to its brain cluster name."""
    if "left_hemisphere" in rel_path:
        return "left_hemisphere"
    if "right_hemisphere" in rel_path:
        return "right_hemisphere"
    if "wiki" in rel_path:
        return "wiki"
    return "unknown"


def extract_summary(content: str, meta: dict) -> str:
    """
    Return a short plain-text summary.
    Uses 'summary' frontmatter if present, else the first non-heading paragraph.
    """
    if "summary" in meta:
        return meta["summary"][:300]
    # Strip frontmatter
    body = re.sub(r"^---.*?---\s*\n", "", content, flags=re.DOTALL)
    # Remove headings and blank lines, take first real paragraph
    lines = [l for l in body.splitlines() if l.strip() and not l.startswith("#")]
    return " ".join(lines)[:300]


# ══════════════════════════════════════════════════════════════════════════
# MAIN SCAN
# ══════════════════════════════════════════════════════════════════════════

def scan(audit: bool = False) -> None:
    nodes: list[dict] = []
    links: list[dict] = []

    # ── Pass 1: collect every markown file and build id → file_path index ──
    #    Reading each file only ONCE.
    file_map: dict[str, Path] = {}      # rel_path → Path
    content_map: dict[str, str] = {}    # rel_path → raw content
    meta_map: dict[str, dict] = {}      # rel_path → parsed frontmatter
    id_map: dict[str, str] = {}         # node_id  → rel_path (for link resolution)

    for root, dirs, files in os.walk(BASE_DIR):
        root_path = Path(root)
        # Prune excluded directories in-place (prevents descent)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)

        for fname in sorted(files):     # sorted → deterministic output
            if not fname.endswith(".md"):
                continue
            if fname in SKIP_FILES:
                continue

            fpath    = root_path / fname
            rel      = str(fpath.relative_to(BASE_DIR))
            content  = read_file(fpath)
            meta     = parse_frontmatter(content)
            node_id  = meta.get("neuron_id", meta.get("page_id", rel))

            if node_id in id_map:
                print(f"  [WARN] Duplicate node id '{node_id}' in '{rel}' "
                      f"(already mapped to '{id_map[node_id]}'). Skipping.", file=sys.stderr)
                continue

            file_map[rel]    = fpath
            content_map[rel] = content
            meta_map[rel]    = meta
            id_map[node_id]  = rel

    # Reverse lookup: rel_path → node_id
    path_to_id: dict[str, str] = {v: k for k, v in id_map.items()}

    # ── Pass 2: build nodes & explicit links ────────────────────────────────
    link_pairs: set[tuple[str, str]] = set()    # dedup set

    def add_link(src: str, tgt: str, ltype: str) -> None:
        """Add a link only if both endpoints exist and pair is new."""
        if tgt not in id_map:
            return
        key = (src, tgt) if src < tgt else (tgt, src)   # undirected dedup
        if key not in link_pairs:
            link_pairs.add(key)
            links.append({"source": src, "target": tgt, "type": ltype})

    for rel in sorted(file_map):
        content = content_map[rel]
        meta    = meta_map[rel]
        node_id = path_to_id[rel]

        nodes.append({
            "id":           node_id,
            "label":        meta.get("title", Path(rel).stem),
            "group":        cluster_for(rel),
            "path":         rel,
            "weight":       int(meta.get("synaptic_weight", 40)),
            "is_blindspot": meta.get("blindspot", "false").lower() == "true",
            "summary":      extract_summary(content, meta),
        })

        # [[WikiLinks]] — match full path or just stem
        for raw in re.findall(r"\[\[([^\]]+)\]\]", content):
            target_stem = raw.split("/")[-1].replace(".md", "")
            # Try exact id match first
            if raw in id_map:
                add_link(node_id, raw, "wiki")
            else:
                # Find node whose stem matches
                candidates = [nid for nid in id_map if Path(nid).stem == target_stem]
                for c in candidates:
                    add_link(node_id, c, "wiki")

        # corpus_callosum frontmatter
        if "corpus_callosum" in meta:
            for target_ref in meta["corpus_callosum"].split(","):
                target_ref = target_ref.strip()
                if target_ref in id_map:
                    add_link(node_id, target_ref, "callosum")
                else:
                    stem = Path(target_ref).stem
                    for nid in id_map:
                        if Path(nid).stem == stem:
                            add_link(node_id, nid, "callosum")

        if audit:
            print(f"  [NODE] {node_id}  group={cluster_for(rel)}")

    # ── Pass 3: auto-structural sibling links ──────────────────────────────
    #    Connect sorted siblings within each cluster so the graph is always
    #    connected.  Uses a deterministic sort (alphabetical by id) so the
    #    output is identical on every run.
    by_cluster: dict[str, list[str]] = {}
    for n in nodes:
        by_cluster.setdefault(n["group"], []).append(n["id"])

    for cluster_id_list in by_cluster.values():
        sorted_ids = sorted(cluster_id_list)
        for i in range(len(sorted_ids) - 1):
            add_link(sorted_ids[i], sorted_ids[i + 1], "sibling")

    # ── Bake core documents ────────────────────────────────────────────────
    docs: dict[str, str] = {}
    for doc_rel in BAKED_DOCS:
        full = BASE_DIR / doc_rel
        docs[doc_rel] = read_file(full)

    # Also bake every scanned .md so the visualizer can show content on click
    for rel, content in content_map.items():
        if rel not in docs:
            docs[rel] = content

    # ── Write output ───────────────────────────────────────────────────────
    settings = parse_toml_settings(SETTINGS_FILE)
    payload  = {
        "nodes":    nodes,
        "links":    links,
        "settings": settings,
        "docs":     docs,
    }

    js = f"// Axon Brain Data — auto-generated by scanner.py v9.0\n" \
         f"// Do not edit manually. Run: python3 graph/scanner.py\n" \
         f"window.BRAIN_DATA = {json.dumps(payload, indent=2, ensure_ascii=False)};\n"

    OUTPUT_FILE.write_text(js, encoding="utf-8")

    print(f"Scan complete - {len(nodes)} nodes | {len(links)} links | "
          f"{len(docs)} documents baked -> {OUTPUT_FILE.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    audit_mode = "--audit" in sys.argv
    if audit_mode:
        print(f"[AUDIT MODE] Scanning {BASE_DIR}")
    scan(audit=audit_mode)
