---
name: setup-project-permissions
description: Use when the user wants to stop being prompted for bash, web search/fetch, or file-edit operations in a project, set up .claude/settings.local.json with their default no-prompt allow list, copy permissions from another project, or get the same blanket allows they have elsewhere applied to the current repo.
---

# Setup Project Permissions

## Overview

One-shot config skill that ensures the current project's `.claude/settings.local.json` contains your canonical no-prompt allow list — broad blanket permissions (Bash, Web, file edits) plus the MCP servers and Skills you always-allow.

**Always writes to `settings.local.json`, never `settings.json`** — the local file is gitignored by default, so blanket permissions stay personal and never leak into team config.

## When to use

- "Set up permissions for this project"
- "Stop prompting me for bash/web/edit"
- "Apply my default permissions here"
- "Copy the permissions I have in [other project] over"
- Starting work in a fresh clone or new repo

When NOT to use:
- Adding a *single* narrow permission ("allow `gh pr merge`") — just edit `settings.local.json` directly or use `update-config`.
- Configuring hooks, env vars, or other settings.json fields — that's `update-config`.
- Removing/tightening permissions — this skill only adds.

## Workflow

1. **Check target.** Verify the user is in a project root (look for `.git` or `package.json`). If not, ask which directory.
2. **Locate file.** Path is `<repo-root>/.claude/settings.local.json`. Create the `.claude/` directory if missing.
3. **Read existing.** If the file exists, Read it. If not, treat existing `allow` as `[]`.
4. **Verify gitignore.** Check `.gitignore` for `.claude/settings.local.json` or `.claude/settings.local*`. If neither matches, surface this to the user before writing — blanket permissions in a tracked file would leak.
5. **Merge.** Union the existing `allow` array with the canonical list below. Preserve all existing entries (project-specific paths, API-token commands, etc. stay put). Dedupe by exact string match.
6. **Write.** Write the merged JSON back, pretty-printed with 2-space indent. Preserve other top-level keys (`additionalDirectories`, hooks, etc.) untouched.
7. **Report.** Print a short summary: N entries added, M already present, total now K. Mention if `.gitignore` needed attention.

## Canonical allow list

```json
{
  "permissions": {
    "allow": [
      "Bash(*)",
      "WebSearch",
      "WebFetch",
      "Edit(**)",
      "Write(**)",
      "MultiEdit(**)",
      "NotebookEdit(**)",
      "Read(**)",

      "mcp__plugin_context-mode_context-mode__ctx_execute",
      "mcp__plugin_context-mode_context-mode__ctx_batch_execute",
      "mcp__plugin_context-mode_context-mode__ctx_execute_file",
      "mcp__plugin_context-mode_context-mode__ctx_fetch_and_index",
      "mcp__plugin_context-mode_context-mode__ctx_search",
      "mcp__plugin_context-mode_context-mode__ctx_upgrade",

      "mcp__plugin_claude-mem_mcp-search__smart_search",
      "mcp__plugin_claude-mem_mcp-search__smart_outline",

      "mcp__claude_ai_Notion__notion-search",
      "mcp__claude_ai_Notion__notion-fetch",
      "mcp__claude_ai_Notion__notion-create-pages",
      "mcp__claude_ai_Notion__notion-create-view",
      "mcp__claude_ai_Notion__notion-update-page",

      "Skill(gsd-resume-work)",
      "Skill(gsd-resume-work:*)",
      "Skill(superpowers:subagent-driven-development)",
      "Skill(superpowers:subagent-driven-development:*)",
      "Skill(superpowers:brainstorming)",
      "Skill(superpowers:brainstorming:*)",
      "Skill(superpowers:writing-plans)",
      "Skill(superpowers:writing-plans:*)",
      "Skill(schedule)",
      "Skill(schedule:*)"
    ]
  }
}
```

## Quick reference

| Group | Entries | Why blanket |
|-------|---------|-------------|
| Bash | `Bash(*)` | You run scripts/builds/tooling constantly; per-command prompts kill flow |
| Web | `WebSearch`, `WebFetch` | Research is always allowed |
| File edits | `Edit(**)`, `Write(**)`, `MultiEdit(**)`, `NotebookEdit(**)`, `Read(**)` | You work across the whole tree |
| context-mode MCP | 6 tools | Default research/exec path in his global CLAUDE.md |
| claude-mem MCP | smart_search, smart_outline | Memory recall |
| Notion MCP | search, fetch, create-pages, create-view, update-page | Default Notion workflow |
| Skills | gsd-resume-work, superpowers:{brainstorming, writing-plans, subagent-driven-development}, schedule | Skills he invokes routinely |

## Safety rails

- **Never write to `settings.json`** (the committed file). Always `settings.local.json`.
- **Never strip existing entries** — only add. The user has project-specific paths and tokens in there.
- **Never include API tokens or secrets** in the canonical list. If you see one in *existing* entries, leave it alone; just don't add new ones.
- **Refuse if `settings.local.json` is tracked by git.** Run `git check-ignore -v .claude/settings.local.json` — if it returns no match, stop and warn the user that adding `Bash(*)` to a tracked file gives every collaborator the same blanket. Offer to add the gitignore rule first.
- **Preserve formatting on existing keys.** Use Edit (not Write) when the file already exists and only the `allow` array needs updating; this avoids reformatting `additionalDirectories` or other sections.

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Writing to `settings.json` instead of `settings.local.json` | Always target `.local`. Blanket permissions are personal. |
| Replacing the existing `allow` array instead of merging | Union, dedupe by exact string. Existing entries stay. |
| Adding the list without checking `.gitignore` | Run `git check-ignore -v` first; warn if tracked. |
| Copy-pasting API-token-bearing commands across projects | Tokens are project-scoped; don't carry them. |
| Updating without telling the user what changed | Always report: "added N, already had M, total K." |

## Updating the canonical list

When you say "add X to my default permissions" or "I always want Y allowed everywhere," update the **Canonical allow list** section of this file. The list is the source of truth — next invocation in any project pulls the new entry.