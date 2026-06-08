---
description: Report branch/worktree health and suggest Claude chats to archive
argument-hint: [--push] [--archive]
---

Run the tidy-workspace script and show its output verbatim to the user.

```bash
bash ~/.claude/scripts/tidy-workspace.sh $ARGUMENTS
```

After the script runs:
- If any `claude/*` branches show `vs origin = local-only` or `+N/-0`, mention that `/tidy --push` will push them.
- If the "Archivable chat sessions" list is non-empty, mention that `/tidy --archive` will move them to `~/.claude/projects/.archive` (safe — skips anything active in the last 8 hours).
- If merged branches still have worktrees, point to `~/.claude/scripts/cleanup-claude-worktrees.sh --apply` as the destructive next step.

Do not run `--archive` or the cleanup script yourself — only surface the suggestions.
