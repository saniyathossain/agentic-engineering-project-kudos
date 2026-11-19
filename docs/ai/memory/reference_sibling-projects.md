---
name: reference-sibling-projects
description: Where the owner's other projects live and what each is the reference for (docker layout, logging, outage page, design, AIDLC)
metadata:
  type: reference
---

Owner asks to "follow other projects" - these are the templates (all under `/Users/bs01616/app/docker/www` unless noted):
- Docker `codes/` + `docker/` layout, `.envs/app.env`, external `common-net` with `common-postgres`/`common-redis`: `/Users/bs01616/app/host/www/bs23/edotco-poc-ms`.
- Hardened prod compose (read_only, cap_drop, limits, loopback ports, edge nginx, `make dev|prod`): `bs23/lnd-python-v1/docker` and `joint/shellconsole/docker`.
- Laravel prod/stage compose and Monolog JSON stderr formatter option, `ErrorContext`, request-id + `X-Client-*` device headers: `bs23/client-focus/focus-plan/focus-university-admission-backend` (frontend logger in `...-frontend/codes/src/lib/logging`, batched POST to `/api/client-log`).
- 5W JSON logging (`internal/support/obs/fivew.go`, `docs/logging.md`), retry/backoff env vars (`DEPLOYER_HTTP_CLIENT_RETRY_*`), edge outage page + `/readyz` polling with backoff: `joint/shellconsole`.
- Design systems: `bs23/lnd-python-v1/DESIGN.md` (opaque cards, one accent, rules) and `joint/shellconsole/codes/frontend/src/styles/*.css` (liquid glass, animated icons).
- AI-DLC example outputs: `/Users/bs01616/app/host/www/bs23/cursor-demo/aidlc-docs`, and legacy rules in `/Users/bs01616/Downloads/Archive (1)/focus-university-admission-backend/.aidlc-rules`.
Verify paths still exist before relying on them. See [[kudos-capstone]].
