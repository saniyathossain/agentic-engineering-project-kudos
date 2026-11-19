---
name: verify-feature
description: Run the Kudos verification loop for a finished feature - tests, Pint, static analysis, on-plan diff check, Playwright UI smoke, critic subagent. Use before committing any unit.
---
# verify-feature

Run in order; stop and fix on first failure.

1. `docker compose -f docker/docker-compose.yml exec -T app php artisan test --compact` — all green, including tests the plan specified.
2. `docker compose -f docker/docker-compose.yml exec -T app vendor/bin/pint --test` — clean.
3. `docker compose -f docker/docker-compose.yml exec -T app vendor/bin/phpstan analyse --memory-limit=1G` — zero errors (skip only if phpstan not yet installed; note it).
4. `npm run types` / `npm run lint` in `codes/` via the `vite` container if TypeScript changed.
5. i18n and logging: no hard-coded user-facing text (grep JSX text/aria/placeholder), new strings added to `codes/lang/en.json`, new failure paths return a friendly page/JSON with the request id and are logged through the JSON channel.
5b. On-plan: every file in `git diff --stat HEAD` appears in the unit plan.
6. UI smoke with Playwright MCP against `http://localhost:8010`: walk the feature's happy path, save a screenshot into `docs/screenshots/<unit>-<step>.png`.
7. Spawn the `critic` subagent with the plan path. Merge/commit only on `Approved`.
8. Append a line to the AIDLC audit trail describing what was verified.
