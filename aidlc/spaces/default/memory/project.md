# Project-Level Rules

> Project-specific specialisation and corrections. Loaded after `org.md` and
> `team.md` as strict-additive guidance.
> Populated by practices-discovery and the self-learning loop.
>
> Use sparingly: most teams don't need a project layer. Reach for it
> only when this specific project needs stable, durable guidance beyond the
> team practice (for example, package-specific release checks or an additional
> regression suite for a legacy component).

## Way of Working

Source: stated by the owner in chat (2026-11-19).
- Every feature runs plan -> implement -> verify: write the plan, build it, then run tests, Pint, Larastan and `tsc`; the `critic` subagent (`.claude/agents/critic.md`) reviews the diff against the plan before a commit.
- Small commits on feature branches; parallel work goes through git worktrees and merges with `--no-ff`.
- Commit messages and PR descriptions carry no attribution trailer (no `Co-Authored-By`).
- Run everything in Docker (`make dev`, `make prod`); the host has no PHP/Node toolchain to rely on.

## Walking Skeleton

<!-- Project-specific specialisation. Example: -->
<!-- The walking skeleton must exercise the legacy service adapter as well -->
<!-- as the new service boundary. -->

## Testing Posture

- PHPUnit feature tests per unit (sqlite in memory; the compose services must not pass DB env into containers or tests would hit the dev database).
- Static: Pint (PSR-12, strict types, final) and Larastan level 8 (baseline only for starter-kit code; never add new entries). Frontend: `tsc --noEmit` and ESLint, both clean.
- Failure paths are tested, not only happy paths: database down, Stripe down, bad input, cross-site posts, throttling.

## Guard Policy

<!-- Project-specific. Mode: strict, relaxed, or off. Strict here holds for every intent, whatever one person asks in chat; relaxed or off here applies to every intent whose policy came from its scope, unless the person sets another; changing this line changes it. A section under the retired Change Control heading, written by an earlier release, is still read. -->

## Deployment

- Layout follows the other projects: `codes/` (app) and `docker/` (Dockerfile with dev | prod | edge targets, `docker-compose.yml` for dev, `docker-compose.prod.yml` override, `.envs/*.env`).
- Prod: immutable images, php-fpm behind an nginx edge, read-only rootfs, non-root, `cap_drop: ALL`, CPU/RAM/swap/pids limits on every service, loopback-only port, migrations explicit (`make migrate`).
- The edge answers 503 with `Retry-After` and a static outage page when the app does not respond; polling intervals come from `OUTAGE_FIRST_MS` / `OUTAGE_LONGEST_MS`.

## Code Style

- PHP: `declare(strict_types=1)`, PSR-12, `final` classes, typed everything, readonly DTOs in `app/Data`, backed enums in `app/Enums` for every fixed value, single-purpose Actions, Policies for authorization, constructor injection, interfaces for external services, early returns, DRY, SOLID.
- TypeScript: strict, no `any`, one component per file, logic in hooks, shared types in `resources/js/types`, extract repeated markup into components.
- Design: warm light/dark system, glass only on floating chrome, serif for quotes, Lucide icons, CSS motion with reduced-motion support (see DESIGN.md).
- No hard-coded user-facing strings: PHP uses `__('key')`, React uses `t('key')`, both from `codes/lang/en.json`.

## Tech Stack

Latest stable of every part of the stack (checked 2026-11-19). Keep it that way: when adding or touching a dependency, use the newest stable release and bump the rest on the same pass.
- PHP 8.5, Laravel 13, Inertia 3 (Laravel adapter and React), Laravel Cashier 16 (Stripe), PHPUnit 13, Pint, Larastan 3.
- Node 26, React 19.3, Vite 8, Tailwind 4.3, ESLint 10, Lucide 1.x, Recharts 3, Radix UI.
- PostgreSQL 18, nginx 1.31, Mailpit 1.34, Composer 2.
- Held back, with the reason: TypeScript stays on 6.0.x because typescript-eslint (latest 8.73) does not yet support TypeScript 7; `eslint-plugin-react` was dropped because it does not support ESLint 10 (React Hooks rules are kept). Revisit both when upstream catches up.

## Decided

- DECIDED: Laravel + Inertia React, own Postgres in compose, Stripe test mode, AI-DLC installed from the official installer (2026-11-19).
- DECIDED: logs are JSON on stderr in the Shell Console "5W" shape (who / what / where / when / why) with request id and device info (2026-11-19).
- DECIDED: translations live in `codes/lang/en.json` (flat dotted keys) for both Laravel and React; English only for now (2026-11-19).

## Scope Overrides

<!-- Custom scope rules for this project. -->

## Forbidden

- NEVER add `Co-Authored-By` or any Claude attribution to commits or PRs (stated 2026-11-19).
- NEVER edit `docker/.envs/app.env` or `codes/.env` from the agent; edit the `.example` files and say what to set (stated 2026-11-19).
- NEVER add new Larastan baseline entries, use `any` in TypeScript, or leave a hard-coded user-facing string (stated 2026-11-19).
- NEVER log secrets, tokens, passwords, card data, request bodies or query values; log only query keys (stated 2026-11-19).
- NEVER expose a respondent's email outside the owner's inbox (stated 2026-11-19).

## Mandated

- ALWAYS log through the JSON 5W channel (`LOG_CHANNEL=stderr_json`) and echo `X-Request-ID` on every response and error page (stated 2026-11-19).
- ALWAYS wrap outbound calls that can fail transiently in the Retrier (exponential backoff with jitter, configured by `RETRY_*` in the env file) and turn exhausted retries into a user-readable 503, not a 500 (stated 2026-11-19).
- ALWAYS answer failures with the friendly error page (HTML) or the structured JSON error (APIs), including the request id; expected dependency outages are 503 with `Retry-After` (stated 2026-11-19).
- ALWAYS give every service CPU, memory, swap and pids limits in compose (stated 2026-11-19).
- ALWAYS use the latest stable version of each stack component and upgrade the others with it (stated 2026-11-19).

## Corrections

- ALWAYS check `docker compose` containers are rebuilt (not only recreated) after changing the entrypoint or Dockerfile (learned 2026-11-19).
- NEVER rely on `flock` across containers on a bind mount: only one container writes the shared `.env`, atomically (learned 2026-11-19).
- ALWAYS read a file before rewriting it with `open(p, 'w')` in the same expression: it truncates first (learned 2026-11-19).
