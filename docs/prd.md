# PRD — Kudos (minimal Testimonial.to clone)

Source: course Module 13 (videos 13-01 reference walkthrough, 13-03 PRD). Trimmed to a minimal v1.

## Product
Business owners create public **Spaces** that collect testimonials from respondents (no account needed), review them in an inbox, publish selected ones through an embeddable wall, and upgrade from Free to Pro via Stripe.

## Roles
- **Owner**: registered user. Manages spaces, testimonials, embeds, billing.
- **Respondent**: public visitor. Submits a testimonial at `/{slug}`, gives consent.

## Features
1. **Auth** — register, login, logout, password reset, email verification.
2. **Spaces** — name (slug generated, unique), logo, header title, custom message (markdown), star-rating toggle, theme (light / dark / brand), field config: name + email always required; optional `company`, `title`, `social_link`, `photo`, each with enabled + required toggles. Live preview while editing.
3. **Public collection page** `/{slug}` — themed; text testimonial form (rating, text, configured fields, consent checkbox); thank-you state; rate limited.
4. **Inbox** per space — list, filter (all / favorite / published / hidden), edit text, favorite, hide, publish, delete.
5. **Embed** — iframe wall `/embed/{public_id}` showing published testimonials only, never emails; copy-paste snippet.
6. **Dashboard** — totals (spaces, testimonials, unique respondents), plan usage, testimonials-per-day chart (7 / 30 / 90 days), dismissible upgrade banner on Free.
7. **Billing** — Free vs Pro, Stripe Checkout (test mode), success page verified server-side, webhooks with signature check, billing portal link. Free limits: 1 space, 10 testimonials/space. Downgrade never deletes data; over-limit spaces stop accepting.

## Security
Owner-only access to own data (policies); non-sequential public IDs (ULID); server-side validation; escape/sanitise testimonial text; restrict upload type/size; rate limit auth + public submit; verify Stripe signatures; never expose respondent email via embed/API; dates in UTC.

## Out of scope (v1)
Video/audio testimonials, custom fields beyond the predefined, teams, custom domains, API, integrations, import, social publishing, AI editing, annual plans, localization.

## Definition of done
Register → create space → respondent submits → owner publishes → embed shows it → owner upgrades (Stripe test card) and sees Pro everywhere; tests, Pint and static analysis green.
