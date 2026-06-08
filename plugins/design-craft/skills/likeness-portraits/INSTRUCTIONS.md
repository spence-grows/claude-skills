# Likeness Portraits — Detailed Instructions

A complete walkthrough of the portrait generation process, from initial setup through batching and code integration.

---

## What This Produces

A directory of consistently-styled portrait illustrations of named individuals — authors, historical figures, team members, whoever the project needs. Each portrait is saved as a `kebab-case-name.jpg` (or `.png` / `.webp`) file the app references directly by slug.

The default style used as a reference: minimalist single-weight line-art stencil, one dark ink color on a warm cream background, head-and-shoulders bust, square format. This style was produced across 76 author portraits for a literary dashboard and reads as editorial rather than AI-generated.

---

## Prerequisites

1. **nano-banana-2 MCP installed and active.** The skill uses `mcp__nano-banana-2__generate_image` and `mcp__nano-banana-2__edit_image`. Verify it's connected before starting — if it's not listed in your active MCP servers, the workflow can't proceed.

2. **An output directory in the project.** Typically `public/portraits/` for a Next.js project. Create it if it doesn't exist:

   ```bash
   mkdir -p apps/web/public/portraits
   ```

3. **A subject list.** This can be:
   - A list of names pasted directly into the conversation
   - A TypeScript/JSON data file that already contains attribution or name fields (e.g. `editorial-quotes.ts`)
   - A spreadsheet or plain `.txt` file with one name per line

---

## Step 1 — Invoke the Skill

In your Claude Code session:

```
/likeness-portraits
```

Or just describe what you want — the skill triggers automatically when you ask to generate portraits of a list of people.

---

## Step 2 — Style Configuration (First Run Only)

On the first run in a project, before any image is generated, Claude will ask you to configure the visual style. This is a **single grouped question** — you can answer all fields at once, or just say **"use defaults"** to get the spence.growth-style output (forest green lines, warm cream background, stencil line art, square format).

### The Fields

| Field                  | What It Controls                            | Default                          |
| ---------------------- | ------------------------------------------- | -------------------------------- |
| `line_color`           | The color of every line in the illustration | `#1A4735` (forest green)         |
| `background_color`     | The flat background behind the subject      | `#FFFCF1` (warm cream)           |
| `composition`          | How much of the subject is shown            | Head-and-shoulders bust          |
| `line_style`           | The character of the line work              | Minimalist single-weight stencil |
| `detail_level`         | How many interior lines appear              | Low-to-medium                    |
| `aspect`               | Image proportions                           | 1:1 square                       |
| `attire_era`           | How to dress the subject                    | Period-appropriate               |
| `background_treatment` | What's behind the subject                   | Flat, paper texture OK           |
| `output_dir`           | Where files are saved                       | Inferred from project            |
| `file_format`          | File extension                              | `jpg`                            |

### Tips for Choosing

- **`line_color`:** Match your brand's primary or text color. Dark colors (navy, forest green, charcoal, burgundy) work best — light ink on cream washes out.
- **`background_color`:** Match your page or card background. The portrait will be composited directly onto the UI, so the background colors should be identical.
- **`line_style` options:**
  - `stencil` — clean, minimal, continuous strokes. Reads as intentional and designed.
  - `loose sketch` — organic, hand-drawn feel. Works for creative/artistic projects.
  - `cross-hatched` — dense, engraving-like. Good for academic or archival aesthetics.
  - `woodcut` — high-contrast, bold. Works at small sizes.
  - `etched` — fine parallel lines, classical. Good for historical subjects.
- **`detail_level`:** Low = fewer lines, more impressionistic, reads well at small sizes. High = more likeness fidelity, but can look busy at small sizes.
- **`composition`:**
  - `head-and-shoulders bust` — the face is dominant, reads well in circular avatars
  - `shoulders-up` — tighter crop, good for icon-sized displays
  - `waist-up` — lets clothing play a bigger role (useful when era/role identity matters)

### What Gets Saved

Your answers are saved to `{output_dir}/.portrait-style.json`. Claude reads this file on every subsequent run — you will **never be re-prompted for style** unless you explicitly ask to change it (e.g. "update the portrait style to use dark teal").

---

## Step 3 — Subject List and Slugs

Provide your list of names. Claude will:

1. **Parse names** from whatever format you provide (TypeScript array, plain list, spreadsheet paste)
2. **Generate slugs** — `kebab-case` with diacritics stripped:
   - `Marcus Aurelius` → `marcus-aurelius`
   - `Brené Brown` → `brene-brown`
   - `W.E.B. Du Bois` → `web-du-bois`
   - `bell hooks` → `bell-hooks`
3. **Diff against existing files** — scan `output_dir` and skip any slug that already has a file. Re-runs only generate the gaps.
4. **Flag uncertain subjects** — if a name is ambiguous or the subject is living/obscure, Claude will ask for a reference photo before generating (see Step 5).

---

## Step 4 — Test Portrait (Required)

Before generating the full batch, Claude generates **one portrait** from near the middle of your list (so you see a typical subject, not the most-famous one).

**Review it carefully:**

- Does the line color match your UI?
- Is the background the right shade?
- Is the likeness plausible?
- Does the line density/detail work at the size you'll display it?
- Is the composition right for your layout (circular avatar vs. bleed card vs. full card)?

**If it needs adjustment**, describe what's off — Claude updates `.portrait-style.json` and regenerates the test portrait. Common adjustments:

- "The lines are too thin / too thick" → adjust `detail_level` or add stroke weight to `line_style`
- "The background is too yellow" → adjust `background_color` hex
- "The crop feels too tight" → switch composition to `waist-up`
- "It looks too sketchy" → switch `line_style` to `stencil`

**Once you approve**, batch generation begins.

---

## Step 5 — Living or Obscure Subjects

The image model has strong priors for well-known historical figures. For **living people** or **obscure historical figures**, it will generate a plausible but potentially inaccurate face.

**The rule:** For any living person, always supply a reference photo. For obscure historical figures, supply a reference if you have one; if not, decide whether to skip them.

To supply a reference:

1. Drop the photo into the Claude conversation
2. Claude uses `mcp__nano-banana-2__edit_image` with the reference image to stylize the actual likeness rather than generate a synthetic one

If you don't have a reference and the subject is living, Claude will skip that portrait and tell you — it won't silently invent a face.

---

## Step 6 — Batch Generation

After the test portrait is approved, Claude generates the rest in batches of ~5 concurrent calls. This keeps the process fast while avoiding MCP rate limits.

Progress is reported as slugs complete. If any individual generation fails, Claude retries once automatically before flagging it for manual follow-up.

Files land in `output_dir` as `{slug}.{file_format}` — e.g. `public/portraits/maya-angelou.jpg`.

---

## Step 7 — Code Integration

Once files are generated, wire them into your app. There are two common patterns:

### Pattern A: Static Import Map

For a small fixed set, manually maintain a `Set` or record of covered slugs:

```ts
// lib/utils/portrait-slugs.ts
export const PORTRAIT_SLUGS = new Set([
  "marcus-aurelius",
  "maya-angelou",
  "carl-jung",
  // ... add as you generate more
]);
```

Simple but requires manual updates with each new batch.

### Pattern B: Build-Time Directory Scan (Recommended)

Generate the set at build time by reading the output directory. No manual maintenance required — each new portrait batch is automatically included:

```ts
// In a server component or data fetcher
import fs from "fs";
import path from "path";

const portraitsDir = path.join(process.cwd(), "public/portraits");

export const HAS_PORTRAIT = new Set(
  fs
    .readdirSync(portraitsDir)
    .filter((f) => /\.(jpg|png|webp)$/.test(f) && !f.startsWith("."))
    .map((f) => f.replace(/\.[^.]+$/, "")),
);
```

### Filtering Data to Portrait-Backed Entries

If your content (quotes, cards, bios) has a name field, filter to only entries with a portrait. Provide a graceful fallback to the full set so the UI never goes empty:

```ts
export function getDailyQuote(quotes: Quote[]) {
  const withPortrait = quotes.filter((q) =>
    HAS_PORTRAIT.has(slugify(q.attribution)),
  );
  return withPortrait.length > 0 ? pickByDay(withPortrait) : pickByDay(quotes); // fallback: no portrait, still show the quote
}
```

### Slugify Helper

Keep slugification consistent between generation and consumption:

```ts
export function slugify(name: string): string {
  return name
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "") // strip diacritics
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-") // non-alphanumeric → hyphen
    .replace(/^-|-$/g, ""); // trim leading/trailing hyphens
}
```

Test it against any edge cases in your subject list before generating — the slug must be identical at generation time and consumption time.

### Using Portraits in UI

Reference portraits by building a path from the slug:

```tsx
// In a card or quote component
const portraitSrc = `/portraits/${slugify(attribution)}.jpg`;

<Image
  src={portraitSrc}
  alt={attribution}
  width={80}
  height={80}
  className="rounded-full object-cover"
/>;
```

For a card with portrait bleed (editorial style):

```tsx
<div className="relative overflow-hidden rounded-xl">
  {/* Portrait fades into the top-right corner of the card */}
  <div
    className="absolute top-0 right-0 w-32 h-40 pointer-events-none"
    style={{
      backgroundImage: `url(${portraitSrc})`,
      backgroundSize: "cover",
      backgroundPosition: "center top",
      maskImage: "linear-gradient(to bottom left, black 0%, transparent 70%)",
      WebkitMaskImage:
        "linear-gradient(to bottom left, black 0%, transparent 70%)",
    }}
  />
  {/* Card content */}
  <div className="relative z-10 p-5">...</div>
</div>
```

---

## Adding More Portraits Later

Just run `/likeness-portraits` again with a new list of names. Claude will:

1. Read the existing `.portrait-style.json` (no re-prompting)
2. Diff the new names against what's already in `output_dir`
3. Skip everything that exists
4. Generate only the new ones (still test-one-first if it's been a while since the last batch)

---

## Changing the Style Across an Existing Set

If you want to re-style all portraits (e.g. brand rebrand from forest green to navy):

1. Ask Claude to update `.portrait-style.json` with the new values
2. Delete (or move to a backup folder) the old portraits
3. Run `/likeness-portraits` with the full subject list — it will regenerate everything

Note: this is a deliberate, destructive operation. The skill won't overwrite existing files without explicit confirmation.

---

## Troubleshooting

| Symptom                                    | Likely Cause                          | Fix                                                                                                                           |
| ------------------------------------------ | ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| Portrait looks nothing like the person     | Model has weak prior for this subject | Supply a reference photo via `edit_image`                                                                                     |
| Background is slightly off from the UI     | Hex mismatch between config and CSS   | Match hex values exactly, check for `#` prefix                                                                                |
| Lines look too thick at small sizes        | `detail_level` too high               | Drop to `low`, or specify smaller stroke weight in `line_style`                                                               |
| Some portraits are cropped awkwardly       | Composition not right for the subject | Adjust `composition` in config for this batch                                                                                 |
| MCP call fails mid-batch                   | Rate limit or transient error         | Claude retries once automatically; if it fails again, restart the batch from the failed slug                                  |
| Slug collision (two people with same slug) | Ambiguous name                        | Add a disambiguator to the name: `"Carl Jung (psychologist)"` — the hint goes in the prompt only, the slug uses just the name |
| Generated file is tiny / blank             | Model returned an error image         | Check the MCP response message; usually a content policy flag — rephrase the descriptor                                       |
