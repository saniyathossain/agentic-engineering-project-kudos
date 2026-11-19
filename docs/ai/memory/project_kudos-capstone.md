---
name: kudos-capstone
description: What the Kudos repo is (course capstone), its stack, layout, status and the decisions already made
metadata:
  type: project
---

Kudos is a minimal Testimonial.to clone built for the Agentic Engineering course (Module 13 assignment). Repo: `/Users/bs01616/app/host/www/bs23/lnd-course-agentic-engineering-project`, local git only (no GitHub remote yet; `gh` is not installed). Requirements: `docs/prd.md`, data model `docs/data-model.md`, design `PRODUCT.md` + `DESIGN.md`, rules `CLAUDE.md` and `aidlc/spaces/default/memory/project.md`.

Stack (all latest stable as of 2026-11-19): PHP 8.5, Laravel 13, Inertia 3 + React 19, Postgres 18, nginx edge, Node 26, Vite 8, Tailwind 4, Stripe via Cashier (test mode, no keys supplied yet). TypeScript is held at 6.0.x and `eslint-plugin-react` is dropped because upstream (typescript-eslint, eslint-plugin-react) lacks TS 7 / ESLint 10 support.

Layout follows the owner's other projects: `codes/` = Laravel app, `docker/` = Dockerfile (dev | prod | edge), `docker-compose.yml`, `docker-compose.prod.yml`, `.envs/*.env(.example)`. Dev app http://localhost:8010 (demo@kudos.test / password), Mailpit :8030, Vite :5180. `make dev|prod|test|lint|types|migrate`.

**Why:** the owner must submit a repo + README + screenshots + a 200-300 word reflection; the README reflection is a draft they will edit. Live Stripe checkout is unverified (needs `STRIPE_*` keys). The AI-DLC `/aidlc` workflow is installed but the build ran as plan, implement, verify directly.

**How to apply:** before suggesting changes read CLAUDE.md; run everything through Docker; never edit `docker/.envs/app.env` or `codes/.env` (a hook blocks it) - edit the `.example` and say what to set. Related: [[no-coauthored-by-trailer]], [[feedback-latest-stable-versions]], [[feedback-coding-standards]], [[feedback-observability-resilience-i18n]], [[feedback-design-preferences]], [[reference-sibling-projects]].
