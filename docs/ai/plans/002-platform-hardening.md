# Plan 002 - latest stack, logging, resilience, translations

Requested 2026-11-19. Written before the work, updated with what happened.

## Goals
1. Every part of the stack on its latest stable release (Laravel 13 was current; the project had started on 12).
2. JSON logs on stderr in the Shell Console "5W" shape with request id and device info, configured from the env file (references: focus backend and frontend, Shell Console).
3. No bare 500s; an outage page like Shell Console's; retries with exponential backoff configurable from the env file.
4. All user-facing text in JSON language files (English only for now).

## Steps and outcome
| # | Step | Outcome |
|---|---|---|
| 1 | Study the reference projects (log shape, request id, device headers, outage page, retry env vars) | Done by a read-only research agent; findings drove the design below |
| 2 | Look up latest versions (packagist, npm registry, Docker Hub) and upgrade | PHP 8.5, Laravel 13.43, Inertia 3, PHPUnit 13, Node 26, Vite 8, Postgres 18, nginx 1.31. Held back: TypeScript 6.0.x (typescript-eslint has no TS 7 support), `eslint-plugin-react` dropped (no ESLint 10 support) |
| 3 | Logging: `stderr_json` channel, `FiveWFormatter`, `CaptureRequestContext` (request id, trace id, device), access log, redaction, browser logger and `POST /client-logs` | Done; 5W groups, request id echoed on every response |
| 4 | Errors: `ExceptionMapper` + `ErrorResponder`, Blade status page, React error page, `/livez` `/readyz`, edge-served `outage.html` with backoff polling | Done; verified by stopping the app container behind the edge |
| 5 | Retries: `RetryPolicy` + `Retrier` (full/equal/no jitter, attempt and time budget), `ResilientBillingGateway` | Done; env knobs `RETRY_*` |
| 6 | Translations: `codes/lang/en.json` shared by `__()` and the React `t()` (type-checked keys); three agents moved ~300 strings in parallel | Done; 357 keys |
| 7 | Independent `critic` review | Changes requested: Stripe retries without idempotency, secrets in logged paths and SQL errors, a 429 reload loop, a dead mapper branch, edge env handling, open `/client-logs`. All fixed (see Plan 003) |

## Decisions
- Single source of truth for words: the flat dotted-key JSON file; the outage page's subset is exported to `public/status/lang.json` so the edge can serve it with the app down.
- Only the `app` container writes `codes/.env` (atomic); `flock` is not reliable across containers on a bind mount.
- A friendly 500 page remains for unexpected bugs (logged at error level); expected dependency failures are 503 with `Retry-After`.
