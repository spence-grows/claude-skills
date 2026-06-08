---
name: design-process
description: "Use when running a disciplined, bespoke design process in Claude Code — the 9-stage playbook (frame → research → plan → draft → verify → audit → perf → ship), the 5-dimension critique rubric, and scaffolds for authoring per-project design-discipline and per-direction skills. Ties the design-language vocabulary skills you author into a cohesive workflow that resists generic AI aesthetics. Triggers: 'run the design process', 'design playbook', 'set up design discipline for this project', 'author a design direction skill', 'critique/audit this UI against the rubric'."
---

# The 9-Stage Design Process

A stage-by-stage walkthrough for running a disciplined design session inside Claude Code. Stages 0–8. Each stage has a primary action, the tools to invoke, and a **skip if** guard.

This skill bundles the supporting pieces it references:
- [`critique-rubric.md`](critique-rubric.md) — the 5-dimension scoring rubric used in Stage 6.
- [`tool-inventory.md`](tool-inventory.md) — catalog of skills/MCPs/CLIs the playbook depends on.
- [`templates/design-discipline.skill.md`](templates/design-discipline.skill.md) — scaffold for a project's protected aesthetic posture.
- [`templates/design-direction.skill.md`](templates/design-direction.skill.md) — scaffold for a per-direction skill (e.g. glass / editorial / brutalist).
- [`templates/audit.md`](templates/audit.md) — scaffold for `docs/audits/YYYY-MM-DD-<surface>.md`.
- [`mcp-snippets/motion-studio.json`](mcp-snippets/motion-studio.json) — fragment to merge into a project's `.mcp.json`.

It assumes you've authored a project-specific design-discipline skill from [`templates/design-discipline.skill.md`](templates/design-discipline.skill.md). Where this document refers to "your discipline skill," it means that file. You draw directions from a vocabulary of named aesthetics — author each as a portable `design-<name>` skill (see [`tool-inventory.md`](tool-inventory.md)).

---

## Stage 0 — Pre-session sanity (~1 min)

- **Action:** Confirm what's installed via [`tool-inventory.md`](tool-inventory.md). Make sure your project-specific discipline skill exists in `.claude/skills/<project>-design-discipline/SKILL.md` and that its description is current enough for Claude Code's auto-discovery to pick it up.
- **Tools:** —
- **Skip if:** This is a copy tweak with no visual work.

## Stage 1 — Frame the work (15–30 min, non-negotiable for bespoke design)

- **Action:** Lock intent, audience, success criteria, and constraints *before any code is written.* The discipline skill auto-loads its protected-aesthetic posture and anti-patterns into context.
- **Tools:**
  - `superpowers:brainstorming` (must)
  - Your project's discipline skill (auto)
  - Any direction-specific skills you've authored (e.g. one per aesthetic direction)
- **Output:** A written brief — purpose, audience, success criteria, constraints, what you're explicitly **not** doing.
- **Skip if:** Pure bug fix with no design judgment.

## Stage 2 — Research reference sites (10–30 min)

- **Action:** Extract design tokens and design language from 3–5 reference sites you admire. Confirm your direction holds or surface a reason to evolve.
- **Tools:**
  - **designlang** — CLI: `npx designlang https://example.com --system-chrome -o /tmp/designlang-out`; or the MCP form ("use designlang to extract tokens from <url>")
  - Start from the cross-style top picks in your discipline skill's Reference Exemplars section.
  - Apply the **5-10-2-8 sourcing rule** — 5 search rounds, 10 candidates, pick 2 each ≥8/10 on craft.
- **Output:** Extracted token sketches + a 1-line "what we're stealing from each."
- **Skip if:** You've done this for the same surface within the past 2 weeks.

## Stage 3 — Plan with discipline (varies)

- **Action:** Lock aesthetic direction, color strategy, register. Plan the build steps.
- **Tools:**
  - `frontend-design` skill — forces explicit aesthetic direction; bans Inter/Roboto defaults
  - `superpowers:writing-plans` or `gsd-plan-phase` for multi-step work
  - Pick a **color strategy** explicitly: Restrained / Committed / Full-palette / Drenched
  - Pick the **register**: brand vs product
  - Apply the **scene-sentence test** to lock mood: write one sentence describing the surface as a physical scene. If you can't, the mood isn't locked yet.
- **Output:** A written plan (PLAN.md or checklist) with a chosen direction labeled (e.g. "D1" / "editorial-v2").
- **Skip if:** One-line CSS change to an existing pattern.

## Stage 4 — Draft (varies)

- **Action:** Write the CSS and HTML. Stay inside the editorial discipline; resist the AI-slop defaults the skill warns against.
- **Tools:**
  - `superpowers:subagent-fanout` if generating 3 layout variants in parallel — give each sub-agent a different aesthetic constraint, identical static prefix wins the cache discount.
  - For animation: `npm i motion` (when next touching the renderer), import from `motion/mini`, invoke `/motion` to look up the right pattern (requires Claude Code restart to discover the slash command after installing the Motion Studio MCP).
  - For marketing artifacts only (Reddit GIFs, fundraising deck, launch animation — *not* the live product surface): invoke `huashu-design`. If your discipline is editorial, clamp Huashu's Direction Advisor to philosophies `#01 / #03 / #10 / #17 / #18 / #19` to stay editorial.
- **Output:** Working CSS + HTML committed to a feature branch.

## Stage 5 — Verify visually (mandatory — the non-technical-reviewer protection)

- **Action:** Look at the rendered surface. Don't claim "done" without seeing it.
- **Today (manual):** Open the rendered URL in a browser, screenshot the relevant section, paste into chat for review.
- **Recommended install:** **Playwright MCP** lets Claude screenshot the rendered output itself and self-correct before showing you. Install: `claude mcp add playwright --scope project -- npx -y @playwright/mcp@latest`
- **Skip if:** Never. This is the explicit guard against "Claude says it's done; reviewer can't tell." If the project's design reviewer is non-technical, this stage is the safety net.

## Stage 6 — Audit before merge (mandatory for product-surface changes)

- **Action:** Run a second-opinion design audit before committing.
- **Tools:**
  - `/impeccable audit <surface>` — Impeccable's deterministic + LLM pass; outputs go to `docs/audits/`
  - `/motion-audit` if animation was touched
  - Apply the **5-dimension critique rubric** (see [`critique-rubric.md`](critique-rubric.md)) — total < 35 ships only with explicit caveat; **< 25 doesn't ship**.
  - Run the **two-altitude AI slop test** — category reflex + anti-reference reflex.
  - Format findings in **Before / After / Why** table.
- **Output:** A scored audit doc at `docs/audits/YYYY-MM-DD-<surface>.md` (template: [`templates/audit.md`](templates/audit.md)).
- **Skip if:** Change is <20 LOC and doesn't touch the rendered output.

## Stage 7 — Performance check (pre-prod only)

- **Action:** Confirm Core Web Vitals before shipping to prod.
- **Today (manual):** Run Lighthouse in Chrome DevTools by hand.
- **Recommended install:** **Chrome DevTools MCP** automates this. Install: `claude mcp add chrome-devtools --scope project -- npx -y chrome-devtools-mcp@latest`
- **Skip if:** Internal-only / non-production surface.

## Stage 8 — Ship

- **Action:** Final review and commit.
- **Tools:**
  - `/ultra-review` — cloud-sandbox parallel reviewer agents. Costs $ per run; reserve for non-trivial PRs.
  - Atomic commit via `gsd-quick`, the `commit-commands:commit` skill, or manual git.
  - Reference the rule or principle from your discipline skill that motivated the change in the commit message.
- **Output:** A merged PR with the audit and verification artifacts cross-linked.

---

## Empirical-input track (optional, parallel to the playbook)

When direction choice is ambiguous, build an **empirical mechanism** instead of arguing it out: ship pairwise-comparison mockups of candidate directions and rank them using a Bradley-Terry MLE model with tournament relegation for underperformers (a Supabase-backed Elo pairing UI is a reasonable reference implementation). Adopt this when you have >5 candidate directions and no obvious winner.

When you start Stage 1 on a redesign, **check the leaderboard first** if you've built one — if a direction is empirically winning, don't re-litigate it.

---

## Sanity checks on the process itself

- **If you find yourself skipping Stage 1 or Stage 5 repeatedly, something's wrong.** Those are the two stages that exist specifically to catch the failure modes ("I started coding without a brief" and "Claude said it was done but I never looked").
- **Stage 6 must not be optional once a surface is in production.** The 5-dimension rubric is the only thing standing between you and slow aesthetic drift toward shadcn defaults.
- **The discipline skill is a living document.** Every audit that lifts a new principle or reference exemplar belongs in the skill, not just in the audit doc. Otherwise the learnings don't compound.
