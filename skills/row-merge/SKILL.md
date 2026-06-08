---
name: row-merge
description: Methodology for safely merging duplicate rows in a relational database — the six safety rails (scalar coalesce, never-overwrite-images, preserve-embeddings, union-deduped relations, retargeted provenance, reversible merged-from event), the winner-picker template, the display-name picker, and the severity rubric for pre-merge audits. Use when designing or running a dedupe pipeline against any table where duplicate detection has produced candidate clusters and you need to collapse them without losing data. Pairs with project-level skills that wrap these rules around specific scripts and tables.
---

# row-merge — safely consolidate duplicate rows without losing anything

## When this skill applies

Any time you have two (or more) rows in one table that refer to the same real-world entity and you want to collapse them into one. Examples:

- Two product rows ingested from different sources
- Two organization/brand rows with punctuation drift ("Viktor & Rolf" vs "Viktor Rolf")
- Two person rows with a typo ("Jacques Polge" vs "Jacque Polge")
- Tag/category rows with different slug casings pointing at the same concept

**Do not use** to delete a row you don't want. Use a `status='removed'` field for that — merges assume both rows are legitimate and you're consolidating them.

## The six safety rails — non-negotiable

Every merge produced by a script using this methodology MUST obey all six. Violating any one of them silently destroys data.

1. **Scalar preservation via coalesce.** If the winner has a `null` for a column and the loser has a non-null, the winner inherits it. The winner never loses data it already had; the loser's unique scalar values are rescued.

2. **Images / large generated assets are sacred.** Image URLs, thumbnails, blurhashes, generated derivatives — these follow coalesce, AND we never overwrite a non-null asset on the winner. If the winner already has an image, the loser's image is captured in the merged-from event for forensic recovery but otherwise discarded.

3. **Embeddings / expensive computed fields are never recomputed.** Vector embeddings, derived hashes, materialized tags — keep whichever side has them. Recomputing is either expensive or non-deterministic.

4. **Relations are union-deduped.** Many-to-many join tables, child rows owned by the parent (notes/tags/skus/list-items, etc.). Move the loser's relations to point at the winner; drop intra-batch duplicates via `ON CONFLICT DO NOTHING`. Never lose a relation row that existed only on the loser.

5. **Provenance is retargeted.** Every audit-trail row whose `entity_id = loser.id` is updated to `entity_id = winner.id` so the merge doesn't break the history.

6. **A `merged_from` event is logged with a full snapshot.** Append-only event row containing the loser's complete pre-delete state as JSON. This is what makes every merge **reversible** — a future operator has the loser's slug, all scalars, image URL, ratings, everything needed to reconstitute.

The loser row is then deleted. FK cascades handle children that aren't relations to retarget.

## The winner-picker

The winner is the row whose DATA we keep. Recommended priority order (adapt to your domain):

1. **Status / completeness** — `enriched > seeded > flagged`, or whatever your "this row has been worked on" signal is.
2. **Has expensive generated content** — LLM-written descriptions, computed embeddings, manually-curated metadata.
3. **Popularity / engagement signal** — review count, traffic, citations, whatever proxies for "users care about this row."
4. **Has core scalars filled** — release year, price, country, etc.
5. **Recency** — `updated_at DESC` as a secondary tiebreak.
6. **Lexicographic id/slug** — final stable tiebreak so the same cluster always picks the same winner across re-runs.

The visible NAME on the winning row is picked separately — see next section.

## The display-name picker

Often the row with the best DATA isn't the row with the best NAME. Decouple the two: pick which row's `name` to inherit independently of which row's data wins. The "richest" name pattern:

- **Most non-ASCII characters** (diacritics, ligatures like œ/ß, curly quotes): high score per character. So "Éclat d'Arpège" beats "Eclat d'Arpege".
- **Curly quotes specifically** (U+2018, U+2019, U+201C, U+201D): bonus.
- **Length**: tiny tiebreak only.
- **Per-domain overrides**: e.g. prefer the variant that does NOT end with the brand name when collapsing brand-suffixed product names ("Light Blue" vs "Light Blue Dolce & Gabbana" → keep "Light Blue").

This means the data winner can be the ASCII-only row (because it has more reviews) but its `name` gets overwritten with the loser's richer form before delete.

## The severity rubric (for pre-merge audits)

When proposing a merge — especially manual or one-off — render an inconsistency report sorted by severity. The operator scans HIGH first.

| Severity | Meaning | Examples |
|---|---|---|
| **HIGH** | Probably different entities. Stop and review. | Year-of-release differs by ≥3; image URL differs and both present; price-tier differs; engagement metric ratio > 10× |
| **MED** | Real disagreement but plausibly same entity. | Year differs by 1–2; specific vs specific category (`edp` vs `edt`, `large` vs `medium`); rating differs by > 0.5 on a 5-pt scale |
| **LOW** | Safe to rescue from loser. | Default placeholder vs specific value (e.g. `"other"` vs `"edp"`); minor drift |
| **INFO** | Straight rescue from loser (winner was null). | Description, embedding, image-url on winner = null |

Bulk-cleanup passes that already pre-cluster aggressively (e.g. on alphanumeric-stripped names) can skip per-pair severity checks — the pass definition itself is the safety claim. Manual `merge-one`-style operations should always render the severity report.

## Operational pattern

```
audit / cluster      → propose merge plan (read-only)
↓
inconsistency report → operator reviews HIGH/MED rows
↓
dry-run merge        → SQL committed inside a transaction that rolls back
↓
apply merge          → same transaction, commits this time
↓
verify               → winner resolves; loser 404s; relation count = expected; merged_from event present
```

Key transaction guarantees:
- Wrap everything in one transaction so a partial merge never leaves orphans.
- Delete child relations BEFORE deleting the parent row, or FK CASCADE will run first and wipe the join rows you were trying to move.
- Bulk-upsert relation moves with `ON CONFLICT DO NOTHING` on the natural unique key.

## When NOT to merge

- **Variants of the same product** (size/concentration/edition/year) — keep separate rows, link via a "variants" relation later.
- **Annual editions** (CK One Summer 2004, 2005, ...) — distinct.
- **Cross-parent same name** (Rose by X vs Rose by Y) — coincidence. Only merge if you have evidence the parents are themselves the same entity.
- **Same fingerprint, different SKU** — two products can share a notes pyramid / a feature set / a spec sheet and still be legitimately different SKUs. Don't merge on fingerprint alone.

## Common pitfalls (learned the hard way)

- **Raw SQL clients return snake_case; ORM clients return camelCase.** Mixing within one merge function silently accesses `undefined` for half the fields. Pick one and stick to it.
- **`ON CONFLICT DO UPDATE` needs unique slugs within the upsert batch.** If two losers slugify the same, dedupe by slug before the bulk-upsert.
- **Cyrillic / Arabic / Thai scripts don't unaccent.** Keep the original name as the display when the cluster is non-Latin.
- **`pg_trgm` similarity doesn't understand unicode equivalence.** "Éclat" and "Eclat" trigram-match at ~0.7, but unaccent first and they're identical (similarity → 1.0). Always normalize before similarity scoring.
- **Coalesce direction matters.** `winner.field ?? loser.field` gives the winner priority; `loser.field ?? winner.field` rescues the loser. Pick deliberately per field.
- **Default placeholders defeat coalesce.** If your ingest writes `"other"` as a default, then coalesce sees a non-null winner value and never rescues the loser's `"specific"` value. Treat sentinels as null at merge time.

## Un-merging (if it was wrong)

The `merged_from` event snapshot lets a future operator reconstruct the loser:

1. INSERT a new row from `metadata.loser_snapshot` (assign a fresh id).
2. Move per-pass relations back. **This is lossy** — the union was recorded, but which relation came from which side wasn't. Assume shared unless you have evidence.
3. Append an `unmerged` event (new row, never edit the original `merged_from`).

Un-merging from a single snapshot is imperfect. Better safety comes from dry-running thoroughly BEFORE applying.

## Project-side companion

A project that uses this methodology should have a thin domain skill that:
- Lists the specific scripts that implement the merge (`cleanup-X.ts`, `merge-one.ts`).
- Names the per-entity FK relation tables that need union-deduping (e.g. `perfume_notes`, `retailer_skus`).
- Records any per-domain coalesce rules (which sentinel values to treat as null).
- Documents the per-pass cluster definitions used by bulk cleanup.
