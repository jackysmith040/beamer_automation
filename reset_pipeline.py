#!/usr/bin/env python3
"""
Convenience CLI entry point to reset the Beamer & Thesis automation workspace.

Usage:
    python reset_pipeline.py                 # Safely backs up to archive/ and resets
    python reset_pipeline.py --no-backup     # Resets without creating a backup
    python reset_pipeline.py --dry-run       # Preview what will be reset
"""

from agent_helper.reset import main

if __name__ == "__main__":
    main()
