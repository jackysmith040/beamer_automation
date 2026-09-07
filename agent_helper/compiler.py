"""
agent_helper.compiler
LaTeX compiler execution, portable Tectonic bootstrapping, log parsing, and self-healing.
"""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any
import urllib.request
import zipfile


def find_latex_compiler() -> tuple[str | None, str]:
    """Locate an available LaTeX compiler on the system or in local bin."""
    # 1. Check local bin/ for bootstrapped tectonic.exe
    local_bin = Path(__file__).resolve().parent / "bin"
    local_tectonic = local_bin / ("tectonic.exe" if sys.platform == "win32" else "tectonic")
    if local_tectonic.exists():
        return str(local_tectonic), "tectonic"

    # 2. Check system PATH for pdflatex, xelatex, tectonic, latexmk
    for cmd in ["tectonic", "pdflatex", "xelatex", "latexmk"]:
        found = shutil.which(cmd)
        if found:
            return found, cmd

    return None, "none"


def get_tectonic_download_info() -> tuple[str, str, str]:
    """Determine the correct Tectonic release URL, archive type, and executable name for the current OS."""
    import platform

    os_type = platform.system().lower()
    machine = platform.machine().lower()
    version = "0.15.0"
    base_url = f"https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40{version}"

    if os_type == "windows":
        return f"{base_url}/tectonic-{version}-x86_64-pc-windows-msvc.zip", "zip", "tectonic.exe"
    elif os_type == "darwin":
        # macOS: Apple Silicon (arm64/aarch64) or Intel (x86_64)
        arch = "aarch64-apple-darwin" if ("arm" in machine or "aarch64" in machine) else "x86_64-apple-darwin"
        return f"{base_url}/tectonic-{version}-{arch}.tar.gz", "tar.gz", "tectonic"
    elif "linux" in os_type:
        # Linux (Ubuntu, Debian, etc.): x86_64 or aarch64
        arch = "aarch64-unknown-linux-musl" if ("arm" in machine or "aarch64" in machine) else "x86_64-unknown-linux-musl"
        return f"{base_url}/tectonic-{version}-{arch}.tar.gz", "tar.gz", "tectonic"
    else:
        raise OSError(f"Unsupported operating system: {os_type}")


def bootstrap_tectonic(target_dir: Path | None = None) -> str | None:
    """Download and extract portable standalone Tectonic binary for zero-dependency PDF generation across Windows, macOS, and Linux."""
    import tarfile

    dest_dir = target_dir or (Path(__file__).resolve().parent / "bin")
    dest_dir.mkdir(parents=True, exist_ok=True)
    exe_name = "tectonic.exe" if sys.platform == "win32" else "tectonic"
    dest_exe = dest_dir / exe_name

    if dest_exe.exists():
        return str(dest_exe)

    try:
        url, arc_type, bin_name = get_tectonic_download_info()
        archive_path = dest_dir / f"tectonic_download.{arc_type}"

        print(f"[COMPILER] Bootstrapping native Tectonic compiler from {url}...")
        urllib.request.urlretrieve(url, archive_path)

        if arc_type == "zip":
            with zipfile.ZipFile(archive_path, "r") as z:
                z.extract(bin_name, dest_dir)
        elif arc_type == "tar.gz":
            with tarfile.open(archive_path, "r:gz") as tar:
                tar.extract(bin_name, dest_dir)

        if archive_path.exists():
            archive_path.unlink()

        if sys.platform != "win32" and dest_exe.exists():
            # Ensure executable permission on Unix (macOS / Linux)
            os.chmod(dest_exe, 0o755)

        return str(dest_exe)
    except Exception as exc:
        archive_path = dest_dir / "tectonic_download"
        for candidate in dest_dir.glob("tectonic_download*"):
            candidate.unlink(missing_ok=True)
        print(f"[COMPILER WARNING] Could not auto-download native Tectonic: {exc}")
        return None


def compile_tex(tex_path: str, output_dir: str = "output", timeout_seconds: int = 180) -> dict[str, Any]:
    """Compile a .tex file to PDF using available or bootstrapped compiler."""
    tex_file = Path(tex_path).resolve()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    compiler_path, compiler_type = find_latex_compiler()

    if not compiler_path:
        # Attempt to bootstrap tectonic
        bootstrapped = bootstrap_tectonic()
        if bootstrapped:
            compiler_path = bootstrapped
            compiler_type = "tectonic"

    if not compiler_path:
        return {
            "success": False,
            "compiler": "none",
            "pdf_path": None,
            "log": "No LaTeX compiler found (pdflatex, xelatex, tectonic). .tex source was generated successfully.",
            "errors": [{"message": "Compiler missing from system PATH"}],
        }

    cmd: list[str] = []
    if compiler_type == "tectonic":
        cmd = [compiler_path, "--outdir", str(out_dir), str(tex_file)]
    elif compiler_type == "pdflatex" or compiler_type == "xelatex":
        cmd = [compiler_path, "-interaction=nonstopmode", f"-output-directory={out_dir}", str(tex_file)]
    elif compiler_type == "latexmk":
        cmd = [compiler_path, "-pdf", f"-outdir={out_dir}", str(tex_file)]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(tex_file.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
        )
        combined_log = proc.stdout + "\n" + proc.stderr
        pdf_name = tex_file.stem + ".pdf"
        pdf_path = out_dir / pdf_name

        success = proc.returncode == 0 and pdf_path.exists()
        errors = parse_latex_errors(combined_log) if not success else []

        return {
            "success": success,
            "compiler": compiler_type,
            "pdf_path": str(pdf_path) if pdf_path.exists() else None,
            "log": combined_log,
            "errors": errors,
            "returncode": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "compiler": compiler_type,
            "pdf_path": None,
            "log": "Compilation timed out after 60 seconds.",
            "errors": [{"message": "Timeout expired"}],
        }
    except Exception as exc:
        return {
            "success": False,
            "compiler": compiler_type,
            "pdf_path": None,
            "log": f"Execution error: {exc}",
            "errors": [{"message": str(exc)}],
        }


def parse_latex_errors(log_text: str) -> list[dict[str, Any]]:
    """Parse standard LaTeX log errors and line numbers for self-healing."""
    errors: list[dict[str, Any]] = []
    lines = log_text.splitlines()

    for idx, line in enumerate(lines):
        line_s = line.strip()
        if line_s.startswith("!") or line_s.startswith("error:"):
            msg = line_s.lstrip("!").replace("error:", "").strip()
            # Look for line number e.g. "l.45" or "file.tex:84:"
            line_num = None
            colon_match = re.search(r":(\d+):", line_s)
            if colon_match:
                line_num = int(colon_match.group(1))
            else:
                for lookahead in lines[idx : idx + 5]:
                    match = re.search(r"l\.(\d+)", lookahead)
                    if match:
                        line_num = int(match.group(1))
                        break
            errors.append({"message": msg, "line": line_num})

    return errors


def self_heal_tex(tex_code: str, errors: list[dict[str, Any]]) -> str:
    """Attempt rule-based self-healing on broken LaTeX source."""
    healed = tex_code

    for err in errors:
        msg = err.get("message", "").lower()
        
        # 1. Missing fragile option on verbatim frame
        if "semiverbatim" in msg or "verbatim" in msg or "fragile" in msg:
            healed = re.sub(
                r"\\begin\{frame\}(?!\[[^\]]*fragile[^\]]*\])",
                r"\\begin{frame}[fragile]",
                healed,
            )

        # 2. Misplaced alignment tab character &
        if "misplaced alignment tab" in msg or "alignment tab character &" in msg or "&" in msg:
            # Escape unprotected & (not \&)
            healed = re.sub(r"(?<!\\)&", r"\&", healed)

        # 3. Unescaped underscore in math or text
        if "missing $ inserted" in msg or "undefined control sequence" in msg:
            # Check for naked underscores in text that aren't preceded by backslash
            healed = re.sub(r"(?<!\\)_(?!.*(?:\$|\\\]))", r"\_", healed)

        # 4. Unescaped percent sign
        if "runaway argument" in msg or "unterminated" in msg:
            healed = re.sub(r"(?<!\\)%", r"\%", healed)

        # 5. Commands before documentclass
        if "documentclass" in healed:
            doc_idx = healed.find(r"\documentclass")
            if doc_idx > 0:
                prefix = healed[:doc_idx].strip()
                healed = healed[doc_idx:]
                # Insert prefix after documentclass
                newline_after = healed.find("\n")
                healed = healed[:newline_after + 1] + f"\n{prefix}\n" + healed[newline_after + 1:]

        # 6. Unclosed document environment
        if "\\begin{document} ended by" in msg:
            if not healed.strip().endswith("\\end{document}"):
                healed += "\n\\end{document}\n"

    return healed
