---
name: claude-as-llm
description: Run batch LLM tasks through Claude Code (me) instead of calling the Anthropic API. Use when the task is LLM-intensive, items can be processed in independent batches, the output schema is well-defined, and the user wants to leverage their Max plan instead of paying per-token API costs. Pattern — I generate model outputs directly in my response, then pipe to a task-specific consume script that persists transactionally. Reusable across enrichment, classification, summarization, structured extraction, translation, code-review-comment generation, and similar.
---

# claude-as-llm — run batch LLM tasks via Claude Code, not the API

## Why this exists

The Anthropic API is billed per token. A Claude Max plan covers Claude Code session tokens at a fixed monthly cost. When a batch task is a good fit (clear schema, self-contained per-item context, terminating queue), the cheapest path is:

1. **I (Claude Code) generate the LLM output directly in my response.** No `anthropic.messages.create` call, no API line item.
2. A consume script reads my output (from a temp file or stdin) and persists it transactionally.

This skill is the **harness pattern** — domain-specific tasks (catalog enrichment, classification, document summarization, etc.) live in their own per-task skills that build on this pattern.

## When this pattern applies

**Use it when:**
- Each item is independent — no item's output influences another's input within a batch.
- Output shape is well-defined (JSON schema known up-front, validated by a consume script).
- Batch size fits in one response: typically 5–50 items, depending on per-item output size.
- Total queue is big enough that API cost would be noticed (hundreds → hundreds of thousands).
- Quality bar warrants Sonnet/Opus-class output (which Max provides at no marginal cost).

**Don't use it for:**
- Real-time / user-facing requests (this is async, batched).
- Items needing live tool use the user wants to retain (browser interaction, paid third-party APIs, etc.).
- One-off tiny tasks where setup overhead exceeds the API cost saved.
- Tasks with item-to-item dependencies inside a batch (loop sequentially via API instead).

## The four pieces every claude-as-llm task needs

| Piece                        | What it is                                                                 | Lives in                          |
| ---------------------------- | -------------------------------------------------------------------------- | --------------------------------- |
| **dump script**              | Claims the next N items from the queue and emits them as JSON              | `scripts/<task>-dump.ts`          |
| **consume script**           | Reads a JSON array of model outputs and persists them transactionally      | `scripts/<task>-consume.ts`       |
| **task skill**               | Per-task LLM rules: what to generate, how to ground it, common pitfalls    | `.claude/skills/<task>-next/SKILL.md` |
| **schedule** (optional)      | One or more cron routines that fire the task skill on a cadence            | `schedule` skill / cron routines  |

Dump and consume are mechanical (data shuffling). The **task skill** is where the per-domain judgment lives. This skill is the harness — it explains how all four fit together so you can build the pieces for a new task or recognize them in an existing one.

## The runtime pattern (per batch)

Once a task has its dump + consume scripts and a task skill, processing one batch looks like:

1. **Read the task skill** (e.g. `.claude/skills/<task>-next/SKILL.md`) and any per-task playbook so the rules are fresh.

2. **Run the dump script** to claim a batch of N items:
   ```bash
   pnpm tsx scripts/<task>-dump.ts <N> --compact
   ```
   It outputs JSON: each entry has every input the LLM needs (fields, calibration data, existing-state context), plus the item id. **Always pass `--compact`** — single-line JSON cuts input tokens ~50% vs pretty-print.

3. **Generate output for each item in my response.** This is the only step that uses Max tokens instead of API tokens. For each input item, build the structured output the consume script expects, following the schema and per-task rules exactly.

4. **Write outputs** to `/tmp/<task>-batch-NN.json` (`NN` = agent slot or timestamp suffix to avoid collisions across parallel runs).

5. **Run the consume script** to persist:
   ```bash
   pnpm tsx scripts/<task>-consume.ts --file /tmp/<task>-batch-NN.json
   ```
   Validates schema, applies updates atomically, logs provenance, returns success/failure counts.

6. **(Optional) Append an observation** to a per-task log so future agents learn from this batch.

## Setting up a new claude-as-llm task

When the user asks "make a claude-as-llm task for X":

1. **Pin down the schema.** Per-item input the LLM needs? Per-item output? Target table(s) / files? Write the schema as a TypeScript type before any code.

2. **Write the consume script first.** Build validation against the schema and a transactional persist path. This is the contract the LLM has to satisfy. Knowing the consume side first prevents schema drift.

3. **Write the dump script.** It should:
   - **Claim atomically** — flip status `seeded → claiming`, use `FOR UPDATE SKIP LOCKED` so parallel routines don't collide.
   - **Bundle context** — every field the LLM needs (input data, calibration references, neighbors, existing state).
   - **Reset stale claims** at the start of each call (default 15 min) so a crashed agent doesn't strand items forever. Make the threshold configurable via env var (e.g. `DUMP_STALE_INTERVAL`) for ad-hoc workflows where claims sit longer.

4. **Write the task skill** at `.claude/skills/<task>-next/SKILL.md`. It should include:
   - The frontmatter `description` (it's how the model decides when to load — be specific).
   - The output schema, with field-level rules and pitfalls.
   - Any quality gates (flag-and-skip vs persist-flagged-for-review).
   - Per-item examples of good and bad output if non-obvious.
   - Reference this skill for the harness boilerplate; don't restate it.

5. **(Optional) Schedule it.** Use the `schedule` skill to create N hourly routines (typically 5–10), each invoking the task skill via prompt `Run the next batch per @.claude/skills/<task>-next/SKILL.md`. Stagger by minutes so they don't race for the same items. Throughput = `slot_count × batch_size / hour`.

## Example tasks this pattern fits

- Catalog enrichment.
- Bulk summarization of long documents into a fixed-schema digest.
- Classification across a labeled vocabulary (sentiment, topic, severity, price tier).
- Structured extraction from unstructured text (entities, dates, prices).
- Cross-language translation when the output schema is fixed.
- Image-caption generation (paired with an image-loading dump that base64s thumbnails into the dump JSON).
- Code-review-comment generation for a queue of diff hunks.
- PR triage / labeling against a fixed label set.

## Token-efficiency checklist

Max sessions are not unlimited — token efficiency directly translates to "how many items per day this skill can clear." Apply these to every task built on the claude-as-llm pattern. They compound multiplicatively. (For broader delegation strategy, see the `token-efficient-delegation` skill.)

### Dump-side (input tokens)

- **`--compact` JSON output by default for skill consumption.** Pretty-printed JSON nearly doubles input tokens vs single-line. Pretty-print stays available behind a flag for debugging.
- **Don't ship duplicate context per item.** When the per-item input shares a field across the batch (e.g. shared calibration data, fixed taxonomy, batch-level metadata), put it ONCE at the chunk header rather than repeating per item.
- **Drop fields the model never reads.** Audit the dump output periodically. If a field never gets cited, remove it.
- **Specific file paths in instructions.** `src/foo.ts:42-51` costs ~50 input tokens; "update the foo function" forces a grep that costs 10×.

### Sub-agent prompt structure (when fan-out is involved)

- **Bit-identical static prefix across parallel sub-agents.** Anthropic prompt cache (5-min TTL, ~90% input discount) keys on byte-exact prefix. Put long boilerplate (rules, schema, vocabulary) at the TOP, identical across all N sub-agents in a fan-out. Variable bits (chunk path, run id) go at the BOTTOM, after a clear `== END STATIC PREFIX ==` marker.
- **Spawn N sub-agents in ONE message.** Sequential dispatch loses both parallelism AND the cache hit (the second request lands after the first's prefix has been written). One message, multiple `Agent` tool calls.
- **Keep total dispatch wall time under 5 minutes.** Build all chunk files first, then send the parallel-spawn message. If chunk preparation takes 5+ minutes, the cache is gone before the last sub-agent starts.
- **Don't toggle thinking, fast mode, or web search mid-task.** Cache hierarchy is `tools → system → messages` — a change at any level invalidates that level and below. Toggle BEFORE the message.

### Sub-agent output (output tokens — no caching, this is the dominant cost)

- **Sparse output by default.** If the schema has many optional/zero fields (vocabulary slugs, enum scores, rarely-set flags), the consumer should default missing keys to the zero value and the prompt should require emitting only non-zero fields. For a 48-key vocabulary where most items hit ~5 keys, that's ~80% fewer output tokens per item.
- **Single-line JSON in output.** No indentation, no whitespace between objects.
- **No preamble, no commentary.** Require the first character of the output file to be the opening JSON delimiter. "Here is the analysis:" sentences are pure waste.
- **One-line completion ack in chat.** Have sub-agents reply with a single short line like `OK chunk-NN: <ok>/<total>` so the orchestrator can confirm success without parsing prose. Long sub-agent chat replies tax the orchestrator's context, not just the sub-agent.

### Context lifecycle

- **One topic per chat.** `/clear` between unrelated tasks. The orchestrator's conversation is re-read on every turn — by message 50 you're paying to re-read 49 prior messages before any new work.
- **`/compact` at logical breakpoints**, never mid-implementation.
- **Use `session-handoff` skill** when a topic genuinely needs to span sessions.
- **`/loop` sleep windows:** <270s for hot work (cache stays warm) or ≥1200s for genuinely idle waits. Never split the difference at 300s — that's the worst-of-both.

### Tool routing

- **CLI over MCP** when both exist. MCP tool definitions stay in context forever; `gh pr view 34` is a one-shot.
- **`Explore` sub-agent for file searches.** Returns a summary, not raw file contents — orchestrator context stays clean.
- **`general-purpose` sub-agent with `model: sonnet` or `model: haiku`** for batch generation when the work fits a smaller model.

### Don'ts that look tempting but lose

- **Multi-turn within a sub-agent** ("first generate the editorial, then the profile" in two turns). Doubles input tokens with no quality benefit; one turn handles both fine.
- **Skill-file hoisting** (move boilerplate into a sub-skill the agent loads). Net wash on tokens — the skill content lands in context anyway. Inline the boilerplate so prompt-cache works.
- **Switching to a smaller model** to "save tokens." If quality drops, you re-run, which is a 2× spend. Stay on the model the task is calibrated for.
- **Anthropic Batch API.** Charges API tokens. Out of scope for the claude-as-llm pattern, which is explicitly the Max-only path.

### Quick measurement loop

When you build or modify a claude-as-llm task, run a tiny experiment to sanity-check token economics before scaling:

1. Capture dump size: `pnpm tsx scripts/<task>-dump.ts 5 --compact | wc -c`. Divide by 4 for a rough input-token estimate per batch.
2. Run one batch end-to-end. Note wall time and persisted count.
3. Compare against the previous task shape. If a change you made should have cut tokens, verify it actually did.

Maintaining a measurement journal (e.g. `docs/<task>-runs.md` with one row per run: shape, wall time, persisted, tokens-per-item) pays for itself within ~5 runs when you start tuning fan-out shapes.

## Common mistakes to avoid

- **Defining a new task without a consume script.** If outputs can't be validated and persisted mechanically, the LLM contract is undefined and drift is inevitable. Build consume first.

- **Items with intra-batch dependencies.** If item N's output should influence item M's, batch them separately or chain them via the API path. The claude-as-llm pattern assumes per-item independence.

- **Schema drift between dump and consume.** Share a TypeScript type between the two scripts (`scripts/<task>/types.ts`) or, at minimum, version the schema in the dump output and have consume reject mismatches.

- **No watchdog.** Crashes happen. Stale `claiming` rows accumulate. Either the dump's reset-stale-claims handles it, or a separate sweeper resets them periodically.

- **Running the API path simultaneously with the Max path.** If `scripts/<task>.ts` (the API version) and the claude-as-llm loop both run, they race. `pgrep -fl <task>.ts` before launching, and document this in the task skill.

- **Treating the skill as the schema.** The schema source of truth is the consume script's validation. The skill describes intent and rules; consume enforces them.

- **Skipping observations.** If a per-task log exists, future agents lose context without it. Even a one-line note compounds over weeks.

## Cost intuition

For a typical Sonnet-grade task with ~1k input tokens and ~500 output tokens per item:

- Via API: ~$0.003 + $0.0075 = ~$0.01 per item × 22,000 items = **~$220** for one full pass.
- Via claude-as-llm: **$0** marginal (covered by Max plan), at the cost of ~3–5 minutes of session time per 10-item batch and the user's session-quota allowance.

The cost-tipping point depends on Max plan headroom and the wall clock you can tolerate. For a 22k-item one-shot, the savings are large enough to justify significant scheduling complexity.
