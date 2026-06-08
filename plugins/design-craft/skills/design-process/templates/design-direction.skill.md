---
name: {{PROJECT_SLUG}}-{{DIRECTION_SLUG}}
description: Use when building any {{PROJECT_NAME}} surface in the {{DIRECTION_NAME}} direction — {{ONE_LINE_DIRECTION_DESCRIPTION}}. Pairs with `{{PROJECT_SLUG}}-design-discipline` (the discipline runs alongside on different surfaces — they're not mutually exclusive). Triggers: {{TRIGGER_KEYWORDS}}.
---

# {{PROJECT_NAME}} — {{DIRECTION_NAME}}

A per-direction skill. The discipline skill is the constitution; this is the playbook for one specific aesthetic direction.

---

## Visual thesis (150 words)

{{VISUAL_THESIS}}

---

## Direction-specific tokens

These extend (don't replace) the core tokens from the discipline skill. List only what changes for this direction.

### Color overrides

| Token | Discipline default | This direction | Reason |
|---|---|---|---|
| `--bg` | `{{DEFAULT_BG}}` | `{{DIRECTION_BG}}` | {{REASON_1}} |
| `--surface` | `{{DEFAULT_SURFACE}}` | `{{DIRECTION_SURFACE}}` | {{REASON_2}} |
| `--accent` | `{{DEFAULT_ACCENT}}` | `{{DIRECTION_ACCENT}}` | {{REASON_3}} |

### Direction-specific tokens

```css
--{{DIRECTION_SLUG}}-{{TOKEN_1}}: {{VALUE_1}};
--{{DIRECTION_SLUG}}-{{TOKEN_2}}: {{VALUE_2}};
```

---

## Surface recipes

### Hero pattern

{{HERO_RECIPE}}

### Card pattern

{{CARD_RECIPE}}

### Button pattern

{{BUTTON_RECIPE}}

---

## Direction-specific motion

What animation patterns reinforce this direction? What contradicts it?

- **Reinforces:** {{MOTION_GOOD}}
- **Contradicts:** {{MOTION_BAD}}

---

## Reference exemplars for this direction

| Site | What we steal | Verdict |
|---|---|---|
| {{REF_1}} | {{STEAL_1}} | ADOPT |
| {{REF_2}} | {{STEAL_2}} | TRIAL |

---

## Cross-surface application

How does this direction apply across the four canonical surfaces?

| Surface | Application |
|---|---|
| Marketing landing | {{MARKETING_APPLICATION}} |
| Product surface (e.g. dashboard) | {{PRODUCT_APPLICATION}} |
| Onboarding flow | {{ONBOARDING_APPLICATION}} |
| Transactional / checkout | {{TRANSACTIONAL_APPLICATION}} |

---

## When to NOT use this direction

What surfaces should use a different direction instead? Be explicit — every direction has surfaces where it's the wrong tool.

{{WHEN_NOT_TO_USE}}
