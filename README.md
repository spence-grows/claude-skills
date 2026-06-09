# Spencer Scott — Claude Code Skills

A small library of Claude Code skills I built for design-strategy and consulting work at frog / Capgemini Invent. Sharing them as we roll Claude Code out more broadly.

Two ways in:
- **`design-craft`** — an installable plugin bundling my 9-stage design process and Capgemini Invent slide branding.
- **Standalone skills** — everything else, as individual skills you can grab à la carte.

> Please keep attribution intact if you fork or adapt these — I put real effort into them. Issues / improvements welcome back here so everyone benefits.

---

## The design plugin — `design-craft`

Install once via the marketplace:

```text
/plugin marketplace add spence-grows/claude-skills
/plugin install design-craft@spencer-scott-skills
```

| Skill | What it does |
|---|---|
| **design-process** | The cohesive **9-stage design playbook** (frame → research → plan → draft → verify → audit → perf → ship) + 5-dimension critique rubric + scaffolds for per-project design-discipline / design-direction skills — a disciplined workflow that resists generic AI aesthetics. |
| **invent-exco-branding** | Capgemini Invent NA PowerPoint branding — fonts, colors, layout dims, text hierarchy, logo/footer rules for dark & light slides. |

---

## Standalone skills

Grab only what you want. Clone the repo and copy the skill folder into your skills directory:

```sh
git clone https://github.com/spence-grows/claude-skills.git
cp -R claude-skills/skills/session-handoff ~/.claude/skills/   # repeat for any skill below
```

(Commands live in `commands/` — copy `commands/tidy.md` into `~/.claude/commands/`.)

### Workflow

| Skill | What it does |
|---|---|
| **session-handoff** | Structured end-of-session handoff so a fresh agent or teammate can continue seamlessly. |
| **setup-project-permissions** | One-shot project allow-list so Claude Code stops prompting for routine bash / web / file-edit ops. |
| **ingest-document** | Vision-ingest decks/PDFs/Figma frames into a searchable KB — captions diagrams, not just text. *(needs a KB backend — see skill)* |
| **setup-project-knowledge-base** | Onboard a new engagement into a local-first searchable corpus (transcripts, client docs, desk research). *(needs a KB backend — see skill)* |
| **tidy** *(command: `/tidy`)* | Report branch/worktree health and suggest Claude chats to archive. |

### Scaling Claude (power-user methodology)

| Skill | What it does |
|---|---|
| **token-efficient-delegation** | Token-optimization playbook — model tiering, subagent delegation, prompt-caching hygiene, context lifecycle. |
| **claude-as-llm** | Run batch LLM tasks through Claude Code (your Max plan) instead of paying per-token API costs. |
| **subagent-fanout** | High-throughput parallel subagent dispatch with the static-prefix discipline that preserves the prompt-cache discount. |
| **row-merge** | Safe methodology for merging duplicate rows in a relational DB — six safety rails, winner-picker, severity rubric. |
| **scrape-and-rehost** | Bulk-fill a DB column from a third-party site — rate-limited fetch, extract, re-host, idempotent write-back. |

---

## Notes

- The two KB skills (`ingest-document`, `setup-project-knowledge-base`) wrap a local-first knowledge-base CLI (the `copilot` tool is the reference backend). They've been generalized — swap the commands for your own KB if you use a different one. The reusable part is the *pattern*.
- `invent-exco-branding` encodes Capgemini Invent NA brand conventions; keep it internal.

Authored by **Spencer Scott**. MIT licensed — see [LICENSE](LICENSE).
