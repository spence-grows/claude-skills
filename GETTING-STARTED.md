# Getting started

A library of Claude Code skills I've built across frog / Invent engagements and some personal projects, packaged so anyone can use them. If you share or adapt them, please keep the attribution pointing back to this repo. Improvements welcome.

Two ways in: the **design-craft** plugin installs in one step; everything else is standalone skills you grab individually.

**Install the design plugin:**

```
/plugin marketplace add spence-grows/claude-skills
/plugin install design-craft@spencer-scott-skills
```

**Grab a standalone skill:** clone the repo and copy the folder you want into `~/.claude/skills/` (commands go in `~/.claude/commands/`). Full index is in the [README](README.md).

---

## 🎨 The design system — how it works & how it's built

This is the centerpiece. It codifies how we actually run bespoke design into Claude Code, so the AI works with discipline instead of drifting toward generic AI-startup output. Five pieces:

1. **A 9-stage playbook** — frame → research → plan → draft → verify → audit → perf → ship. The spine of a design session, each stage with its tools and a "skip if" guard.
2. **A project "design-discipline" skill (template)** — your protected aesthetic posture: fonts, palette, anti-patterns to refuse, reference exemplars, accessibility floor. You author one per project from the scaffold. This is really critical — I got this wrong on my first few projects and things got generic.
3. **Optional per-"direction" skills (template)** — a named aesthetic (e.g. glass / editorial) that pairs with the discipline on different surfaces.
4. **A 5-dimension critique rubric** — Philosophy / Hierarchy / Craft / Function / Originality, with ship / no-ship bands. The gate before merge. This is basically how I got Claude to assess its own output and score it against generic slop.
5. **A tool inventory** — the skills, MCPs, and CLIs the playbook leans on (token extraction, screenshot-verify, motion, etc.).

**How it was built:** extracted from my personal project work — I pulled the repeatable parts of the process, made them brand-agnostic, and turned each into a reusable skill or template. It's designed to compound: every audit that surfaces a durable principle gets folded back into the discipline skill. The shared scaffolding (playbook + rubric) stays constant; the per-project discipline skill is what you fill in.

---

## 🧩 The skills — what each is & when to use it

### In the design-craft plugin

- **design-process** — the design system above. *Use whenever you're building or refreshing a real UI/surface and want distinctive, disciplined output.*
- **invent-exco-branding** — Capgemini Invent NA slide formatting (fonts, colors, layout, logo/footer, dark & light). *Use when creating, editing, or QA-ing any Invent PowerPoint: ExCo decks, strategy decks. Internal-only.*

### Workflow (standalone)

- **session-handoff** — a structured end-of-session summary (decisions, changes, open threads). *Use before clearing context or handing a thread to a teammate / fresh agent.*
- **setup-project-permissions** — writes a no-prompt allow list for a project. *Use when you're tired of approving every command and want flow.* Some things really don't need a permission prompt (e.g. reading or editing a file within the project folder).
- **ingest-document** — vision-ingests decks/PDFs/Figma frames into a searchable knowledge base (captions diagrams, not just text). *Use to capture the thinking in a deck so it's searchable later.* (Needs a KB backend — I use Voyager; `setup-project-knowledge-base` covers standing one up.)
- **setup-project-knowledge-base** — onboards an engagement into a searchable corpus (transcripts, client docs, research). *Use at the start of a new engagement so nothing gets lost.* (Needs a KB backend.)
- **/tidy** (command) — reports branch/worktree health and chats to archive. *Use to clean up a messy workspace.*

### Scaling Claude (power-user methodology)

- **token-efficient-delegation** — playbook for model tiering, subagent delegation, and prompt-cache hygiene. *Use when planning multi-step work or watching token cost.* This was important for managing my token spend before the limits went up.
- **claude-as-llm** — run batch LLM tasks through your Max plan instead of the metered API. *Use for large batch jobs with a defined output schema (classify, enrich, summarize, extract).*
- **subagent-fanout** — high-throughput parallel subagent dispatch that preserves the prompt-cache discount. *Use when N independent slices of one task should run in parallel — e.g. large-scale enrichment or ingestion where each agent works its own batch of rows.*
- **row-merge** — safe methodology for merging duplicate rows in a database. *Use when deduping records without losing data.*
- **scrape-and-rehost** — bulk-fill a database column from a third-party site, idempotently. *Use when backfilling assets (logos, images, facts) at scale.*

---

Happy to walk anyone through setup — just reach out.
