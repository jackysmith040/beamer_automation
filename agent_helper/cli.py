"""
agent_helper.cli
Modern, robust Typer-powered CLI for the Beamer & Thesis Automation Framework.
Provides beautiful, vibrant Rich terminal output for humans and
structured, machine-readable JSON schemas (--json) for AI agents.
"""

import json
from pathlib import Path
import subprocess
import sys
from typing import Optional

# Ensure UTF-8 output encoding across Windows, macOS, and Linux
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from agent_helper.runner import run_pipeline
from agent_helper.reviewer import review_presentation
from agent_helper.compiler import compile_tex, self_heal_tex, find_latex_compiler
from agent_helper.reset import reset_workspace
from agent_helper.normalizer import extract_frontmatter
from agent_helper.parser import parse_slides
from agent_helper.slide_builder import build_presentation

app = typer.Typer(
    name="beamer",
    help="Agent-Driven, Zero-Config LaTeX & Beamer Automation Framework",
    add_completion=False,
)
console = Console(highlight=False)
err_console = Console(stderr=True, highlight=False)


@app.command(name="build")
def build(
    input_file: Path = typer.Option(
        ...,
        "--input",
        "-i",
        help="Path to input Markdown or LaTeX draft file.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    template_file: Path = typer.Option(
        Path("template_override/modern_clean.tex"),
        "--template",
        "-t",
        help="Path to template LaTeX file.",
    ),
    output_dir: Path = typer.Option(
        Path("output"),
        "--output-dir",
        "-o",
        help="Directory to save final deliverables.",
    ),
    digestion_dir: Path = typer.Option(
        Path("digestion"),
        "--digestion-dir",
        "-d",
        help="Directory for AST sandbox digestion.",
    ),
    max_retries: int = typer.Option(
        3,
        "--max-retries",
        help="Maximum self-healing compiler retry passes.",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output structured JSON response for AI agents.",
    ),
    open_pdf: bool = typer.Option(
        False,
        "--open",
        help="Automatically open the compiled PDF upon success.",
    ),
) -> None:
    """Run the complete 4-stage automation pipeline (Input -> Digestion -> Override -> Output)."""
    if not as_json:
        console.print(
            Panel.fit(
                f"[bold cyan]🚀 Starting Beamer Automation Pipeline[/bold cyan]\n"
                f"[dim]Input:[/dim] {input_file}\n"
                f"[dim]Template:[/dim] {template_file}\n"
                f"[dim]Output Directory:[/dim] {output_dir}",
                border_style="cyan",
            )
        )

    try:
        report = run_pipeline(
            input_file=str(input_file),
            template_file=str(template_file),
            output_dir=str(output_dir),
            digestion_dir=str(digestion_dir),
            max_retries=max_retries,
        )
    except Exception as exc:
        if as_json:
            typer.echo(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        else:
            err_console.print(f"[bold red]❌ Pipeline Failed:[/bold red] {exc}")
        raise typer.Exit(code=1)

    if as_json:
        typer.echo(json.dumps(report, indent=2))
    else:
        status = report.get("status")
        if status in ["success", "tex_generated"]:
            pdf_path = report.get("stages", {}).get("compilation", {}).get("pdf_path")
            console.print(
                Panel.fit(
                    f"[bold green]✨ Pipeline Completed Successfully![/bold green]\n"
                    f"[bold white]PDF Output:[/bold white] {pdf_path or 'TeX generated'}",
                    border_style="green",
                )
            )
            if open_pdf and pdf_path and Path(pdf_path).exists():
                if sys.platform == "win32":
                    subprocess.run(["start", "", str(pdf_path)], shell=True)
                elif sys.platform == "darwin":
                    subprocess.run(["open", str(pdf_path)])
                else:
                    subprocess.run(["xdg-open", str(pdf_path)])
        else:
            err_console.print(f"[bold yellow]⚠️ Pipeline Finished with Status:[/bold yellow] {status}")


@app.command(name="review")
def review(
    file_path: Path = typer.Argument(
        ...,
        help="Path to Markdown (.md) or LaTeX (.tex) file to inspect.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output structured JSON response for AI agents.",
    ),
) -> None:
    """Run pre-flight AST validation, bracket checking, and environment linting."""
    content = file_path.read_text(encoding="utf-8")
    if file_path.suffix.lower() in [".md", ".markdown"]:
        meta, slides = parse_slides(content)
        tex_code = build_presentation(meta, slides)
        report = review_presentation(tex_code, slides=slides)
    else:
        report = review_presentation(content)

    rep_dict = report.to_dict()

    if as_json:
        typer.echo(json.dumps(rep_dict, indent=2))
        raise typer.Exit(code=0 if report.is_valid else 1)

    table = Table(title=f"Pre-flight Review: {file_path.name}", border_style="cyan")
    table.add_column("Check", style="bold white")
    table.add_column("Result", style="cyan")

    table.add_row("Syntax Valid", "[green]PASS[/green]" if report.is_valid else "[red]FAIL[/red]")
    table.add_row("Total Warnings", str(len(report.warnings)))
    table.add_row("Total Errors", str(len(report.errors)))

    console.print(table)

    if report.warnings:
        console.print("\n[bold yellow]Warnings:[/bold yellow]")
        for w in report.warnings:
            console.print(f"  • {w}")

    if report.errors:
        console.print("\n[bold red]Errors:[/bold red]")
        for e in report.errors:
            console.print(f"  • {e}")

    raise typer.Exit(code=0 if report.is_valid else 1)


@app.command(name="compile")
def compile_cmd(
    tex_file: Path = typer.Argument(
        ...,
        help="Path to .tex file to compile.",
        exists=True,
        file_okay=True,
        dir_okay=False,
    ),
    output_dir: Path = typer.Option(
        Path("output"),
        "--outdir",
        "-o",
        help="Output directory for the compiled PDF.",
    ),
    self_heal: bool = typer.Option(
        True,
        "--self-heal/--no-self-heal",
        help="Attempt self-healing syntax recovery if compilation fails.",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output structured JSON for AI agents.",
    ),
) -> None:
    """Compile any LaTeX presentation or thesis file using the zero-config Tectonic engine."""
    compiler_path, compiler_type = find_latex_compiler()

    if not as_json:
        console.print(f"[dim]Compiler:[/dim] [cyan]{compiler_type}[/cyan] ({compiler_path or 'auto-bootstrap'})")

    if self_heal:
        res = self_heal_tex(str(tex_file), str(output_dir))
    else:
        res = compile_tex(str(tex_file), str(output_dir))

    if as_json:
        typer.echo(json.dumps(res, indent=2))
    else:
        if res.get("status") == "success":
            console.print(f"[bold green]✔ Compilation Succeeded:[/bold green] {res.get('pdf')}")
        else:
            err_console.print(f"[bold red]✖ Compilation Failed:[/bold red] {res.get('errors')}")

    raise typer.Exit(code=0 if res.get("status") == "success" else 1)


@app.command(name="reset")
def reset_cmd(
    no_backup: bool = typer.Option(
        False,
        "--no-backup",
        help="Skip creating an archive backup before wiping.",
    ),
    clear_templates: bool = typer.Option(
        False,
        "--clear-templates",
        help="Also reset template_override/ (preserved by default).",
    ),
    clean_inbox: bool = typer.Option(
        False,
        "--clean-inbox",
        help="Reset INBOX.md to a fresh template.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview actions without touching the filesystem.",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output structured JSON for AI agents.",
    ),
) -> None:
    """Safely reset the automation workspace to start fresh on a new Beamer or Thesis project."""
    res = reset_workspace(
        backup=not no_backup,
        keep_templates=not clear_templates,
        clean_inbox=clean_inbox,
        dry_run=dry_run,
    )

    if as_json:
        typer.echo(json.dumps(res, indent=2))


@app.command(name="demo")
def demo(
    output_dir: Path = typer.Option(
        Path("output/demo"),
        "--output-dir",
        "-o",
        help="Directory to save the demo build.",
    ),
    as_json: bool = typer.Option(
        False,
        "--json",
        help="Output JSON for AI agents.",
    ),
) -> None:
    """Run an instant end-to-end sample build so newcomers can verify everything works in 5 seconds."""
    sample_md = Path("samples/beamer/sample_presentation.md").resolve()
    sample_tpl = Path("samples/templates/modern_clean.tex").resolve()

    if not sample_md.exists():
        # Fallback to template_override / input if samples not yet written
        sample_md = Path("input/sample_presentation.md").resolve()
        sample_tpl = Path("template_override/modern_clean.tex").resolve()

    if not as_json:
        console.print(
            Panel.fit(
                "[bold cyan]🎬 Running 5-Second Beamer Automation Demo[/bold cyan]\n"
                "Building high-fidelity presentation from pristine samples...",
                border_style="cyan",
            )
        )

    res = run_pipeline(
        input_file=str(sample_md),
        template_file=str(sample_tpl),
        output_dir=str(output_dir),
    )

    if as_json:
        typer.echo(json.dumps(res, indent=2))
    else:
        pdf_path = res.get("stages", {}).get("compilation", {}).get("pdf_path")
        console.print(
            Panel.fit(
                f"[bold green]✔ Demo Generated Successfully![/bold green]\n"
                f"[bold white]PDF Ready At:[/bold white] {pdf_path}",
                border_style="green",
            )
        )


@app.command(name="init")
def init_cmd(
    project_type: str = typer.Option(
        "beamer",
        "--type",
        "-t",
        help="Project type to initialize: 'beamer' or 'thesis'.",
    )
) -> None:
    """Initialize fresh starter templates in input/ for a student, lecturer, or researcher."""
    input_beamer = Path("input/beamer")
    input_thesis = Path("input/thesis")
    input_assets = Path("input/assets")

    input_beamer.mkdir(parents=True, exist_ok=True)
    input_thesis.mkdir(parents=True, exist_ok=True)
    input_assets.mkdir(parents=True, exist_ok=True)

    if project_type.lower() == "thesis":
        target = input_thesis / "thesis_draft.tex"
        if not target.exists():
            target.write_text(
                "\\documentclass[12pt,a4paper]{report}\n"
                "\\begin{document}\n"
                "\\title{Dissertation Title}\n"
                "\\author{Student Name}\n"
                "\\maketitle\n"
                "\\chapter{Introduction}\n"
                "Start writing your thesis here.\n"
                "\\end{document}\n",
                encoding="utf-8",
            )
        console.print(f"[bold green]✔ Initialized Thesis starter in:[/bold green] {target}")
    else:
        target = input_beamer / "presentation_draft.md"
        if not target.exists():
            target.write_text(
                "---\n"
                "title: Project Presentation\n"
                "author: Your Name\n"
                "institute: University Department\n"
                "theme: modern_clean\n"
                "---\n\n"
                "# Introduction\n"
                "- Welcome to the presentation\n"
                "- Core findings and deliverables\n",
                encoding="utf-8",
            )
        console.print(f"[bold green]✔ Initialized Beamer starter in:[/bold green] {target}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
