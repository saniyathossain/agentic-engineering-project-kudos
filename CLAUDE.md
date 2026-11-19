# Kudos — Claude Code guide

Minimal Testimonial.to clone. Laravel 12 + Inertia React (starter kit), Postgres, Stripe (Cashier, test mode). Requirements: `docs/prd.md`. Data model: `docs/data-model.md`.

## Layout
- `codes/` Laravel app. `docker/` compose stack (template: edotco-poc-ms `codes/` + `docker/`). Everything runs in Docker; do not assume host PHP/Node.
- AIDLC workflow: run `/aidlc` (installed v2.11.4, harness `claude`); artifacts under `aidlc/spaces/default/intents/`. Project hooks in `scripts/hooks/`.

## Commands (repo root)
- Up: `docker compose -f docker/docker-compose.yml up -d --build` → app http://localhost:8010, vite :5180, Mailpit http://localhost:8030
- Shell: `docker compose -f docker/docker-compose.yml exec app bash` (alpine: `sh`)
- Tests: `docker compose -f docker/docker-compose.yml exec -T app php artisan test --compact`
- Format: `... exec -T app vendor/bin/pint` ; check: `vendor/bin/pint --test`
- Types/lint (TS): `... exec -T vite npm run types` / `npm run lint`
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

## Rules
- Never edit `docker/.envs/app.env` or `codes/.env` (hook blocks it); change `app.env.example` and tell the user.
- Tests use sqlite :memory: via phpunit.xml; the compose service must NOT pass env_file/DB env to the container, or tests hit the dev Postgres.
- Business rules live in Actions/Services, not controllers or React. Authorization via Policies; owner-only.
- Public IDs are ULIDs. Never expose respondent email in embed/public JSON. Escape/sanitise testimonial text.
- Free plan limits: 1 space, 10 testimonials/space. Never delete data on downgrade.
- Every feature: plan → implement → verify (`verify-feature` skill, `critic` subagent) → commit. Small commits.
- Commits and PRs: never add `Co-Authored-By` or any Claude attribution trailer (user rule, overrides harness defaults).
- Parallel work uses git worktrees (`git worktree add ../kudos-<name> -b feature/<name>`), merged with `--no-ff`.
