# Graphify IDE Workflow Documentation

This document captures the design decisions and workflow preferences established for running the `graphify` pipeline.

## Core Decisions

1. **API Key Avoidance**:
   We bypass the use of external LLM API keys for bulk semantic extraction. Instead, we leverage the power of the Agent IDE's native context window. The agent reads the most important documentation files directly and manually constructs the semantic knowledge graph JSON.

2. **User-Controlled Execution**:
   Rather than the agent running opaque bash commands in the background, the agent generates a self-contained, robust Python script (`run_graphify.py`). This script orchestrates the detection, extraction, and building phases. The user retains full control and visibility by executing this script manually in their terminal.

3. **Dependencies**:
   The workflow requires the `graphifyy` package, and we ensure compatibility with database extraction by noting the `graphifyy[sql]` dependency.

4. **Slash Command Integration**:
   By placing these instructions in `~/.gemini/config/skills/graphify-ide/SKILL.md`, the workflow is natively registered as a slash command (`/graphify-ide`). This ensures the agent will instantly recall these exact steps whenever triggered.
