---
name: setup-project-knowledge-base
description: Use when onboarding a new client project/engagement into a local-first knowledge corpus — standing up a searchable knowledge base so call transcripts, client docs, desk research, and cross-project material are captured and queryable. Triggers: "set up a knowledge base for <project>", "do the KB setup for this project", "ingest this client's docs/transcripts", "make this project searchable".
---

# Setting Up a Project Knowledge Base

## Overview

Don't build new infrastructure per engagement. **Onboard each new project into one existing
local-first knowledge corpus.** The reference backend is the **`copilot`** KB tool
(`uv run copilot`, LanceDB + an embedding model, hybrid retrieval, a multi-project registry at
`~/.copilot/projects.json`) — adapt the commands to your own KB if you use a different one.
The *pattern* (four content buckets → durable searchable corpus, kept separate from session
memory) is the reusable part.

**Two layers, kept distinct:**
- **Corpus (the KB)** = the durable, searchable archive of *everything* — the four buckets
  below. System of record.
- **Claude Code memory** = small distilled facts for in-session reasoning. Points *at* the
  corpus; never duplicates it.

**Four buckets → KB primitives:**
| Bucket | Mechanism |
|---|---|
| 1. Call/meeting transcripts (e.g. a Notion DB) | `sync-notion` + a **Project** property = the project's display name |
| 2. Client docs (decks/PDF/Word/Excel, often read-only SharePoint) | `add-source` watch-folders, vision applied |
| 3. Desk research | a folder *you own* (inside the project folder), auto-ingested |
| 4. Cross-project material | a `SHARED` scope, auto-included in every `query -p` |

## Requirements / adapt this

Assumes a KB CLI with `add-source`, `sync-folders`, `sync-notion`, `vision`, and `query`
commands. Set `COP` to your KB repo (its `.env` is **cwd-relative** — run everything from the
repo root):

```sh
COP="$HOME/path/to/copilot"
```

## When to use
- A new engagement starts and you want nothing to get lost / to refer back to prior calls and docs.
- "Set this up like we did for the last client."

When NOT: one-off doc lookups (just `query`); editing the KB tool itself.

## Conventions
Run everything as `cd "$COP" && uv run copilot ...`. Pick a slug `PID` (e.g. `acme-redesign`)
and a human `DISPLAY` (e.g. `ACME Redesign`).

## Setup sequence

1. **Create the project + register client-doc folders** (read-only SharePoint is fine — ingest
   only reads). Set `--name`/`--desc` **once, on the first call only**:
   ```sh
   cd "$COP" && uv run copilot add-source PID "/path/to/client/folderA" --name "DISPLAY" --desc "<one line: client, LOB, goal>" --no-vision
   cd "$COP" && uv run copilot add-source PID "/path/to/client/folderB" --no-vision   # NO --name on later calls
   ```
   Single files can't be folder-ingested (see Gotcha 3) — for a lone file in an otherwise-excluded folder, either register its parent subfolder (if clean) or use `vision <file>` (Gotcha 4).

2. **Desk-research folder** — create `<project folder>/working docs/desk-research/` with a
   README. It's inside the project watch-folder and the walk is recursive, so it auto-ingests.
   No separate source needed.

3. **Apply vision to the visual files** (decks/PDFs). Vision is OFF by default and the
   content-hash skip means a later `--vision` run does nothing on already-text-ingested files
   — you **must** `--force`. Target just the visual files (cheap), don't `--force` the whole
   corpus:
   ```sh
   cd "$COP" && find "/path/to/client" -type f \( -iname '*.pdf' -o -iname '*.pptx' \) -print0 \
     | while IFS= read -r -d '' f; do uv run copilot vision "$f" -p PID --force; done
   ```

4. **Transcripts (Notion):** add a Select property named exactly **`Project`** to the Call
   Transcripts DB, with an option labeled **exactly `DISPLAY`** (matched case-insensitively to
   the project's display_name/slug; a non-matching value silently *creates a junk project*).
   Tag calls going forward. Then:
   ```sh
   cd "$COP" && uv run copilot sync-notion --default-project inbox      # NEVER default to PID — see Gotcha 1
   ```

5. **Daily freshness (launchd).** Copy `launchd-sync.sh` + `launchd-sync.plist` from this skill,
   substitute `PID`/paths/username, then load. The wrapper MUST `cd "$COP"` and set `PATH`
   (launchd has a minimal env). See the templates in this skill dir.

6. **Cleanup mis-routed transcripts** (LLM routing is noisy): a `reroute` command sweeps
   `inbox` into projects; `kb_inventory.py PID` lists docs; `kb_move.py inbox <doc_id…>` evicts
   non-project calls. Both tools are in this skill dir.

7. **Consume + bridge.** Self-serve: `query -p PID --transcripts --answer`, `live -p PID`. For
   Claude Code, clone a `/PID-recall` command (a thin wrapper over that query) into
   `<project>/.claude/commands/`.

8. **Document:** add a "Knowledge system" section to the project CLAUDE.md and a project memory
   pointer, so future sessions know the corpus is the system of record.

## Gotchas (the ones that bite — learned by execution, not by reading code)

| Gotcha | Reality |
|---|---|
| `sync-notion --default-project PID` | **Re-pollutes** the project: every untagged page dumps into it. Always default to `inbox`; let the Notion `Project` tag route real calls. |
| Vision skipped after text ingest | Content-hash skip means `--vision` no-ops on already-ingested files. Use `vision <file> --force` (or `sync-folders --vision --force`). |
| `add-source`/`sync-folders` on a single file | Silently no-ops (it `rglob`s *inside* the path). Use the `vision <file>` command for single files. |
| `add-source --name` on later calls | Overwrites the **project display_name** (it's per-project, not per-source). Set `--name`/`--desc` only on the first call; breaking the display_name also breaks Notion routing. |
| KB is single-writer (LanceDB) | Never run two ingest/sync commands concurrently (incl. background passes vs. the launchd job). Serialize. |
| Re-tagging an existing Notion page | Dedup is on the page **body** hash, not properties → a property-only change is "skipped (unchanged)" and does NOT re-route. Tags route NEW/changed pages; fix historical ones with `reroute`/`kb_move`. |
| `notion_filter` in projects.json | **Dead config — never read.** Routing keys off the page's own `Project` property. Don't set it. |
| `query` flags | It's `--transcripts` and `--answer` (no `--scope`; default scope already = `project+shared`, so SHARED/cross-project is included). |
| First `--vision` run | Slow (per-page model calls); content-hash cached after, so daily re-syncs are cheap. |
| Editing projects.json fields with no command | Only `add-source` (watch_folders) and `notion-writeback` mutate via CLI; for `display_name`/etc. use the Registry API: `Registry.load(); p=r.get(PID); p.x=...; r.upsert(p); r.save()`. |
