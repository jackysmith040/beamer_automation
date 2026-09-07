#!/usr/bin/env bash
# ==============================================================================
# Beamer & Thesis Automation Pipeline - Reset Script (macOS & Linux)
# ==============================================================================
# Safely resets the workspace for a fresh project:
# - Archives current work into archive/ (with timestamp)
# - Cleans input/, digestion/, and output/
# - Preserves compiler binaries and core system configurations
# ==============================================================================

set -e

# Detect Python / uv
if command -v uv >/dev/null 2>&1; then
    PYTHON_CMD="uv run python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "[ERROR] Neither 'uv' nor 'python3' was found on your PATH." >&2
    exit 1
fi

$PYTHON_CMD reset_pipeline.py "$@"
