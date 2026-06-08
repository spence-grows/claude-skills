---
name: token-efficient-delegation
description: Token-optimization playbook for planning sessions — model tiering (Haiku/Sonnet/Opus/Aider/Gemini Code Assist), subagent delegation, prompt-caching hygiene, context lifecycle. Trigger when planning a multi-PR roadmap, assigning executors to tasks, or when the user mentions token budget, cost, "use cheaper tools," "be token efficient," or wants to diversify away from Claude-only execution.
---

# Token-efficient delegation

Distilled from the 2026 token-optimization writeups (BuildToLaunch, GitConnected, affaan-m/everything-claude-code) and the official Anthropic prompt-caching docs. Use this skill in the planning phase: every task in a roadmap should have an explicit executor assignment from the table below, not a default to Opus.

## Why this matters

Claude re-reads the entire conversation on every turn. By message 50, you're paying to re-read 49 prior messages before any new work. Most cost overruns aren't bad prompts — they're context bloat plus mismatched model tiers.

## Rule 1 — Tier the model to the task

| Task type | Tool | Why |
|---|---|---|
| Architecture, multi-file design, ambiguity resolution | **Opus (main session)** | Only model worth the spend on judgment calls |
| Implementation across 1–3 files with clear spec | **Sonnet subagent** (`Agent` with `model: sonnet`) | ~60% cheaper than Opus, plenty for spec-driven coding |
| Mechanical edits (rename, reformat, single-file change with exact instructions) | **Haiku subagent** or **Aider with DeepSeek/Gemini** | Haiku ~80% cheaper than Opus; Aider is fully external (zero Claude quota) |
| In-VS-Code edits the user wants to drive themselves | **Gemini Code Assist** | Free tier, doesn't touch Claude quota at all |
| File reads / "where is X" / "what does Y do" | **Explore subagent** | Returns a summary, not raw file contents — main context stays clean |

When delegating from inside Claude Code, be explicit: `Agent({ subagent_type: "general-purpose", model: "haiku", prompt: "..." })`.

## Rule 2 — Delegate heavy reads to subagents

Any task that would have me read 3+ files or 15K+ tokens of source goes to an Explore or general-purpose subagent. The subagent's accumulated context dies with it; only the summary lands in main context. Never duplicate work — if a subagent is researching, don't also grep myself.

## Rule 3 — Self-contained prompts for external tools

Aider and Gemini Code Assist don't see the planning conversation. When handing off to them:
- Write the prompt as a complete unit: file paths, line numbers, exact change, why it matters
- Reference `AGENTS.md` for project conventions (both tools import it via `.aider.conf.yml` / `GEMINI.md`)
- Don't write "based on the plan" or "based on findings" — paste the actual instruction

## Rule 4 — One topic per chat

When switching to an unrelated task, `/clear` and start fresh. For continuity within a topic, `/compact` at logical breakpoints (after exploration, after a bug is fixed, before pivoting). Never compact mid-implementation. The `/session-handoff` skill is the right pattern when a topic genuinely needs to span sessions.

## Rule 5 — Specific file paths over folder vagueness

"Edit `src/components/SiteHeaderNav.tsx:168-179` to convert the `<Link>` to a DropdownMenu" costs ~50 input tokens. "Update the nav to add a dropdown" forces Claude to grep, list, and read until it finds the right file — easily 10× the cost.

## Rule 6 — Extended thinking budget

For non-reasoning tasks (renames, mechanical edits, content generation), set `MAX_THINKING_TOKENS=10000` (or 0). Default is ~32K — most edits don't need it. Toggle thinking *before* sending the message; toggling mid-conversation invalidates the messages cache.

## Rule 7 — Prompt caching hygiene

The Anthropic API caches in the hierarchy `tools → system → messages`; a change at any level invalidates that level and below. Practical implications inside Claude Code:
- Don't toggle fast mode, web search, or extended thinking mid-task — each toggle invalidates the messages cache
- Long-running agent loops (e.g. enrichment fan-out, scheduled `/loop` jobs) benefit from 1-hour cache TTL on the system prompt; 5-min default for normal sessions
- Prompt cache 5-min TTL means: sleeping >300s in a `/loop` blows the cache. Stay <270s for hot work, or commit to ≥1200s for genuinely idle waits — never split the difference

## Rule 8 — CLI over MCP when both exist

`gh pr view 34` returns the PR JSON. The GitHub MCP returns the same data wrapped in tool-definition tokens that stay in context forever. Same for `supabase`, `aws`, `vercel`. Default to CLI.

## Rule 9 — Skills load on demand

Don't list-and-load skills reflexively. Only invoke the ones the current task needs. The `Skill` tool's system reminder is informational — it's not a checklist.

## Rule 10 — `.claudeignore` and CLAUDE.md hygiene

- `.claudeignore` should exclude `node_modules/`, `.next/`, `dist/`, `build/`, `*.log`, `.env*`. (Verify the project has this.)
- CLAUDE.md is re-read every turn. Keep it under ~500 tokens; link to `AGENTS.md` for the full runbook.

## Quick checklist before delegating

- [ ] Is this mechanical? → Aider or Gemini Code Assist
- [ ] Is this single-file with clear spec? → Haiku subagent
- [ ] Is this multi-file with judgment? → Sonnet subagent
- [ ] Is this architectural / ambiguous? → keep on Opus
- [ ] Did I write the prompt as if the executor has zero context? (For external tools, yes.)
- [ ] Am I duplicating a subagent's work?

## How to apply this in a planning session

When producing a multi-PR roadmap, every PR gets an explicit "**Executor:**" line. Don't default to "I'll do it" — that means Opus. Examples:

> **PR 1 — Quick wins.** Executor: Gemini Code Assist (in VS Code), one edit at a time. Each change is single-file, single-purpose; perfect for free-tier sidebar edits with the user driving.

> **PR 6 — Schema rework.** Executor: Opus (this session) for the design + migration; Sonnet subagent for the route restructuring; Gemini for individual file moves.

The user can then disagree with the assignment ("no, do PR 4 yourself"), but the default surfaces the cheap path.
