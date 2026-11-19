---
name: feedback-design-preferences
description: Owner's UI design preferences (light/dark, glass/frosted, chips, pickers, animated icons, performance, no AI slop)
metadata:
  type: feedback
---

Design wants: dark and light modes of equal quality, aesthetic typography with tonal shades, liquid-glass / frosted surfaces, responsive layouts, motion and transitions, aesthetic Lucide icons that animate like Shell Console's, chips, date pickers, placeholders, and "unsloppiness" (no generic AI look) - all without hurting performance.

**Why:** the owner gave this on 2026-11-19 and pointed at the lnd-python (Python Learning) and Shell Console design systems.

**How to apply:** follow `DESIGN.md`: warm oklch tokens, `.frost` and `.glass` only on floating chrome, `.pane` for content, Fraunces for quotes/headings + Instrument Sans UI, `Chip` component, dependency-free `DatePicker`, animated icon classes (`ico-*`) and transform/opacity-only motion honouring `prefers-reduced-motion` and `prefers-reduced-transparency`. No gradient text, no emoji, no purple default. Check both themes and a phone width in the browser before calling it done. See [[kudos-capstone]].
