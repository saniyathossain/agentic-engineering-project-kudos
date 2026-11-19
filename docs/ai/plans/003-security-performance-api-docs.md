# Plan 003 - security hardening, performance, API documentation

Requested 2026-11-19.

## Goals
1. Keep plans, AI-related docs and skills in the repository.
2. Proper Docker ignore and image optimisation; compose security; no known vulnerabilities.
3. Responsive light/dark checks and a Google PageSpeed (Lighthouse) check.
4. API documentation with every success and error case: OpenAPI plus Postman, Insomnia and Bruno collections, environment variables.
5. No underline on hyperlinks.

## Steps
| # | Step | Where |
|---|---|---|
| 1 | Fix the critic's findings (idempotent Stripe calls with timeouts, log scrubbing, 429 loop, mapper, edge env, `/client-logs` limits, reserved-slug migration, enums and DTOs) | `codes/app/**`, `docker/nginx/**` |
| 2 | Docker: root-owned read-only code, no composer/git in the prod image, BuildKit caches, unprivileged nginx, segmented networks (data network is internal), Docker secret for the database password, read-only containers with no capabilities, resource limits, pinned images | `docker/Dockerfile`, `docker/docker-compose.prod.yml`, `docker/Dockerfile.dockerignore` |
| 3 | Security headers and CSP (nonce for the Ziggy and Vite scripts) | `codes/app/Http/Middleware/SecurityHeaders.php` |
| 4 | Vulnerability scans: `composer audit`, `npm audit`, Trivy for config, secrets and images | `scripts/audit.sh`, `make audit`, `docs/security.md` |
| 5 | Lighthouse on the production stack (desktop and mobile, light and dark), fix what it finds | `docs/performance/` |
| 6 | Responsive checks at phone, tablet and desktop widths in both themes | `docs/performance/responsive.md` |
| 7 | OpenAPI + collections generated from one source, verified with newman | `docs/api/` (built by a delegated agent), `docs/configuration.md` |
| 8 | Links without underlines | `app.css`, `status.css`, `DESIGN.md` |
| 9 | AI docs in the repo | `docs/ai/` |
