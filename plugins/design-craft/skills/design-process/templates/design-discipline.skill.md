---
name: {{PROJECT_SLUG}}-design-discipline
description: {{PROJECT_NAME}}-specific design discipline — the protected aesthetic posture, anti-patterns to refuse generating, accessibility/touch/performance/motion rules, and a curated reference-exemplar library by style. Invoke on every {{PROJECT_NAME}} UI/CSS decision: choosing tokens, picking type scales, drafting components, accessibility audits, evaluating reference sites, or whenever 'does this strengthen our voice or regress us toward generic AI' is the question. This skill is meant to be iterated — the Reference Exemplars section grows as we surface new best-in-class sites.
---

# {{PROJECT_NAME}} Design Discipline

> **How to use this file:** Replace every `{{PLACEHOLDER}}`. Delete the **Author's note** blocks once you've internalized them. Re-read this every time you start a design session. Edit it every time you ship an audit that surfaced a durable rule.

---

## Protected aesthetic posture

**Author's note — replace this section with your project's core aesthetic stance. Aim for 50–100 words. The goal is that a Claude session reading this paragraph alone could refuse a draft that violates the posture.**

{{ONE_PARAGRAPH_AESTHETIC_THESIS}}

Examples to spark yours (don't copy these):

- **Editorial / publication-grade:** "{{PROJECT_NAME}} reads like a small, well-edited print magazine. Wide margins, real typography (serif display + grotesk text + mono numerals), generous spacing, calm color. No glowing gradients. No glassmorphism. No 'productivity tool' chrome."
- **Glass / depth-first:** "{{PROJECT_NAME}} is a stack of frosted panes. Depth via blur and layering, not shadows. Hero photography supplies palette warmth; UI surfaces stay desaturated. Interactive elements are slightly more opaque than the surfaces they rest on."
- **Editorial-meets-warm:** "{{PROJECT_NAME}} feels like a handwritten travel journal printed on heavy paper. Hand-set type, ink-on-paper color values, subtle deckle edges on cards. Refuses the trip-coordinator-app aesthetic that every competitor inhabits."

---

## Brand voice (one paragraph)

**Author's note — what the voice sounds like in copy. Affects microcopy, button labels, empty states, error messages. The discipline skill enforces voice as much as visual choices.**

{{VOICE_PARAGRAPH}}

---

## Register — when to be "brand" vs "product"

- **Brand register** (marketing site, landing page, About page, fundraising materials): {{BRAND_REGISTER_DESCRIPTION}}
- **Product register** (the app surface itself, dashboards, settings, transactional flows): {{PRODUCT_REGISTER_DESCRIPTION}}

The two should feel adjacent but distinct. If your brand register is loud and your product register is quiet, that's a deliberate choice — not a bug.

---

## Core tokens

### Typography

| Role | Family | Weights | Notes |
|---|---|---|---|
| Display | `{{DISPLAY_FONT}}` | `{{DISPLAY_WEIGHTS}}` | `{{DISPLAY_NOTES}}` |
| Text | `{{TEXT_FONT}}` | `{{TEXT_WEIGHTS}}` | `{{TEXT_NOTES}}` |
| Mono / numerics | `{{MONO_FONT}}` | `{{MONO_WEIGHTS}}` | Tabular figures on |

**Banned for body copy:** Inter, Roboto, San Francisco system defaults. (These are the AI-startup tells. If you need a fallback, use the system serif or `Georgia`.)

### Color

**Strategy:** {{COLOR_STRATEGY}}  *(pick one: Restrained / Committed / Full-palette / Drenched)*

| Token | Value | Use |
|---|---|---|
| `--bg`         | `{{BG}}`         | Page background |
| `--surface`    | `{{SURFACE}}`    | Card / panel background |
| `--surface-2`  | `{{SURFACE_2}}`  | Elevated surface |
| `--ink`        | `{{INK}}`        | Primary text |
| `--ink-muted`  | `{{INK_MUTED}}`  | Secondary text |
| `--accent`     | `{{ACCENT}}`     | Primary interactive |
| `--accent-2`   | `{{ACCENT_2}}`   | Secondary interactive |
| `--positive`   | `{{POSITIVE}}`   | Success / confirmation |
| `--negative`   | `{{NEGATIVE}}`   | Error / destructive |

### Spacing

Use a single spacing scale. Don't invent values. **Recommended scale (4px base):** `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96`. Anything between is a craft slip and counts against the Craft score.

### Radius

| Element | Radius | Why |
|---|---|---|
| Cards | `{{CARD_RADIUS}}` | Cards are "objects" |
| Chips / tags | `{{CHIP_RADIUS}}` | Chips are smaller objects |
| Inputs | `{{INPUT_RADIUS}}` | Inputs are "slots" |
| Buttons | `{{BUTTON_RADIUS}}` | Match input radius or 1.5× |

---

## Anti-patterns — refuse to generate these

The list of "I see this and I know an AI wrote it" tells. Add to this list every time you catch one in an audit.

### Typography anti-patterns

- **Inter as the body font.** It's the AI-startup default. Pick something with a point of view.
- **Roboto, Open Sans, Lato as headings.** Same problem.
- **`font-family: -apple-system, ...` with no fallback strategy.** Fine for a prototype, slop for production.
- **Mixing 4+ font weights from the same family.** Two weights usually. Three if you're sure.

### Color anti-patterns

- **Purple gradients (`#7c3aed` → `#a78bfa`).** The "AI assistant" tell.
- **Pure black (`#000`) on pure white (`#fff`).** Too much contrast — use `#111` on `#fafafa` or warmer.
- **Aqua / teal as a "trustworthy fintech" hint.** It's a tell, not a strategy.
- **Status colors that are only color.** Always pair color with an icon or text label (function score).

### Component anti-patterns

- **The "AI startup hero" pattern:** centered headline + gradient blob + "Get started" button + grid of three logo monochromes. If you see this, redraw the page.
- **Card with `box-shadow: 0 4px 6px rgba(0,0,0,0.1)`.** The default Tailwind shadow. Use a shadow token with intentional offset and color.
- **`border-radius: 8px` on everything.** Different elements want different radii. See the Radius table.
- **Sticker emoji as UI iconography.** 🎉 in a button label is a slop tell.

### Voice / copy anti-patterns

- **"Effortless," "seamless," "delightful."** Generic adjectives that mean nothing.
- **Startup-slop names in placeholders:** "Acme," "Nexus," "[anything]ly." Use real-feeling names. ("Jane Doe Effect" — fake names should feel like real people.)
- **Em-dashes in user-facing copy.** AI tell. Use sentences or parentheticals.
- **Emoji in body copy of a serious surface.** Different register.

### Motion anti-patterns

- **`transition: all 0.3s ease`.** Animates layout properties. Performance disaster. Use specific properties + transform/opacity only.
- **Bounce or overshoot easing in product UI.** Reads as juvenile. Reserve for celebration moments only.
- **Mount animations on every page load.** Reads as theatre. Animate state changes, not arrivals.

{{PROJECT_SPECIFIC_ANTI_PATTERNS}}

---

## Accessibility floor (non-negotiable)

- **Touch targets ≥44×44px** on all interactive elements. Phone-thumb test must pass.
- **Color contrast ≥4.5:1** for body text, ≥3:1 for large text (≥18px or ≥14px bold).
- **Never status-by-color-alone.** Color + icon, color + text, or color + position.
- **Keyboard navigable.** Tab order must be logical. Focus rings visible (don't `outline: none` without a replacement).
- **Real content lengths.** Test with the longest plausible name, the longest plausible string, the maxed-out edge case.

---

## Performance floor

- **LCP <2.5s** on 4G mobile (Lighthouse mobile, simulated throttling).
- **INP <200ms.**
- **CLS <0.1.**
- **No layout shifts after the first paint.** Reserve space for images, embeds, and async content.
- **Font loading:** `font-display: swap` for display fonts; subset to the glyphs you actually use.

---

## Motion discipline

### Per-element duration table (lifted from Emil Kowalski)

| Element | Duration |
|---|---|
| Button press | 100–160ms |
| Tooltip | 125–200ms |
| Dropdown | 150–250ms |
| Modal | 200–500ms |

**Rule of thumb:** exit = 75% of enter. Modals don't dismiss as slowly as they appear.

### Named easing curves

```css
--ease-out-quart:  cubic-bezier(0.25, 1, 0.5, 1);
--ease-out-quint:  cubic-bezier(0.22, 1, 0.36, 1);
--ease-in-out:     cubic-bezier(0.65, 0, 0.35, 1);
--ease-drawer:     cubic-bezier(0.32, 0.72, 0, 1);
```

### Component principles

- `:active { transform: scale(0.97); }` on interactive elements — gives tactile feedback.
- Never `scale(0)` as the entry state — animate from `scale(0.96)` minimum (avoids the "popping into existence" tell).
- `transform-origin` discipline: dropdowns from `top center`, tooltips from the trigger edge, modals from `center center`.
- Use `@starting-style` for mount animations when possible.
- Gate hover effects behind `@media (hover: hover)` to avoid sticky-tap on touch devices.

---

## Reference exemplars

**Author's note — start with 3–5 sites you admire that are in your direction. Add a verdict for each. Update this section every time an audit surfaces a new exemplar.**

### Cross-style top picks

| Site | Style | What we steal | Verdict |
|---|---|---|---|
| {{EXEMPLAR_1}} | {{STYLE_1}} | {{STEAL_1}} | ADOPT |
| {{EXEMPLAR_2}} | {{STYLE_2}} | {{STEAL_2}} | ADOPT |
| {{EXEMPLAR_3}} | {{STYLE_3}} | {{STEAL_3}} | TRIAL |

### By style category

(Expand this as you research more reference sites. Group by editorial / minimalist / glass / brutalist / playful / etc.)

---

## Quality reflexes (apply continuously, not just at audit time)

### The two-altitude AI slop test
- **Category reflex:** could this design come from any product in our category?
- **Anti-reference reflex:** does this share visual DNA with the most-copied site in our category?

### The scene-sentence test
Write one sentence describing the surface as a physical scene. If you can't, the mood isn't locked.

### The 5-10-2-8 sourcing rule
- **5** search rounds for reference research
- **10** candidate sites collected
- **2** picked from each round
- **8** is the minimum craft score for inclusion

### Color strategy taxonomy
Pick one explicitly before drafting:
- **Restrained:** monochrome + 1 accent
- **Committed:** monochrome + 2 accents
- **Full-palette:** 5–7 hues used intentionally
- **Drenched:** single dominant hue across the surface

### Brand vs product register split
Be explicit about which register a surface lives in. See the Register section above.

### "Embody the role, not the medium"
You're not "making HTML." You're a {{PROJECT_NAME}} designer working in HTML. Different framing produces different output.

---

## Audit output format — Before / After / Why

When you finish a draft and run the Stage 6 audit, format findings as a table:

| Before | After | Why |
|---|---|---|
| `Inter, 600` headings | `{{DISPLAY_FONT}}, 500` headings | Inter is the AI-startup tell. Display font carries Originality. |

Each row is a discrete change. Each Why is a one-sentence rule that could be lifted into this skill.

When the audit completes, **lift the durable Why rules into this file**. That's how the discipline compounds.

---

## What's worth lifting from external skills

When you install vendored skills (impeccable, huashu-design, emil-design-eng), don't just rely on their in-context invocation. **Lift the durable principles into this file** so they survive a `/clear`. This file is the long-term memory of your design discipline; vendored skills are short-term context.

Examples of principles to lift:
- impeccable's anti-pattern rules (the ones that apply to your direction)
- emil-design-eng's per-element duration table (already lifted above)
- huashu-design's Direction Advisor philosophy clamps (if you ship a discipline that's editorial-adjacent, clamp Direction Advisor to philosophies #01 / #03 / #10 / #17 / #18 / #19)
