---
name: subagent-fanout
description: Methodology for high-throughput parallel sub-agent dispatch from inside Claude Code — the bit-identical static prefix discipline that wins the prompt-cache discount, single-message parallel spawn, RUN_ID file conventions, sparse single-line JSON output, and one-line completion ack. Use when designing or running a fan-out where N sub-agents do independent slices of the same task and you want both wall-clock parallelism AND the cache discount across sub-agents 2..N. Pairs with claude-as-llm for the dump→generate→consume harness.
---

# subagent-fanout — parallel sub-agent dispatch with prompt-cache hits

## When this skill applies

You have a queue of items, each item processable independently against the same rule set, and the queue is large enough that one sub-agent can't clear it in a single response. Typical signals:

- A claude-as-llm task whose batch ceiling is ~10 items per response and you want 100+ per fire.
- An orchestration where multiple Explore-style agents could research different files in parallel.
- A bulk classification/transformation where every item gets the same prompt skeleton, only the input data varies.

**Don't use it for:**
- Tasks with item-to-item dependencies (sub-agent N's output influences M's input).
- Tasks requiring live tool use the orchestrator wants to keep visibility on (browser sessions, paid third-party calls).
- Workloads where one sub-agent fits comfortably (< ~20 items).

## Why the cache hit matters

Anthropic prompt caching keys on **byte-exact prefix match**. The cache has a 5-min TTL and ~90% input-token discount on the cached portion. With N sub-agents in a fan-out:

- Sub-agent 1 writes the prefix to cache. No discount on this request.
- Sub-agents 2..N read from cache. ~90% discount on the cached portion of each.

For a typical 2,000-token static prefix and a 5-way fan-out, that's roughly `4 × 0.9 × 2000 = 7,200 tokens` saved per fire. Across a production loop firing every hour, this is the difference between "comfortable Max headroom" and "rate-limited by 3pm."

The discipline below is what keeps the cache hot.

## The five rules

### Rule 1 — Bit-identical static prefix

Structure every sub-agent prompt as:

```
<long boilerplate: rules, schema, vocabulary, output format, examples>

== END STATIC PREFIX ==

<short variable footer: input path, output path, run id, slot number>
```

Everything ABOVE the marker must be **byte-identical** across all N sub-agents in one fan-out. Same characters, same casing, same whitespace, same line breaks. A single character drift (a different run id leaked in, "Chunk-01" vs "chunk-01" casing, an extra trailing space) defeats the cache key.

The variable footer can vary freely — it lands after the cached prefix and isn't expected to hit cache.

### Rule 2 — Spawn N sub-agents in ONE message

Send a single message containing N `Agent` tool calls. Sequential dispatch loses BOTH the wall-clock parallelism and the cache hit (the second request lands after the first's prefix has expired or before it has been written).

```
# Right: one message, N tool calls
Agent({ ..., prompt: prefix + footer_1 })
Agent({ ..., prompt: prefix + footer_2 })
Agent({ ..., prompt: prefix + footer_3 })

# Wrong: N messages, one tool call each
```

### Rule 3 — Stay under 5 minutes wall-time from prefix-write to last-spawn

The 5-min TTL is the constraint. If chunk preparation itself takes 5+ minutes, the cache is gone before the last sub-agent reads it. Pattern:

1. Build all chunk input files first (cheap — file writes).
2. THEN send the parallel-spawn message (one shot).

If your fan-out shape requires > 5 min of orchestrator work to set up, you have too few sub-agents doing too much each — split smaller.

### Rule 4 — `RUN_ID` discipline for `/tmp` files

```bash
RUN_ID="$(date +%Y%m%dT%H%M%S)-<runLabel>"   # e.g. 20260506T143000-prod
```

Use it as the prefix for every file in this run:

```
/tmp/<task>-${RUN_ID}-pool.json
/tmp/<task>-${RUN_ID}-chunk-01-input.json
/tmp/<task>-${RUN_ID}-chunk-01-output.json
…
```

Why: parallel orchestrations (e.g. two scheduled `/loop` jobs racing) must never clobber each other's intermediate files. Always regenerate `RUN_ID`; never reuse.

### Rule 5 — Sub-agent output discipline

Every byte the sub-agent emits is uncached output. Token cost is the dominant cost. Therefore:

- **Sparse output.** If the schema has many optional/zero fields, the consumer should default missing keys to the zero value and the prompt should require emitting only non-zero fields. (For a 48-key vocabulary where most items hit ~5 keys, that's ~80% fewer output tokens per item.)
- **Single-line JSON.** No indentation, no inter-object whitespace.
- **No preamble.** First character of the output file MUST be the opening JSON delimiter (`[` or `{`). No "Here is the analysis", no markdown fences, no commentary.
- **One-line completion ack in chat.** Sub-agent replies with exactly one short line like `OK chunk-NN: <ok>/<total>`. Long sub-agent chat replies tax the orchestrator's context, not just the sub-agent's.

## The orchestration shape

```
generate RUN_ID
↓
claim pool atomically (FOR UPDATE SKIP LOCKED) → /tmp/<task>-${RUN_ID}-pool.json
↓
slice pool into N chunks → /tmp/<task>-${RUN_ID}-chunk-NN-input.json
↓
send ONE message with N parallel Agent calls    ← THE LOAD-BEARING STEP
   each prompt = bit-identical-static-prefix + per-chunk-footer
   each sub-agent writes to /tmp/<task>-${RUN_ID}-chunk-NN-output.json
   each sub-agent acks "OK chunk-NN: ok/total"
↓
consume each output sequentially (or batched)
↓
append a measurement row to the run journal
```

The atomic-claim, slice, dispatch, consume sub-steps are details of the harness pattern (see `claude-as-llm`). The dispatch step is what this skill is about.

## Choosing fan-out shape

There's no universally optimal shape — measure for your task. Three axes to think about:

| Axis | Push higher when… | Push lower when… |
|---|---|---|
| **Sub-agent count (N)** | Wall-clock matters more than budget | Single-task is fast and you want fewer files to manage |
| **Items per sub-agent (M)** | Per-item cost dominates output tokens (cache amortizes well) | Quality drops at the tail of long batches; latency matters |
| **Total batch (N×M)** | Queue is huge; staying inside 5-min TTL still works | Queue is small; setup overhead dominates |

A sensible default for novel tasks: start at `5×30`. Once you have measurements (see below), tune up the per-batch (`5×50`) for budget efficiency, or tune up the agent count (`8×30`) for wall-clock.

**Latency tail matters.** With M items per sub-agent, the slowest sub-agent in the fan-out usually takes ~1.5–2× the median. The orchestrator can't move on to consume until the last one returns. Larger M widens the tail.

## Measurement journal

Maintain an append-only file with one row per run. Columns to capture per run:

```
run_id  shape   total_claimed  persisted  flagged  aborted  wall_seconds  observations
```

After ~5 runs you'll see which shape gives the best persisted-per-token ratio and which gives the best wall-clock. Document the chosen production default in the per-task skill with a one-line citation back to the run that proved it.

## Common mistakes

- **Spawning sub-agents sequentially.** Always one message, multiple tool calls.
- **Drifting the static prefix.** Even a single character difference between sub-agents' boilerplate prevents cache hits. Audit by `diff`-ing the actual prompts you send.
- **Interpolating the run id into the static block.** It belongs in the variable footer.
- **Forgetting the `--compact` flag** on the upstream dump that produces the chunk inputs. Pretty-printed JSON nearly doubles input token cost.
- **Reusing a `RUN_ID`.** Always regenerate. Collisions clobber intermediate files.
- **Picking a shape larger than the queue.** If only 200 items remain, don't run a 250-item shape — claim what's available and adjust.
- **Letting sub-agents do extra tool work the prompt didn't authorize.** Web research, file reads, etc. each blow the input token budget the cache was supposed to amortize. Forbid explicitly in the prefix.
- **Spreading sub-agent dispatch across >5 min.** TTL gone, cache miss, paying full price on agents 2..N. If chunk prep is slow, parallelize that or split into smaller pre-batches.

## Project-side companion

A project that uses this methodology should have a thin domain skill that:
- Documents the production fan-out shape (e.g. `5×50`) with a citation to the run that validated it.
- Inlines the per-task rules block in the static prefix (do NOT factor out to a referenced doc — the indirection breaks cache alignment unless every sub-agent reads the same way).
- Lists the dump/consume scripts and the temp file path conventions for the task.
- References this skill for the dispatch discipline rather than restating it.
