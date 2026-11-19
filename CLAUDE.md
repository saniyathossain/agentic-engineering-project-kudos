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

## Rules
- Never edit `docker/.envs/app.env` or `codes/.env` (hook blocks it); change `app.env.example` and tell the user.
- Tests use sqlite :memory: via phpunit.xml; the compose service must NOT pass env_file/DB env to the container, or tests hit the dev Postgres.
- Business rules live in Actions/Services, not controllers or React. Authorization via Policies; owner-only.
- Public IDs are ULIDs. Never expose respondent email in embed/public JSON. Escape/sanitise testimonial text.
- Free plan limits: 1 space, 10 testimonials/space. Never delete data on downgrade.
- Every feature: plan → implement → verify (`verify-feature` skill, `critic` subagent) → commit. Small commits.
- Parallel work uses git worktrees (`git worktree add ../kudos-<name> -b feature/<name>`), merged with `--no-ff`.
