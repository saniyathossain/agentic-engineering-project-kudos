# Kudos — minimal Testimonial.to clone

Capstone for the Agentic Engineering course (Module 13), built with Claude Code.
Laravel 13 + Inertia 3 React (TypeScript) + Postgres 18 + Stripe (Cashier, test mode), all in Docker. Latest stable of every part of the stack (PHP 8.5, Node 26, Vite 8, nginx 1.31); two packages are held back on purpose, see [CLAUDE.md](CLAUDE.md#versions).

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
Every service has CPU, memory, swap and pids limits (override with `APP_MEM_LIMIT`, `APP_CPUS`, `QUEUE_*`, `VITE_*`, `DB_*`). Ports are bound to 127.0.0.1; override with `APP_PORT`, `VITE_PORT`, `DB_PORT`, `MAILPIT_PORT`.

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

## Observability and resilience

- **Logs**: JSON on stderr, one object per line, grouped `who` / `what` / `where` / `when` / `why` (the Shell Console shape) plus `request_id`, `trace_id` and `client` (device type, OS, browser, timezone, screen, connection, language). Browser errors are shipped to the same stream via `POST /client-logs`. Configure with `LOG_*` in `docker/.envs/app.env`; secrets, bodies and query values are never logged.
- **Request id**: accepted from the edge or caller when valid, otherwise generated; echoed in the `X-Request-ID` header and shown on every error page.
- **No bare 500**: failures render a friendly page (or structured JSON) with the request id. A database or Stripe outage is a 503 with `Retry-After`. In prod the nginx edge serves a static outage page (503) when the app does not answer; it polls `/readyz` with exponential backoff and reloads when the app is back (`OUTAGE_FIRST_MS`, `OUTAGE_LONGEST_MS`). The browser shows a connection banner with the same backoff when a request cannot reach the server.
- **Retry with exponential backoff and jitter** around outbound calls (Stripe): `RETRY_ATTEMPTS`, `RETRY_BASE_DELAY_MS`, `RETRY_MAX_DELAY_MS`, `RETRY_FACTOR`, `RETRY_JITTER=full|equal|none`, `RETRY_BUDGET_MS`.
- **Probes**: `/livez` (process) and `/readyz` (database critical; cache and storage advisory), outside the session stack.
- Known limit: an unexpected bug is still a 500 (a friendly page that is logged at error level); validation and mail wording come from Laravel's own language files.

## Documentation

| Topic | Where |
|---|---|
| Security controls, audit results, accepted risks | [docs/security.md](docs/security.md) · `make audit` |
| Performance (Lighthouse, the engine behind Google PageSpeed) and responsive checks | [docs/performance/](docs/performance/) · `scripts/lighthouse-all.sh` |
| HTTP API: OpenAPI 3.1, Postman, Insomnia and Bruno collections, every success and error case | [docs/api/](docs/api/) |
| Every environment variable | [docs/configuration.md](docs/configuration.md) |
| Requirements, data model, design | [docs/prd.md](docs/prd.md), [docs/data-model.md](docs/data-model.md), [PRODUCT.md](PRODUCT.md), [DESIGN.md](DESIGN.md) |
| AI workflow: plans, memory, research, skills, hooks | [docs/ai/](docs/ai/README.md) |

## Translations

All user-facing text is in `codes/lang/en.json` (flat dotted keys, `:placeholder` syntax), read by Laravel with `__()` and by React with `t()` (keys are type-checked). English only for now; add `lang/<locale>.json` to add a language.

## Design

Direction documented in [PRODUCT.md](PRODUCT.md) and [DESIGN.md](DESIGN.md), drawn from the Shell Console glass language and the Python Learning design rules.
Warm paper canvas with an equal dark twin (oklch tokens in `codes/resources/css/app.css`), one coral accent, amber reserved for star ratings,
Fraunces serif for headlines and quotes with Instrument Sans for the UI. Liquid glass only on floating chrome (sidebar, top bar, menus, dialogs);
content sits on translucent panes. CSS-only motion (staggered rise, button lift/press, drifting hero cards), disabled under `prefers-reduced-motion`
and `prefers-reduced-transparency`. Lucide icons throughout, no emoji, no gradient text. Space themes (light/dark/brand) are the owner's choice on the public page and embed.
Theme toggle (light / dark / system) is in the app header, auth pages and landing page. Layouts were checked at desktop and phone width.
Frosted chrome (`.frost`), chips, a dependency-free date picker (inbox date-range filter), placeholders and skeletons, animated Lucide icons that act out their meaning on hover (all transform/opacity, off under reduced motion). Current screenshots: `docs/screenshots/design-*.jpg`.

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

_What worked:_ planning from the course videos first, then a strict foundation (enums, DTOs, policies, migrations) before features, made work parallelisable. An agent built the embed wall and dashboard in a git worktree and merged with two trivial conflicts; later three agents moved ~300 UI strings into `lang/en.json` in parallel because each owned a disjoint set of files and a lock-safe merge helper. Static analysis at level 8, tests and an independent `critic` review caught real mistakes (nullable relations, an unhandled DB outage).

_Where it went wrong:_ the Docker dev stack cost the most time: container env beat PHPUnit's env (tests hit the dev database), `artisan serve` ignores container env, and three containers raced to rewrite one `.env` (flock does not work across containers on a bind mount; only one container may write it now). Upgrading to Laravel 13 / Inertia 3 left a stale compiled Blade view that rendered a blank page, which tests could not see because they never run the browser bundle; I only found it by opening the app. I also assumed Laravel 12 was current until corrected, and a one-line Python edit once truncated a file by opening it for write before reading it.

_Next time:_ look up versions before scaffolding, write the Docker and test-isolation rules into CLAUDE.md before the first run, open the app in a browser after every framework upgrade, give parallel agents a component inventory to avoid duplicates, and get Stripe test keys up front so billing is verified end to end.
