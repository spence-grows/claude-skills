# The 5-Dimension Critique Rubric

Applied at Stage 6 of the playbook. Score each dimension 0–10. Total determines ship/no-ship.

---

## The dimensions

### Philosophy (0–10)

Does the surface have a coherent point of view, or is it a pastiche of trends?

- **10:** A first-time visitor could describe the design philosophy in one sentence after 30 seconds. The surface feels inevitable — no element is an arbitrary trend reference.
- **7–9:** Coherent direction, with one or two elements that don't pull their weight.
- **4–6:** Multiple competing references; the surface is "designed" but not pointed.
- **0–3:** A pile of trends. Glass + brutalism + a sticker pack. No center.

### Hierarchy (0–10)

Can a user read the surface at a glance? Does the eye land where it should?

- **10:** Three-second squint test passes. Primary action, primary content, secondary context are unmistakable.
- **7–9:** Reads correctly with a moment of orientation.
- **4–6:** User has to work to find what matters.
- **0–3:** Everything competes for attention. Nothing wins.

### Craft (0–10)

Is the execution clean — alignment, spacing, typography, color, motion?

- **10:** Everything is on the grid. Every spacing increment is intentional. Every font weight/size pairing is consistent across the surface. Color values are exact, not approximated. Motion has named easing curves and per-element durations.
- **7–9:** One or two visible craft slips (a misaligned edge, an inconsistent font weight).
- **4–6:** Multiple craft slips, but the underlying decisions are good.
- **0–3:** Sloppy execution. Misaligned, inconsistent, approximated.

### Function (0–10)

Does it work? A11y, touch targets, perf, edge cases, real content lengths.

- **10:** All touch targets ≥44px. All color pairs ≥4.5:1 contrast (or ≥3:1 for large text + explicit AA-large exemption). LCP <2.5s on 4G. INP <200ms. Works with real content lengths (long names, missing fields, max-length strings). Keyboard navigable. Screen-reader sensible.
- **7–9:** One or two function failures (e.g. one touch target slightly small, one a11y label missing).
- **4–6:** Multiple function failures; needs a remediation pass before ship.
- **0–3:** Doesn't work for real users in real conditions.

### Originality (0–10)

Would this be recognizably yours with the wordmark removed?

- **10:** Yes. A regular user would identify the brand from the design language alone. A competitor copying this would feel obviously derivative.
- **7–9:** Distinctive but shares language with a small set of obvious peers.
- **4–6:** Looks like a category — "AI startup," "fintech," "creator tool." Identifiable category, not brand.
- **0–3:** Anonymous. Could be any product. Default shadcn / default Tailwind / default Vercel.

---

## Ship/no-ship bands

| Total | Verdict | What to do |
|---|---|---|
| **40–50** | Ship with confidence | Add the surface to your discipline skill's Reference Exemplars as a "we did this well" anchor |
| **35–39** | Ship with caveat | Commit message must name the weakest dimension and the planned follow-up |
| **25–34** | Iterate | Return to Stage 3 (plan) or Stage 4 (draft). Do not ship |
| **0–24** | Do not ship | Return to Stage 1 (brief). The plan was wrong, not just the execution |

---

## The two-altitude AI slop test

Run this before scoring. It catches the failure mode where each dimension scores 6–7 but the whole thing still looks generic.

- **Category reflex:** Show the surface to someone unfamiliar with your product. Ask "what category of product is this?" If they name your category in under 5 seconds, you've designed *to the category* rather than *to your brand*. That's a slop signal.
- **Anti-reference reflex:** Identify the most-copied site in your category. Is any element of your surface visually adjacent to it? (Identical card radius, identical color, identical hero pattern.) If yes, change that element.

A surface that passes both reflexes earns a +1 Originality bonus. A surface that fails either gets capped at 6/10 on Originality regardless of other factors.

---

## The scene-sentence test

Used at Stage 3 to lock the mood before you draft. Write one sentence describing the surface as a physical scene. Good examples:

- "A folded broadsheet newspaper resting on a wooden cafe table at dusk."
- "A glass aquarium of layered tropical light, viewed from above."
- "A pegboard wall in a workshop, every tool in its labeled outline."

Bad examples (these mean the mood isn't locked):

- "A modern, clean, professional design."  *(generic adjectives, no scene)*
- "Something Vercel-y but warmer."  *(reference instead of scene)*
- "Whatever feels right."  *(no anchor at all)*

If you can't write the scene sentence, you're not ready for Stage 4.

---

## Before / After / Why audit format

When you ship the Stage 6 audit, format findings as a table with three columns:

| Before | After | Why |
|---|---|---|
| `border-radius: 8px` everywhere | `border-radius: 12px` on cards, `4px` on chips, `2px` on inputs | Cards are objects; chips are tags; inputs are slots. Different metaphors → different radii. |
| Headings in `Inter, 600` | Headings in `<your-display-font>, 500` | Inter is the AI-startup tell. The display font carries Philosophy and Originality scores. |

Each row is a discrete change. Each "Why" is a one-sentence rule that could be lifted into the discipline skill.

When you finish the audit, **lift the durable Why rules into the discipline skill itself** — that's how learnings compound. Otherwise the next session starts from zero.
