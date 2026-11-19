---
name: feedback-observability-resilience-i18n
description: Required logging format, error/outage handling, retry/backoff config and translation file conventions for apps built here
metadata:
  type: feedback
---

Logs: JSON on stderr, one object per line, grouped who / what / where / when / why (Shell Console style) plus `request_id`, `trace_id` and caller device info; configured from the env file. Errors: never a bare 500 - friendly page or structured JSON carrying the request id, expected dependency failures are 503 + `Retry-After`, an edge-served outage page polls `/readyz` with exponential backoff. Retries: exponential backoff with jitter configurable from the env file (`RETRY_ATTEMPTS`, `RETRY_BASE_DELAY_MS`, `RETRY_MAX_DELAY_MS`, `RETRY_FACTOR`, `RETRY_JITTER`, `RETRY_BUDGET_MS`). Translations: one flat dotted-key JSON file (`codes/lang/en.json`) read by Laravel `__()` and by React `t()`; English only for now but no hard-coded user-facing text.

**Why:** requested on 2026-11-19 after pointing at the focus backend/frontend and Shell Console projects as the references ("check ... application log format ... outage page ... no 500 error ... retry with exponential backoff app.env configurable ... lang in json files").

**How to apply:** reuse `app/Logging/FiveWFormatter`, `CaptureRequestContext`, `Retrier` + `RetryPolicy`, `ErrorResponder`/`ExceptionMapper`, `public/status/*` and `lib/i18n.ts` instead of inventing new ones. Add new env knobs to `docker/.envs/app.env.example` (and the prod example). Known limit: unexpected bugs still return 500 (friendly page, logged critical); validation/mail strings come from Laravel's own lang files. See [[kudos-capstone]], [[reference-sibling-projects]].
