# Kudos — minimal Testimonial.to clone

Capstone for the Agentic Engineering course (Module 13), built with Claude Code.
Laravel 12 + Inertia React (TypeScript) + Postgres + Stripe (Cashier, test mode), all in Docker.

Requirements: [docs/prd.md](docs/prd.md) · Data model: [docs/data-model.md](docs/data-model.md) · Screenshots: [docs/screenshots/](docs/screenshots/)

## Run it

Needs Docker with Compose v2. Everything runs in containers (no host PHP/Node).

```bash
cp docker/.envs/app.env.example docker/.envs/app.env   # once
make dev                                               # build + start (migrates and seeds on boot)
```

| What | URL |
|---|---|
| App | http://localhost:8010 |
| Mail inbox (Mailpit) | http://localhost:8030 |
| Vite dev server | http://localhost:5180 |

Demo login (seeded, local only): `demo@kudos.test` / `password`.
Ports are bound to 127.0.0.1; override with `APP_PORT`, `VITE_PORT`, `DB_PORT`, `MAILPIT_PORT`.

```bash
make test    # PHPUnit (sqlite in-memory)
make lint    # Pint + Larastan level 8
make types   # tsc --noEmit
make down
```

### Production-style stack

```bash
cp docker/.envs/app.prod.env.example docker/.envs/app.prod.env   # fill in APP_KEY, DB password, Stripe, mail
make prod                                                        # immutable images, nginx edge on 127.0.0.1:8010
make migrate                                                     # migrations are explicit in prod
```

`docker/docker-compose.prod.yml` follows the layout used in the other projects: multi-stage `docker/Dockerfile`
(`dev` | `prod` php-fpm | `edge` nginx), read-only rootfs, non-root, `cap_drop: ALL`, resource limits, loopback-only port
(put your TLS proxy in front), no bind mounts, no Vite/Mailpit, Postgres not published. Config/route/view caches are built at boot from the container env.

### Stripe (test mode)

Set `STRIPE_KEY`, `STRIPE_SECRET`, `STRIPE_PRO_PRICE_ID`, `STRIPE_WEBHOOK_SECRET` in your env file. For webhooks locally:
`docker compose -f docker/docker-compose.yml --profile billing up stripe` (forwards to `/stripe/webhook`). Test card `4242 4242 4242 4242`.
Without keys the billing page explains that Stripe is not configured and the Upgrade button is disabled.

## Features

| Feature | Status |
|---|---|
| Register / login / logout / password reset | Done (Laravel starter kit) |
| Email verification (required for the app area) | Done — mails land in Mailpit |
| Spaces: name → unique slug, logo, header, markdown message, rating toggle, 3 themes, optional fields (company, title, social link, photo) with enabled/required toggles, live preview | Done |
| Public collection page `/{slug}`: themed, config-driven validation, consent, rate limited, thank-you state | Done |
| Inbox: filters, publish / hide / favorite / edit / delete | Done |
| Embed wall `/embed/{id}` + JSON feed + copyable iframe snippet; published only, never exposes email | Done |
| Dashboard: totals, unique respondents, plan usage, 7/30/90-day chart, dismissible upgrade banner | Done |
| Billing: Free vs Pro, Stripe Checkout, server-side success check, signature-verified webhooks (Cashier), billing portal, plan limits (1 space / 10 testimonials per space on Free; downgrade never deletes data) | Built and unit-tested with a fake gateway. **Not verified against live Stripe** (no test keys were available) |
| Owner-only authorization (policies), ULID public ids, HTML stripped from testimonials | Done, covered by tests |
| Video/audio testimonials, custom fields, teams, custom domains, integrations, localization, annual billing | Out of scope (as in the PRD) |

Known gaps: only Postgres is exercised in dev (tests use sqlite); no SSR/CSP tuning; browser checks were manual — there is no automated end-to-end suite.

## Design

Direction documented in [PRODUCT.md](PRODUCT.md) and [DESIGN.md](DESIGN.md), drawn from the Shell Console glass language and the Python Learning design rules.
Warm paper canvas with an equal dark twin (oklch tokens in `codes/resources/css/app.css`), one coral accent, amber reserved for star ratings,
Fraunces serif for headlines and quotes with Instrument Sans for the UI. Liquid glass only on floating chrome (sidebar, top bar, menus, dialogs);
content sits on translucent panes. CSS-only motion (staggered rise, button lift/press, drifting hero cards), disabled under `prefers-reduced-motion`
and `prefers-reduced-transparency`. Lucide icons throughout, no emoji, no gradient text. Space themes (light/dark/brand) are the owner's choice on the public page and embed.
Theme toggle (light / dark / system) is in the app header, auth pages and landing page. Layouts were checked at desktop and phone width.
Current screenshots: `docs/screenshots/design-*.jpg`.

## Code standards

Enforced by Pint (`pint.json`: PSR-12, strict types, `final`), Larastan level 8 (baseline covers starter-kit code only), TypeScript `strict`.
Backed enums (`app/Enums`), readonly DTOs (`app/Data`), single-purpose Actions (`app/Actions`), Policies, a `BillingGateway` interface over Stripe,
early returns, one component per file on the frontend. Details in [CLAUDE.md](CLAUDE.md).

## Agentic tools used (and where)

| Tool | Where |
|---|---|
| **AI-DLC** (awslabs, v2.11.4) | Installed and configured for Claude Code (`.claude/`, `aidlc/`). `/aidlc` was started but the build itself ran as plan → implement → verify directly; `docs/prd.md`, `docs/data-model.md` stand in for inception artifacts. |
| **Plan mode + video analysis** | Course videos were turned into a requirements summary and plan before any code. |
| **Subagents** | A `general-purpose` agent built the embed wall + dashboard in an isolated git worktree while the main session built spaces/public/inbox/billing; `Explore` agents summarised the videos. A `critic` reviewer agent is defined in `.claude/agents/critic.md` (not yet run on this code). |
| **Parallel work + merge** | Branch `worktree-agent-…` (embed + dashboard) merged with `--no-ff` into `main`; conflicts in `package.json`/lockfile resolved by hand. See `git log --graph`. |
| **Skill** | `.claude/skills/verify-feature/SKILL.md` (tests → Pint → Larastan → on-plan diff → UI smoke → critic). |
| **Hooks** | `scripts/hooks/protect-env.sh` (PreToolUse: blocks edits to env files) and `pint-on-edit.sh` (PostToolUse), wired in `.claude/settings.json`. |
| **MCP** | Playwright MCP configured in `.mcp.json`; UI verification in this build used the desktop app's built-in browser (screenshots in `docs/screenshots/`). |
| **CLAUDE.md** | Commands, layout and rules, including the coding standards. |

## Reflection (draft — edit before submitting)

_What worked:_ planning from the videos first, then a strict foundation (enums, DTOs, policies, migrations) before features, made the work parallelisable:
the embed/dashboard agent only needed the contract (models, routes files, types) and its branch merged with two trivial conflicts. Static analysis at level 8 plus
tests caught real mistakes early (nullable relations, untyped resources).

_Where it went wrong:_ the Docker dev stack cost the most time. Passing `env_file` into the containers made PHPUnit's `<env>` values lose, so the first test run hit the dev
Postgres; `artisan serve` ignores container env, so config had to be merged into `.env`; three containers raced to rewrite that `.env` (fixed with `flock`); the prod image
shipped dev-generated bootstrap caches until a `.dockerignore` was added. A one-line Python edit also truncated a file by opening it for write before reading. Parallel work duplicated a clipboard hook and a star-rating
component, which I deduplicated after the merge.

_Next time:_ write the Docker/test-isolation rules into CLAUDE.md before the first run, give parallel agents a shared component inventory to avoid duplicates, run the `critic` subagent
and a Playwright E2E suite per unit instead of manual checks, and get Stripe test keys up front so billing is verified end to end.
