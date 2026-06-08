---
name: scrape-and-rehost
description: Methodology for bulk-filling a database column from a third-party site — query for rows missing the field, fetch each source page or CDN URL with rate limiting, extract the asset, re-host to your own storage, write back idempotently. Covers rate envelope (1 req/s + jitter, exponential backoff), idempotency via WHERE NULL, header tactics for accessing different TLDs, Cloudflare detection, nohup/restart safety, and progress monitoring. Use when a large batch of rows needs an external asset (image, logo, document, structured fact) whose URL isn't directly derivable from data you already have.
---

# scrape-and-rehost — bulk fill a DB column from third-party sources

## When this skill applies

| Signal | Use this skill |
|---|---|
| `SELECT COUNT(*) FROM <table> WHERE <field> IS NULL` returns thousands of rows | ✓ |
| The asset lives on a third-party site/CDN | ✓ |
| The site is accessible without Cloudflare / DataDome / aggressive WAF | ✓ |
| Source URL must be discovered per row (HTML scrape) OR derived from a slug/id mapping | ✓ |
| Source is bot-friendly at ~1 req/s | ✓ |

Skip this pattern when:
- You only need < ~500 assets and already have the direct source URLs (just write the loop directly).
- Source is behind a hostile WAF (try other TLDs first; otherwise the source isn't viable for bulk).
- Asset is not legally redistributable (this pattern re-hosts; verify the use case).

## Architecture

```
DB rows WHERE <field> IS NULL
  │
  ▼
derive script (one per source)
  ├── load slug/id → source URL map (CSV, slug derivation, or DB column)
  ├── query DB for candidates (ORDER BY popularity DESC, ID, etc.)
  └── for each candidate (concurrency=1, 2–3s jitter):
        fetch source page HTML  OR  fetch CDN URL directly
        extract asset src       (CSS class pattern, og:image meta, JSON path)
        fetchAndStore(src) → re-host to your storage
        UPDATE table SET <field>, derived_metadata
        log provenance event
```

**The load-bearing detail:** `WHERE <field> IS NULL` in the candidate query is what makes the whole run **idempotent**. If the process dies and restarts (laptop sleep, network blip, deploy), it processes only rows still missing the field. No state file required.

## Rate envelope — do not negotiate down

These values are tuned for typical bot-tolerant sites. Going faster invites 429 blocks that destroy throughput for hours.

```
CONCURRENCY     = 1          # 3 max for HTML page fetches; 5 max for direct-CDN downloads
JITTER          = 2000-3000ms between requests (random)
MAX_RETRIES     = 4 per candidate
BACKOFF         = 30s → 60s → 120s → 120s → skip
USER_AGENT      = a realistic Chrome string, not "node-fetch"
```

If the source starts pushing back (429s, 403s), the script should **slow itself down via backoff**, not paper over the symptom by reducing concurrency further. Persistent 429 means stop the run and reassess.

## Header tactics

Different TLDs of the same source often have different bot protection. Try `.de`, `.fr`, `.co.uk` if the `.com` is behind Cloudflare.

```
Accept-Language: <site native>      # e.g. de-DE for parfumo.de
Accept: image/avif,image/webp,image/apng,image/*,*/*;q=0.8
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
```

Confirm bot-friendliness with a quick `curl -I` BEFORE writing the script:

```bash
curl -I -A "<UA>" "https://target.example.com/sample-page"
# Look for: no `cf-ray` header, no 403, no 503
```

## Source identification (do this first)

Before writing a derive script, answer these by hand on 5–10 sample URLs:

1. **What HTML element holds the asset?** A specific CSS class? An `<meta property="og:image">`? A JSON-LD blob? Make sure the pattern is consistent across pages, not specific to the example you picked.

2. **How do you map a DB row to a source URL?** Three common cases:
   - Direct: a `source_url` column already exists.
   - Derivable: source URL is `site.com/{slug}` from your existing slug.
   - Indirect: requires a CSV / external map / slug-cleanup pass.

3. **Does the source require special headers?** Test `Accept-Language`, custom `User-Agent`, `Referer`.

## Storage and write conventions

- **Always re-host.** Never store third-party CDN URLs directly — they rot, change, or go behind WAFs.
- **Storage key namespace.** Pick a prefix per asset class so different sources can co-exist: `web/par-<slug>`, `logos/par-<id>`, `pdfs/manual-<id>`. The prefix encodes both the asset type and the source.
- **Format conversion.** Convert to a modern format (WebP for images, …) at fetch time; store dimensions and a content hash for change detection.
- **Provenance.** Log one event per fill: `entity_id`, `field_name`, `source_url`, `source` enum value, `fetched_at`. Audit trail for "why does this row have this asset?"

## Long-running execution

```bash
# 1. Dry run first — confirms slug matching and URL derivation, no writes.
pnpm tsx scripts/derive-<source>.ts --dry-run | head -20

# 2. Count candidates before starting.
pnpm tsx scripts/derive-<source>.ts --dry-run 2>&1 | grep "selected"

# 3. Real run, backgrounded with nohup so laptop sleep won't kill it.
nohup pnpm tsx scripts/derive-<source>.ts \
  >> /tmp/<source>-run.log 2>&1 &
echo "PID: $!"
```

For runs > ~500 items, **always** use `nohup` so the process survives shell exit. On most macOS configurations, nohup also keeps it alive through laptop sleep — but if the laptop dies and the process dies, just restart with the same command. The `WHERE <field> IS NULL` query skips already-filled rows automatically.

## Progress monitoring

Emit a one-line progress ticker every 100 items:

```
·  10169/24906  db=9843  404=0  noImg=824  imgFail=2  429=0  skip=0   0.26 req/s
```

| Field | Meaning |
|---|---|
| `N/total` | Candidates attempted / total selected at start |
| `db=N` | Rows successfully written |
| `404=N` | Source pages returned 404 (expected for deleted entries) |
| `noImg=N` | Pages loaded but no matching asset element (selector failure or page format change) |
| `imgFail=N` | Asset fetch / processing error (network, format) |
| `429=N` | Rate-limit events (should stay 0 at concurrency=1) |
| `skip=N` | Candidates skipped after exhausting retries |

```bash
tail -f /tmp/<source>-run.log         # live tail
ps aux | grep derive-<source> | grep -v grep   # confirm alive
```

If `noImg` rises sharply mid-run, the page format probably changed — pause and re-validate the selector pattern.

## Restart safety

The same run command is idempotent:

```bash
nohup pnpm tsx scripts/derive-<source>.ts >> /tmp/<source>-run.log 2>&1 &
```

No `--start=N` flag needed. The `WHERE <field> IS NULL` ensures previously-filled rows are skipped. The only state NOT preserved is the `processed` counter (resets to 0); the `db=` cumulative comes from the DB query itself, so it shows real progress across restarts.

## Concurrent-run hygiene

If you might run the same script from two shells (e.g. by accident), the atomic-claim pattern matters:

- Each candidate-row select should `FOR UPDATE SKIP LOCKED` if you want true safety.
- Or accept that the second run will mostly find rows the first already filled (idempotent — wasteful but safe).

Most bulk-fill scripts pick the second path because the WHERE-NULL filter on the next candidate select naturally avoids most collisions.

## Checklist before starting a new source

- [ ] `curl -I` confirms no Cloudflare/WAF block.
- [ ] CSS selector / extraction pattern verified on 5–10 sample pages, including edge cases.
- [ ] URL pattern tested for at least one row from each "shape" of slug (with diacritics, with apostrophes, with non-Latin scripts).
- [ ] `fetchAndStore` (or your project's storage helper) handles the format conversion; no need to re-implement.
- [ ] Storage key prefix chosen, doesn't collide with existing objects.
- [ ] Dry-run shows reasonable candidate count and example URLs.
- [ ] `nohup` + log path confirmed before the full run.

## Common mistakes

- **Going to concurrency=5 on HTML pages.** Trips 429s. Reserve concurrency 5 for direct-CDN image downloads only.
- **Hardcoding the User-Agent as `node-fetch`.** Most sites block it on sight.
- **No `WHERE <field> IS NULL` filter.** Restart re-fetches everything; you lose the idempotency guarantee.
- **Writing the source URL directly.** Re-host always; third-party URLs rot.
- **Skipping the dry-run.** A bad selector against 24K rows is 24K log lines of `noImg`.
- **Treating `og:image` as the default selector.** Often a hero/banner image, not the canonical product asset. Prefer a specific CSS class.
- **No backoff on 429.** Hammering during a rate-limit window extends the block.

## Project-side companion

A project that uses this methodology should have a thin domain skill that:
- Lists the specific scripts (`derive-<source>.ts`, `house-logo-rehost.ts`, etc.).
- Names the storage helper (`fetchAndStore` from `scripts/lib/images.ts`, or equivalent).
- Documents the table of known sources for the domain — which work, which are blocked by Cloudflare, which CSS selectors apply.
- Tracks the storage key prefix conventions.
- References this skill for the rate envelope and execution discipline rather than restating it.