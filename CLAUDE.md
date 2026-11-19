# Kudos — Claude Code guide

Minimal Testimonial.to clone. Laravel 13 + Inertia 3 React, PHP 8.5, Postgres 18, Stripe (Cashier, test mode). Requirements: `docs/prd.md`. Data model: `docs/data-model.md`.

## Layout
- `codes/` Laravel app. `docker/` compose stack (template: edotco-poc-ms `codes/` + `docker/`). Everything runs in Docker; do not assume host PHP/Node.
- AIDLC workflow: run `/aidlc` (installed v2.11.4, harness `claude`); artifacts under `aidlc/spaces/default/intents/`. Project hooks in `scripts/hooks/`.

## Commands (repo root)
- Up: `docker compose -f docker/docker-compose.yml up -d --build` → app http://localhost:8010, vite :5180, Mailpit http://localhost:8030
- Shell: `docker compose -f docker/docker-compose.yml exec app bash` (alpine: `sh`)
- Tests: `docker compose -f docker/docker-compose.yml exec -T app php artisan test --compact`
- Format: `... exec -T app vendor/bin/pint` ; check: `vendor/bin/pint --test`
- Types/lint (TS): `... exec -T vite npm run types` / `npm run lint` (the vite service is plain `node:26-alpine`). One-off Node: `docker run --rm -v "$PWD/codes:/app" -w /app node:26-alpine sh -c "npm run types"`
- Security audit: `make audit` (composer, npm, Trivy config/secrets/images); Lighthouse: `scripts/lighthouse.sh <path> <name> [mobile|desktop] [light|dark]` against the prod stack
- Prod build: `make prod` (needs `docker/.envs/app.prod.env`); outage drill: stop the `app` service and open the edge URL
- Stripe webhooks: `docker compose -f docker/docker-compose.yml --profile billing up stripe`
- Demo login: demo@kudos.test / password (seeded, local only)

## Coding standards (BE + FE, enforced by critic)
- PHP: `declare_strict_types`, PSR-12 (Pint `codes/pint.json`), `final` classes, typed props/params/returns, no `mixed`, no loose `==`. Larastan level 8 (`codes/phpstan.neon`; baseline covers starter-kit code only, never add new baseline entries).
- DTOs: readonly `final` classes in `app/Data/<Domain>/` built from validated FormRequests; controllers pass DTOs to Actions, never raw arrays/`$request->all()`.
- Enums: backed PHP enums in `app/Enums/` (SpaceTheme, TestimonialStatus, Plan...) for every fixed value; cast on models; mirror as TS union types.
- Early return / guard clauses; max one nesting level; no `else` after return.
- DRY + SOLID: single-purpose Action classes (`app/Actions/`), Policies for authorization, constructor injection, interfaces for external services (Stripe gateway). Thin controllers, no business logic in React.
- TS: `strict` on, no `any`, explicit prop types, shared types in `resources/js/types/`, one component per file, logic in hooks, no duplicated markup (extract component).
- Names say intent; small functions; comments only for non-obvious why.

## Versions
Latest stable of every component, always (PHP, Laravel, Node, npm and composer packages, Docker images); upgrade them together. Look versions up (packagist, npm registry, Docker Hub) rather than assuming. Held back on purpose: TypeScript 6.0.x (typescript-eslint has no TS 7 support yet) and no `eslint-plugin-react` (no ESLint 10 support). Recheck both when touching dependencies.

## Logging (JSON 5W on stderr)
- Channel `stderr_json`, formatter `App\Logging\FiveWFormatter`: one JSON object per line with `who`, `what`, `where`, `when`, `why`, plus `request_id`, `trace_id` and `client` (device type, OS, browser, timezone, screen, connection, language). Env: `LOG_CHANNEL`, `LOG_LEVEL`, `LOG_FORMAT=json|text`, `LOG_ACCESS=all|errors|off`, `LOG_ACCESS_SLOW_MS`, `LOG_TRACE_LIMIT`, `LOG_SERVICE`.
- Log with context keys the formatter understands: `event`, `outcome` (ok|refused|degraded|failed), `status`, `reason`, `hint`, `duration_ms`, `exception`. Never log secrets, bodies or query values (only query keys); the formatter redacts keys like password/token/secret.
- Every request gets `X-Request-ID` (accepted from the edge/client if valid, else generated) and the id is echoed on every response and error page. Browser errors go to `POST /client-logs` via `resources/js/lib/logger.ts`.

## Errors and resilience
- No bare 500: `ErrorResponder` + `ExceptionMapper` render a friendly page (HTML) or `{error, code, dependency, request_id}` (JSON). Database or Stripe down = 503 + `Retry-After`; an unexpected bug = friendly 500 page, logged. In `APP_DEBUG` bugs still show their trace.
- Probes `/livez` and `/readyz` live outside the web group (no session). The edge nginx serves the static `public/outage.html` (503, `Retry-After`, no-store) when the app does not answer; `public/status/*` is served by the edge itself; polling backoff is `OUTAGE_FIRST_MS` / `OUTAGE_LONGEST_MS`.
- Outbound calls that can fail transiently go through `App\Support\Resilience\Retrier` (exponential backoff with jitter; `RETRY_ATTEMPTS`, `RETRY_BASE_DELAY_MS`, `RETRY_MAX_DELAY_MS`, `RETRY_FACTOR`, `RETRY_JITTER=full|equal|none`, `RETRY_BUDGET_MS`). Stripe is wrapped by `ResilientBillingGateway`; exhausted retries become `BillingUnavailable`.
- New env settings go in `docker/.envs/app.env.example` (dev defaults merge in automatically) and `app.prod.env.example`.

## Translations
All user-facing text lives in `codes/lang/en.json` (flat, dotted keys, `:placeholder` syntax). PHP: `__('key')`. React: `t('key')` from `@/lib/i18n` (keys are type-checked; `tDynamic`, `tc` for run-time keys and plurals; never call `t()` at module top level). Add keys with `python3 codes/scripts/lang_add.py partial.json`. The outage page's words come from `public/status/lang.json`, generated by `php artisan lang:export-status`. Only English for now. Validation and mail wording still come from Laravel's own lang files.

## Files that must not be committed or shipped
- Git: `.gitignore` covers secrets (`docker/.envs/app*.env`, `secrets/`, `codes/.env`), dependencies and build output (`vendor`, `node_modules`, `public/build`, `public/hot`), generated files (`public/status/lang.json`) and most Lighthouse reports. `.gitattributes` marks lockfiles and generated docs as generated and keeps AI tooling, docs and scripts out of `git archive`.
- Docker: `docker/Dockerfile.dockerignore` lets only the app source, php/nginx config and entrypoints into the build context; `.env`, secrets, `.git`, AI tooling, docs, tests, dependencies and build output never enter an image. Dependencies are installed and assets built inside the image from the lockfiles.
- Fonts are self-hosted (`@fontsource-variable/*`, bundled by Vite); never add a third-party font or script origin (the CSP forbids it).

## Rules
- Never edit `docker/.envs/app.env` or `codes/.env` (hook blocks it); change `app.env.example` and tell the user.
- Tests use sqlite :memory: via phpunit.xml; the compose service must NOT pass env_file/DB env to the container, or tests hit the dev Postgres.
- Only the `app` container writes `codes/.env` (atomically); queue waits for it. Entrypoint and Dockerfile changes need `docker compose up -d --build`, not just a recreate. `flock` is unreliable across containers on bind mounts.
- Business rules live in Actions/Services, not controllers or React. Authorization via Policies; owner-only.
- Public IDs are ULIDs. Never expose respondent email in embed/public JSON. Escape/sanitise testimonial text.
- Free plan limits: 1 space, 10 testimonials/space. Never delete data on downgrade.
- Every feature: plan → implement → verify (`verify-feature` skill, `critic` subagent) → commit. Small commits.
- Commits and PRs: never add `Co-Authored-By` or any Claude attribution trailer (user rule, overrides harness defaults).
- Parallel work uses git worktrees (`git worktree add ../kudos-<name> -b feature/<name>`), merged with `--no-ff`.
