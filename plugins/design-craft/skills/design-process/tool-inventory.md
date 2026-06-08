# Tool Inventory

The skills, MCPs, CLIs, and APIs the playbook depends on — the reference for what each tool does and when to invoke it. Install the third-party ones separately (links below).

---

## Skills

### Third-party (install separately)

| Tool | Source | Trigger | What it does |
|---|---|---|---|
| **impeccable** | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | `/impeccable audit <surface>`, `/impeccable polish`, `/impeccable critique`, `/impeccable shape` (+19 commands) | Deterministic + LLM design audit. 7 domain reference files, 27 anti-pattern rules. Author has real design-engineering pedigree |
| **huashu-design** | [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) | Auto-loads on prototyping/marketing-artifact prompts | 20 philosophies across 5 schools (Pentagram / iA / Müller-Brockmann / Kenya Hara etc.), Direction Advisor, parallel HTML demos, MP4/GIF export pipeline. Marketing artifacts only — not the production product surface |
| **emil-design-eng** | [emilkowalski/skill](https://github.com/emilkowalski/skill) | Case-by-case for animation review | Per-element duration table (Button 100-160 / Tooltip 125-200 / Dropdown 150-250 / Modal 200-500), 4 named easing curves, `:active scale(0.97)`, `@starting-style` mount pattern, mandated Before/After/Why review format |

### Built-in (always available, no install)

| Tool | Trigger | What it does |
|---|---|---|
| **frontend-design** | Invoke explicitly per redesign | Forces explicit aesthetic direction; bans Inter/Roboto defaults; pushes for distinctive output |
| **superpowers:brainstorming** | Before any creative work | Locks intent, audience, success criteria, constraints before code |
| **superpowers:subagent-fanout** | When generating N variants in parallel | Bit-identical static-prefix discipline wins the prompt-cache discount across sub-agents 2..N |
| **superpowers:writing-plans** | Multi-step task plans | Plan-first discipline with verification loops |
| **superpowers:verification-before-completion** | Before claiming done | Evidence before assertions; required for Stage 5 |

### Project-authored (you create these from templates)

| Tool | Template | What it does |
|---|---|---|
| **&lt;project&gt;-design-discipline** | [`templates/design-discipline.skill.md`](templates/design-discipline.skill.md) | The protected aesthetic posture for your specific project — fonts, palette, anti-patterns, reference exemplars |
| **&lt;project&gt;-&lt;direction&gt;** (optional, one per aesthetic direction) | [`templates/design-direction.skill.md`](templates/design-direction.skill.md) | A per-direction skill (e.g. "glass" / "editorial" / "brutalist") that pairs with the discipline skill on different surfaces |

### Portable design-language vocabulary (optional, growing library)

A set of skills named `design-<vocabulary>` that each capture a *named aesthetic vocabulary* — generic enough to drop into any project. They're the *language*; your project-direction skill is the *application*. You author these yourself (none ship in this plugin); the library is meant to grow as you ship new named aesthetics across projects.

Examples of the kind of vocabulary you'd capture: a dark-canvas "glass" register, a restrained motion-driven register, an editorial "service-brand" register — each authored once as `design-<name>` with its own visual thesis, tokens, and trigger keywords, then reused across projects.

**How to use these in a project:**

1. Author them once in `~/.claude/skills/design-<name>/SKILL.md`. They auto-discover by description across all your projects.
2. When a project needs a snapshot pinned at a specific version, copy the relevant `design-*` skill folder into the project's `.claude/skills/` instead of relying on the user-scope copy.
3. Your project-direction skill (e.g. `myproject-glass`) extends one of these — the vocabulary skill provides the language, your skill applies it to your tokens, surfaces, and constraints.

**The library is meant to grow.** Every time you ship a new named aesthetic across projects, author it as a portable `design-<name>` skill instead of a one-off project skill. Over time this becomes your personal pattern library.

---

## MCP servers

| Tool | Scope | Install | How to invoke |
|---|---|---|---|
| **Playwright MCP** | Project | `claude mcp add playwright --scope project -- npx -y @playwright/mcp@latest` | Headless browser control + screenshot loop. Closes the Stage 5 visual feedback loop |
| **Chrome DevTools MCP** | Project | `claude mcp add chrome-devtools --scope project -- npx -y chrome-devtools-mcp@latest` | Lighthouse, LCP/INP/CLS traces, network waterfalls. For Stage 7 perf audit |
| **Motion Studio MCP** | Project | Commit a `.mcp.json` fragment (see [`mcp-snippets/motion-studio.json`](mcp-snippets/motion-studio.json)) | `/motion` searches Motion's 330+ examples; `/motion-audit` reviews animation. Requires Claude Code restart to discover slash commands |
| **designlang** | User | `claude mcp add designlang --scope user -- npx -y designlang mcp` | Extracts DTCG design tokens + design language from any URL via Playwright. Used at Stage 2 |
| **Context7** *(optional)* | User | See [upstash/context7](https://github.com/upstash/context7) README | Up-to-date framework/library docs injected on demand |
| **Exa MCP** *(optional, requires API key)* | User | See [exa-labs/exa-mcp-server](https://github.com/exa-labs/exa-mcp-server) | Semantic web search for harder research questions |

---

## CLIs (npm-based)

| Tool | Install | Purpose |
|---|---|---|
| **designlang** | `npx designlang <url> --system-chrome -o /tmp/designlang-out` | Same as the MCP, callable as a one-shot. Use when you don't want to keep an MCP connection open |
| **Motion** (the library) | `npm i motion` (per-project) | Animation library — spring physics, transform+opacity. Import from `motion/mini` for ~3KB vanilla bundle |
| **AutoAnimate** | `npm i @formkit/auto-animate` | One-call FLIP animations for list reorders. Complement to Motion, not replacement |
| **gh** (GitHub CLI) | `brew install gh` | Preferred over the GitHub MCP for PR work — lower context cost |
| **claude** (Claude Code) | `npm install -g @anthropic-ai/claude-code` | The CLI surface for everything in this kit |

---

## APIs the playbook touches

| API | Used when | Notes |
|---|---|---|
| **Anthropic Messages API** (`@anthropic-ai/sdk`) | LLM features in your product (chat, agents, conversation) | Always enable prompt caching. The `claude-api` skill handles model migrations |
| **Supabase** (optional) | If you build an empirical-input design-ranker | Pairwise-comparison storage, Bradley-Terry MLE compute, tournament relegation for the empirical-input track |

---

## Recommended-against (do not install)

These were evaluated and explicitly rejected. They push toward generic AI-startup aesthetic, which contradicts the entire point of this kit.

| Tool | Reason |
|---|---|
| **v0 MCP** | Abandoned (no commits since mid-2025); regresses to shadcn aesthetic |
| **shadcn skill** | Excellent if you adopt shadcn as system-of-record; fights bespoke CSS otherwise. Hold until you've made a system-level decision |
| **Magic UI MCP** | Pushes toward the same shadcn-default aesthetic |
| **taste-skill** | Hard React + Tailwind + Framer Motion assumption; default fonts (Geist / Cabinet Grotesk / Satoshi) pull *away* from editorial directions; allows shadcn |
| **UI/UX Pro Max** | Curated palettes are anti-bespoke (recommends category-typical answers). Lift the a11y/touch/perf rules into your own discipline skill instead |

---

## How this inventory stays current

Once a quarter, re-run the audit:

1. Check each vendored skill's source repo for major version bumps.
2. Re-test the MCPs (some break silently when their upstream changes).
3. Add anything new that's earned its place (with a verdict: ADOPT / TRIAL / ASSESS / HOLD).
4. Remove anything that's been HOLD for two cycles without earning a re-evaluation.

If you're consuming this kit in a project, your `tool-inventory.md` may diverge — that's fine. This file is the upstream reference.
