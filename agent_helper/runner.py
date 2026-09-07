"""
agent_helper.runner
Unified orchestrator for the Beamer Automation Pipeline.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from agent_helper.normalizer import normalize_text, extract_frontmatter
from agent_helper.parser import parse_slides, Slide
from agent_helper.template_engine import extract_preamble, detect_archetypes, inject_content
from agent_helper.slide_builder import build_presentation
from agent_helper.reviewer import review_presentation
from agent_helper.compiler import compile_tex, self_heal_tex


def run_pipeline(
    input_file: str,
    template_file: str,
    output_dir: str = "output",
    digestion_dir: str = "digestion",
    max_retries: int = 3,
) -> dict[str, Any]:
    """Execute the full 4-stage pipeline."""
    input_path = Path(input_file).resolve()
    template_path = Path(template_file).resolve()
    out_dir = Path(output_dir).resolve()
    dig_dir = Path(digestion_dir).resolve()

    out_dir.mkdir(parents=True, exist_ok=True)
    dig_dir.mkdir(parents=True, exist_ok=True)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    report: dict[str, Any] = {
        "status": "in_progress",
        "input": str(input_path),
        "template": str(template_path),
        "stages": {},
    }

    print(f"\n[PIPELINE START] Processing {input_path.name} with template {template_path.name}...")

    # ── STAGE 1: INGESTION & NORMALIZATION ─────────────────────────────────────
    raw_content = input_path.read_text(encoding="utf-8")
    normalized = normalize_text(raw_content)
    metadata, slides = parse_slides(normalized)
    
    # Save sandbox digestion artifacts
    digestion_json = dig_dir / f"{input_path.stem}_digested.json"
    slide_dicts = [s.to_dict() for s in slides]
    digestion_json.write_text(
        json.dumps({"metadata": metadata, "slides": slide_dicts}, indent=2),
        encoding="utf-8",
    )
    print(f"-> [STAGE 1: DIGESTION] Parsed {len(slides)} slides into sandbox: {digestion_json.name}")
    report["stages"]["digestion"] = {
        "slide_count": len(slides),
        "metadata": metadata,
        "sandbox_file": str(digestion_json),
    }

    # ── STAGE 2: TEMPLATE OVERRIDE & BUILD ─────────────────────────────────────
    template_code = template_path.read_text(encoding="utf-8")
    archetypes = detect_archetypes(template_code)
    slides_latex = build_presentation(metadata, slides, archetypes)
    full_tex = inject_content(template_code, slides_latex, metadata)
    print(f"-> [STAGE 2: TEMPLATE OVERRIDE] Injected content into {template_path.stem} (Theme: {archetypes['theme']})")

    # ── STAGE 3: REVIEW STAGE ──────────────────────────────────────────────────
    review_res = review_presentation(full_tex, slides)
    review_json = dig_dir / f"{input_path.stem}_review.json"
    review_json.write_text(json.dumps(review_res.to_dict(), indent=2), encoding="utf-8")
    print(f"-> [STAGE 3: REVIEW] Syntax valid: {review_res.valid} | Warnings: {len(review_res.warnings)} | Errors: {len(review_res.errors)}")
    report["stages"]["review"] = review_res.to_dict()

    # ── STAGE 4: OUTPUT & COMPILATION (WITH SELF-HEALING) ──────────────────────
    output_tex = out_dir / f"{input_path.stem}.tex"
    output_tex.write_text(full_tex, encoding="utf-8")

    compile_res = compile_tex(str(output_tex), output_dir=str(out_dir))
    attempt = 1

    while not compile_res["success"] and attempt < max_retries and compile_res["compiler"] != "none":
        print(f"-> [STAGE 4: COMPILATION RETRY #{attempt}] Triggering self-healing on LaTeX errors...")
        healed_tex = self_heal_tex(full_tex, compile_res["errors"])
        if healed_tex == full_tex:
            print("   No further automatic healing rules matched.")
            break
        full_tex = healed_tex
        output_tex.write_text(full_tex, encoding="utf-8")
        compile_res = compile_tex(str(output_tex), output_dir=str(out_dir))
        attempt += 1

    report["stages"]["compilation"] = {
        "success": compile_res["success"],
        "compiler": compile_res["compiler"],
        "pdf_path": compile_res.get("pdf_path"),
        "tex_path": str(output_tex),
        "attempts": attempt,
    }

    if compile_res["success"]:
        print(f"-> [STAGE 4: SUCCESS] Generated PDF: {compile_res.get('pdf_path')}")
        report["status"] = "success"
    elif compile_res["compiler"] == "none":
        print(f"-> [STAGE 4: NOTE] .tex generated at {output_tex.name}. (Compiler not installed on PATH)")
        report["status"] = "tex_generated"
    else:
        print(f"-> [STAGE 4: WARNING] Compilation failed after {attempt} attempts.")
        report["status"] = "compilation_error"

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Beamer Slide Automation Pipeline")
    parser.add_argument("--input", "-i", required=True, help="Path to input markdown/text file")
    parser.add_argument("--template", "-t", required=True, help="Path to Beamer LaTeX template (.tex)")
    parser.add_argument("--output-dir", "-o", default="output", help="Output directory for .tex and .pdf")
    parser.add_argument("--digestion-dir", "-d", default="digestion", help="Digestion sandbox directory")

    args = parser.parse_args()
    try:
        res = run_pipeline(
            input_file=args.input,
            template_file=args.template,
            output_dir=args.output_dir,
            digestion_dir=args.digestion_dir,
        )
        sys.exit(0 if res["status"] in ["success", "tex_generated"] else 1)
    except Exception as exc:
        print(f"[FATAL ERROR] {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
