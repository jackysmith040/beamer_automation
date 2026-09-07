"""
agent_helper.reset
Safe, atomic workspace reset utility for the Beamer & Thesis Automation Pipeline.
Allows starting fresh on a new beamer presentation or thesis without deleting
the tectonic compiler, cached fonts, or template overrides.
"""

import argparse
from datetime import datetime
from pathlib import Path
import shutil
from typing import Any
import zipfile


def reset_workspace(
    root_dir: str | Path = ".",
    backup: bool = True,
    keep_templates: bool = True,
    clean_inbox: bool = False,
    archive_dir: str | Path = "archive",
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Safely reset the automation workspace so a new project can begin.

    Args:
        root_dir: Workspace root directory.
        backup: If True, creates a timestamped zip backup in archive/ before wiping.
        keep_templates: If True, leaves template_override/ intact.
        clean_inbox: If True, resets INBOX.md to a fresh template.
        archive_dir: Directory where backups are stored.
        dry_run: If True, only reports what would be done without modifying files.

    Returns:
        dict containing status, archive path, and lists of reset folders.
    """
    root = Path(root_dir).resolve()
    arch_path = root / archive_dir
    
    report: dict[str, Any] = {
        "status": "success",
        "backup_created": None,
        "directories_cleared": [],
        "directories_initialized": [],
        "dry_run": dry_run,
    }

    dirs_to_clean = ["input", "digestion", "output"]
    if not keep_templates:
        dirs_to_clean.append("template_override")

    # 1. OPTIONAL BACKUP CREATION
    if backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = arch_path / f"project_backup_{timestamp}.zip"
        if dry_run:
            print(f"[DRY-RUN] Would create backup zip: {backup_filename.name}")
        else:
            arch_path.mkdir(parents=True, exist_ok=True)
            items_to_backup = [root / d for d in dirs_to_clean if (root / d).exists()]
            if (root / "INBOX.md").exists():
                items_to_backup.append(root / "INBOX.md")

            with zipfile.ZipFile(backup_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
                for item in items_to_backup:
                    if item.is_file():
                        zipf.write(item, item.name)
                    elif item.is_dir():
                        for file in item.rglob("*"):
                            if file.is_file():
                                rel_path = file.relative_to(root)
                                zipf.write(file, str(rel_path))

            report["backup_created"] = str(backup_filename)
            print(f"[RESET] Backup saved to: {backup_filename.name}")

    # 2. CLEAR DIRECTORIES
    for d_name in dirs_to_clean:
        target = root / d_name
        if target.exists():
            report["directories_cleared"].append(d_name)
            if dry_run:
                print(f"[DRY-RUN] Would clear directory: {d_name}/")
            else:
                shutil.rmtree(target)
                target.mkdir(parents=True, exist_ok=True)
                print(f"[RESET] Cleared: {d_name}/")

    # 3. REINITIALIZE CLEAN WORKSPACE STRUCTURE
    new_subdirs = [
        root / "input" / "beamer",
        root / "input" / "thesis",
        root / "input" / "assets",
        root / "digestion",
        root / "output",
    ]
    if not keep_templates:
        new_subdirs.append(root / "template_override")

    if dry_run:
        for sd in new_subdirs:
            print(f"[DRY-RUN] Would initialize directory: {sd.relative_to(root)}/")
        print("[DRY-RUN COMPLETE] No files were modified.")
    else:
        for sd in new_subdirs:
            sd.mkdir(parents=True, exist_ok=True)
            report["directories_initialized"].append(str(sd.relative_to(root)))

        # Add helpful guidance README to input
        input_readme = root / "input" / "README.md"
        input_readme.write_text(
            "# Input Directory\n\n"
            "Drop your project files here to start automation:\n\n"
            "- `input/beamer/`: Place your draft `.tex`, `.md`, or notes for Beamer slides.\n"
            "- `input/thesis/`: Place your draft `.tex` or chapter files for the Thesis.\n"
            "- `input/assets/`: Place your images, diagrams, and figures here.\n",
            encoding="utf-8",
        )

        # 4. OPTIONAL INBOX RESET
        if clean_inbox:
            inbox_file = root / "INBOX.md"
            inbox_file.write_text(
                "# INBOX\n\n"
                "Add your new instructions, ideas, or files here.\n",
                encoding="utf-8",
            )
            print("[RESET] Reinitialized INBOX.md")

        print("[RESET COMPLETE] Automation reset successfully. Ready for a new Beamer or Thesis project!")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reset the Beamer & Thesis automation pipeline for a fresh project."
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating a zip backup of the current project before resetting.",
    )
    parser.add_argument(
        "--clear-templates",
        action="store_true",
        help="Also clear the template_override/ folder (templates preserved by default).",
    )
    parser.add_argument(
        "--clean-inbox",
        action="store_true",
        help="Reset INBOX.md to a blank state.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without modifying the filesystem.",
    )

    args = parser.parse_args()
    reset_workspace(
        backup=not args.no_backup,
        keep_templates=not args.clear_templates,
        clean_inbox=args.clean_inbox,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
