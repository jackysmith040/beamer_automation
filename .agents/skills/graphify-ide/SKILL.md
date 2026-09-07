---
name: graphify-ide
description: "Custom graphify workflow that runs inline in the IDE without API keys and generates scripts for the user to execute. Trigger: /graphify-ide"
---

# /graphify-ide

When the user types `/graphify-ide`, follow this specific workflow based on past user preferences:

## 1. No API Keys & Inline Semantic Extraction
The user does **not** want to use external API keys (like `GEMINI_API_KEY` or `GOOGLE_API_KEY`) for semantic extraction.
Instead of skipping semantic extraction or trying to dispatch background subagents, you (the Agent IDE) must perform the semantic extraction inline. Review the core conceptual documents (e.g. architecture notes, decision logs) and inject a lightweight semantic JSON object into the build process.

## 2. Provide Scripts, Do Not Execute
The user prefers to run the commands themselves. Do **not** use the terminal tools to execute the graphify pipeline automatically without asking.
Instead, write a single, robust Python script (e.g., `run_graphify.py`) that handles the entire pipeline:
- Detection (`graphify.detect`)
- Structural/AST Extraction (`graphify.extract`)
- Merging the inline semantic JSON you created
- Building the graph, clustering, and generating the HTML and Markdown reports.

After writing the script, simply give the user the terminal commands to run the script (e.g., `python3 run_graphify.py`).

## 3. Dependencies
Always ensure the virtual environment has the required dependencies, explicitly keeping in mind `graphifyy` and `graphifyy[sql]`.

## 4. Local Slash Command Integration
Skills should be placed in `~/.gemini/config/skills/` (global) so they can be natively triggered via their slash command name.
