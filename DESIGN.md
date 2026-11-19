# Kudos — design system

Reference: the Shell Console glass language (translucent panes, specular edge, blur only on floating chrome, calm liquid motion) and the Python Learning rules (one accent, opaque cards for content, no decorative gradients, Lucide icons, honest copy).

## World
A warm paper canvas by day, a warm charcoal one by night, built from the same roles. Content sits on soft panes; only chrome that content scrolls under (sidebar, top bar, menus, dialogs) is liquid glass. One coral accent; amber is reserved for star ratings. Quotes are set in a serif; everything else in a clean sans.

## Tokens (`resources/css/app.css`, oklch)
- Ground `--background`, panes `--card` (translucent, no blur), glass `--glass` (blurred, for chrome), ink `--foreground`, secondary ink `--muted-foreground` (>= 4.5:1 both modes).
- Accent `--primary` coral (white text >= 4.5:1 light; dark ink text on a lighter coral in dark). `--star` amber. State: `--success`, `--destructive`.
- Radius: control 12 px (`rounded-xl`), card 20 px (`rounded-2xl`), pill full.
- Shadows `--sh-sm|md|lg|glass`, tinted with the ink hue, never pure black.
- Ambient: two low-chroma radial washes fixed behind the page (warm top-right, cool bottom-left; haze tones in dark).

## Type
- UI: Instrument Sans 400/500/600. Display and quotes: Fraunces 400/500/600 (`font-display`), tight tracking on large sizes.
- Scale: page title 30-36, section 20-24, body 15-16, small 13. Numerals tabular in stats. Line length for quotes 60-70ch.

## Surfaces
- `.pane`: content card (translucent gradient, hairline, soft shadow, specular top edge). No backdrop blur (cheap to scroll).
- `.glass`: sidebar, top bar, popovers, dialogs, mobile sheet. Blur 24 px + saturation. Falls back to a solid popover without `backdrop-filter`, under `prefers-reduced-transparency`.
- One lead card per page may use the accent tint (`.pane-accent`); everything else is a plain pane.

## Motion
CSS only. Blocks rise in (8 px + fade, 380 ms, liquid ease) with a 60 ms stagger via `--i`; buttons lift on hover and settle on press; theme switch cross-fades colours; hero cards drift slowly. All off under `prefers-reduced-motion`.

## Icons
Lucide, 16-20 px, stroke 1.75, always paired with text or an accessible name. Icon chips: 36 px rounded-xl tinted with the accent at 12%.

## Rules
No gradient text. No coloured side borders. No emoji. No glass on content. No stock-purple. Every control has a visible focus ring. Light and dark are checked together.
