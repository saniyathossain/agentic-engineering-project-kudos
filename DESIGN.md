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
CSS only, transform and opacity only (compositor friendly); long lists use `content-visibility: auto`; page content dims slightly while Inertia loads. Blocks rise in (8 px + fade, 380 ms, liquid ease) with a 60 ms stagger via `--i`; buttons lift on hover and settle on press; theme switch cross-fades colours; hero cards drift slowly. All off under `prefers-reduced-motion`.

## Frost, chips, pickers
- `.frost`: glass with a stronger blur (32 px), brightness lift and a fine static grain. Used only where something floats over content: sticky header, popovers (date picker), dialogs. `.glass` for the sidebar and menus. Both drop blur under `prefers-reduced-transparency` or without `backdrop-filter`.
- `Chip` (`components/ui/chip.tsx`): tones neutral, accent, success, warning, danger, outline; optional dot or icon; `selected` is the ink pill; `asChild` turns a link or button into a filter chip. Status, plan, dates and filters all use it.
- `DatePicker` (`components/ui/date-picker.tsx`): popover month grid with arrow-key navigation, Today / Clear, min/max, no dependency, nothing mounted until opened. Days travel as `YYYY-MM-DD` strings (`lib/dates.ts`), so no timezone shifts them.
- Placeholders: every text input has a concrete example; loading uses `.skeleton` (a transform-only light sweep).

## Typographic shades
Three inks: `--foreground` (primary), `--ink-2` (secondary, `text-ink-2`), `--ink-3` (tertiary and placeholders, `text-ink-3`). `eyebrow` and `lead` utilities for labels and intro text; tabular numerals for figures; Fraunces for quotes and headings.

## Icons
Lucide, 16-20 px, stroke 1.75, always paired with text or an accessible name. Icon chips: 36 px rounded-xl tinted with the accent at 12%.
Animated icons (as in Shell Console): icons inside any pressable parent lift and grow a touch on hover/focus and settle on press; named icons act out their meaning on hover through a class (`ico-send` and `ico-up-right` nudge, `ico-heart` pops, `ico-trash` wiggles, `ico-plus` turns a quarter, `ico-pencil` tilts, `ico-sparkles` twinkles, `ico-sun`/`ico-moon` turn, `ico-eye` blinks, `ico-calendar` pops). A swapped icon pops in (`ico-swap`), a success check draws itself (`ico-draw`), a picked star twinkles. Transform and opacity only.

## Rules
No underlines on links, anywhere (`a { text-decoration: none }` in the base layer and in `public/status/status.css`). A link is told apart by the accent colour and a medium weight, shifts to the ink colour on hover and shows the focus ring from the keyboard; links inside running text use `TextLink`. No gradient text. No coloured side borders. No emoji. No glass on content. No stock-purple. Every control has a visible focus ring. Light and dark are checked together.
