#!/bin/bash
# launchd-sync.sh — daily corpus sync for ONE project. Copy to ~/.copilot/bin/<PID>-sync.sh and edit PID.
# Critical: launchd has a minimal env, so we set PATH and cd into the copilot repo (the .env is cwd-relative).
PID="REPLACE_WITH_project_id"            # e.g. acme-redesign
COP="REPLACE_WITH_path_to_copilot_repo"  # e.g. $HOME/Documents/Claude/copilot
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
cd "$COP" || exit 1
mkdir -p "$HOME/.copilot/logs"
LOG="$HOME/.copilot/logs/$PID-sync.log"
echo "===== $(date '+%Y-%m-%d %H:%M:%S') $PID-sync START =====" >> "$LOG"
# Default untagged Notion pages to inbox (NEVER to the project — that re-pollutes it).
uv run copilot sync-notion  --default-project inbox     >> "$LOG" 2>&1
uv run copilot sync-folders --project "$PID" --vision   >> "$LOG" 2>&1
echo "===== $(date '+%Y-%m-%d %H:%M:%S') $PID-sync DONE  =====" >> "$LOG"
