# Plan — "Kudos" Testimonial Collection SaaS (Module 13 capstone)

## Context
Course Module 13 rebuilds a minimal **Testimonial.to** clone in Laravel (videos 13-01 reference walkthrough, 13-03 PRD via ChatGPT, 13-08 Conductor parallel workspace; 04-05 plan→implement→verify with fresh critic reviewer). Assignment: build same app with Claude Code, show agentic workflow (planning, context, verification, gap fixing), parallel session, README + reflection + screenshots.

User choices: **Laravel + Inertia React**, **own Postgres in compose**, **Stripe test mode**, **AIDLC rules fresh from awslabs/aidlc-workflows**. Docker layout follows `edotco-poc-ms` template: `codes/` (app source) + `docker/` (Dockerfile, docker-compose.yml, `.envs/app.env`), compose built with `context: ../`, `dockerfile: docker/Dockerfile`, `../codes` bind mount.

Working dir `/Users/bs01616/app/host/www/bs23/lnd-course-agentic-engineering-project` is empty, not a git repo. No `gh` CLI — user creates GitHub repo (or `brew install gh`) before push.

## Scope (from 13-03 PRD, trimmed to minimal v1)
Roles: **Owner** (registered) and **Respondent** (public, no auth).

1. Auth — register/login/logout, password reset, email verify (Laravel React starter kit / Fortify; Mailpit catches mail).
2. Spaces CRUD — name → unique slug (public URL preview), logo upload, header title, custom message (markdown), collect star rating toggle, theme (3 predefined: light, dark, brand), field config: name+email always required; optional predefined fields `company`, `title`, `social_link`, `photo` each with enabled/required toggles. Live preview pane on form.
3. Public collection page `/{slug}` — themed, questions, text testimonial modal (rating, text, fields per config, photo, consent checkbox required), thank-you state. Rate limited, no auth.
4. Inbox per space — list, filter (all/favorite/published/hidden), edit text, favorite, hide, publish, delete.
5. Embed widget — "wall of love": public JSON + iframe page `/embed/{public_id}` showing published testimonials only, no emails exposed; copyable embed snippet.
6. Dashboard — stats (spaces, testimonials, unique respondents, plan usage), testimonials-per-day graph (7/30/90 days, Recharts), dismissible free-plan upgrade banner.
7. Billing — Cashier + Stripe Checkout (test mode), Free vs Pro, success page verifies server-side, webhooks (`/stripe/webhook`, signature verified), billing portal button, limits: Free = 1 space / 10 testimonials per space; over-limit space stops accepting.

Out of scope (README "not done"): video/audio, custom fields beyond predefined, teams, custom domains, localization, AI editing, annual plans.

## Data model (→ `docs/data-model.md`, Mermaid ERD)
- `users` (Cashier columns: stripe_id, pm_type, pm_last_four, trial_ends_at) + `banner_dismissed_at`
- `spaces`: id, public_id (ULID), user_id FK, name, slug unique, logo_path, header_title, message, collect_rating bool, theme enum, fields jsonb (`{company:{enabled,required},...}`), is_accepting bool, timestamps
- `testimonials`: id, public_id (ULID), space_id FK cascade, rating nullable 1–5, body text, respondent_name, respondent_email, company, title, social_link, photo_path, consent bool, status enum(pending, published, hidden), is_favorite, submitted_at, timestamps; index (space_id, submitted_at)
- `subscriptions`, `subscription_items` — Cashier standard
- Relations: User 1–N Space 1–N Testimonial; User 1–N Subscription. Policies: owner-only on Space/Testimonial.

## Repo layout
```
lnd-course-agentic-engineering-project/
├── codes/                     # Laravel app (laravel new --react, Pest)
├── docker/
│   ├── Dockerfile             # php:8.4-cli-alpine + pdo_pgsql, gd, intl, composer, node for build
│   ├── docker-compose.yml     # app, vite, queue, postgres, mailpit, stripe-cli (profile)
│   └── .envs/app.env(.example)
├── .aidlc-rules/aws-aidlc-rules/core-workflow.md   # from awslabs/aidlc-workflows
├── .aidlc-rule-details/{common,inception,construction,operations,extensions}
├── aidlc-docs/                # aidlc-state.md, audit.md, inception/*, construction/<unit>/*
├── .claude/
│   ├── settings.json          # hooks + permissions
│   ├── agents/critic.md       # fresh reviewer subagent (diff vs plan, runs pest/pint/larastan)
│   └── skills/verify-feature/SKILL.md  # pest + pint + larastan + playwright smoke checklist
├── .mcp.json                  # Playwright MCP (+ laravel boost MCP inside container optional)
├── docs/data-model.md, docs/prd.md, docs/screenshots/
├── CLAUDE.md                  # router style like focus backend: commands, rules, load-on-demand aidlc
└── README.md
```

## Docker compose (own stack, self-contained)
Services: `app` (`php artisan serve --host 0.0.0.0 --port 8000`, port `${APP_PORT:-8010}`), `vite` (node:22-alpine, `npm run dev`, 5173), `queue` (`php artisan queue:work`), `db` (postgres:17, volume, healthcheck), `mailpit` (8025), `stripe` (stripe/stripe-cli `listen --forward-to app:8000/stripe/webhook`, `profiles: [billing]`). Volumes `../codes:/app`, anonymous `/app/vendor`, `/app/node_modules`. Entry script runs `composer install`, `key:generate` if missing, `migrate --seed`. Ports bound to 127.0.0.1, avoid clash with existing 8000/5173/5432/8025.

## Execution steps (AIDLC phases, each feature = plan → implement → verify)
**Inception**
1. `git init`, fetch awslabs/aidlc-workflows rules into `.aidlc-rules` + `.aidlc-rule-details`; create `aidlc-docs/aidlc-state.md`, `audit.md`.
2. `aidlc-docs/inception/requirements.md` + `user-stories.md` + `docs/prd.md` from scope above; `workflow-planning.md` with units: U1 setup, U2 spaces, U3 public collection, U4 inbox, U5 dashboard, U6 billing, U7 embed.
3. `docs/data-model.md` ERD (application-design stage).

**Construction**
4. U1 setup: scaffold Laravel React starter kit in `codes/`, docker files, compose up, Pest green; CLAUDE.md, `.claude/` hooks (PostToolUse: `pint --dirty` on PHP edits; PreToolUse: block edits to `.env`/`docker/.envs/app.env`), critic agent, verify-feature skill, `.mcp.json` Playwright. Commit.
5. U2 Spaces → U3 Public page → U4 Inbox → U5 Dashboard → U6 Billing, sequential on `main` via feature branches. Each: write `aidlc-docs/construction/<unit>/plan.md`, implement with Pest feature tests, run verify-feature skill, spawn **critic** subagent, Playwright MCP UI check + screenshot to `docs/screenshots/`, commit.
6. **Parallel**: U7 Embed widget in separate git worktree (`feature/embed-widget`, own Claude session) while U5/U6 run on main; merge with `--no-ff`, resolve conflicts, rerun tests. Logged in `audit.md`.

**Operations / check**
7. Full requirement sweep vs `requirements.md` with Playwright end-to-end (register → space → submit → publish → embed → upgrade with Stripe test card `4242…`) — note gaps, fix or list as not done.
8. README: run instructions, feature done/not-done table, agentic tools & where used, screenshots, reflection 200–300 words (draft; user edits). Push to GitHub repo user creates.

## Agentic tools coverage
- Subagent: `critic` reviewer per unit (04-05 pattern) + Explore for research
- Skill: `verify-feature`
- Hook: pint-on-edit, protect env files
- MCP: Playwright for UI verification/screenshots
- Parallel: git worktree + separate session (Conductor alternative)
- AIDLC: state/audit/inception/construction docs

## Verification
- `docker compose -f docker/docker-compose.yml up -d --build`; `docker compose exec app php artisan test`; `vendor/bin/pint --test`; `vendor/bin/phpstan` (larastan).
- Playwright MCP flow at `http://localhost:8010`; Mailpit for verify email; `--profile billing` + Stripe test keys for checkout + webhook (`subscriptions` row created, billing page shows Pro).
- `docker compose exec db psql` spot-check data; embed page shows only published, no emails.

## User-supplied inputs needed during build
- Stripe test keys (`STRIPE_KEY`, `STRIPE_SECRET`, price id) in `docker/.envs/app.env` — Claude will not enter them.
- GitHub repo URL (or install `gh` and authenticate).
- Screen recording + final reflection edit.
