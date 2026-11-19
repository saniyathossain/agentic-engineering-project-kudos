# Security

How Kudos is protected, how it is checked, and what is knowingly accepted. Run the checks with `make audit`.

## Controls

### Containers and compose (`docker/Dockerfile`, `docker/docker-compose.prod.yml`)
| Control | Detail |
|---|---|
| Minimal images | Multi-stage build; the production image has php-fpm and its extensions only: no composer, git, node or build toolchain. `docker/Dockerfile.dockerignore` keeps `.git`, `.env` files, secrets, docs, tests and dev tooling out of the build context |
| Non-root | App as `www-data` (82), edge as `nginx` (101, the unprivileged nginx image), database as `postgres` |
| Read-only | `read_only: true` on every production service; code is root-owned and read-only to the app user; writable paths are the `storage` volume and tmpfs mounts (`noexec,nosuid,nodev`) |
| No privileges | `cap_drop: [ALL]` and `no-new-privileges` on every service, none adds a capability back; `init: true` reaps zombies |
| Database without gosu | A derived image removes the stock image's `gosu` binary (built with an old Go toolchain, many CVEs) and starts as `postgres` directly |
| Networks | `edge` (nginx and app), `egress` (outbound calls such as Stripe), `data` (`internal: true`): the database has no route to the outside and only the app containers can reach it |
| Ports | Only the edge publishes a port, on loopback (`127.0.0.1`); put a TLS proxy or load balancer in front. Postgres is never published in production |
| Secrets | The database password is a Docker secret file (`docker/.envs/secrets/db_password`, git-ignored). Any `NAME_FILE=/path` variable is read into `NAME` at start (`entrypoint.prod.sh`), so Stripe keys can use secrets too. `app.prod.env` is git-ignored and is not given to the edge or the database |
| Limits | CPU, memory, swap and pids limits on every service; log rotation |
| Pinned and patched | Image versions are pinned to a minor tag; `apk upgrade` runs in each stage so OS fixes land on rebuild |
| Healthchecks | In the Dockerfile and in compose for every long-running service |

### Application
- **Content-Security-Policy** with a per-request nonce for the scripts Vite and Ziggy print, no `unsafe-eval`, `object-src 'none'`, `frame-ancestors 'self'` (only the embed pages allow `*`), `form-action 'self'`, `base-uri 'self'`. On in production (`CSP_ENABLED`), switchable to report-only (`CSP_REPORT_ONLY`). Plus `Permissions-Policy`, `Cross-Origin-Opener-Policy`, HSTS over HTTPS; nginx adds `nosniff`, referrer policy and `X-Frame-Options`.
- **Authentication**: Laravel session auth with email verification required for the app area; rate limits on login and registration at the edge and in the framework; passwords hashed.
- **Authorization**: owner-only policies on spaces and testimonials; respondents never see other respondents' data; a respondent's email never leaves the owner's inbox (not in embeds, JSON feeds or logs).
- **Input**: server-side validation on every request; text stripped of HTML and rendered escaped; uploads limited by type and size; slugs cannot collide with application routes.
- **CSRF**: on for every state-changing route. The one exception, `POST /client-logs` (a beacon cannot carry a token), only accepts same-origin browser requests (`Sec-Fetch-Site` / `Origin`), is rate limited at the edge and in the app, and caps the body at 16 KB.
- **Stripe**: checkout success is confirmed with Stripe, never trusted from the redirect; webhooks verify the signature; every create call carries an idempotency key; calls time out fast and retry with backoff.
- **Logging**: JSON lines with a scrubber for secrets and personal data in free text and paths (emails, hashes, keys, tokens, query strings, reset links) and key-based redaction; SQL bindings are never logged.
- **Errors**: friendly pages and structured JSON never expose stack traces or exception messages (outside `APP_DEBUG`).

## Checks (`make audit`, `scripts/audit.sh`)
1. `composer audit --locked` - PHP dependency advisories.
2. `npm audit` - JavaScript dependency advisories.
3. Trivy `config` - Dockerfile misconfiguration.
4. Trivy `fs --scanners secret` - secrets committed to the repository.
5. Trivy `image` - fixable HIGH and CRITICAL vulnerabilities in `kudos-app:prod`, `kudos-edge:prod`, `kudos-db:prod`.

Latest run (2026-11-19, after the fixes below): composer 0 advisories, npm 0 vulnerabilities, no secrets, Dockerfile clean, images clean for fixable HIGH/CRITICAL (see the table).

### Findings fixed along the way
| Finding | Fix |
|---|---|
| Edge image: 13 fixable HIGH/CRITICAL OS-library CVEs (brotli, curl, expat, ...) | `apk upgrade` in the edge stage |
| Database image: 27 CVEs in the bundled `gosu` binary | Derived `db` image removes `gosu` and runs as `postgres` |
| Dockerfile had no HEALTHCHECK (DS-0026) | Added to the prod, edge and db targets |
| Reset-password and verification tokens could reach the logs via the request path, `Referer` and `page_url` | Query strings dropped, long token-like path segments masked |
| Emails and password hashes could reach the logs inside SQL exception messages | Exceptions log the driver message only, and all free text is scrubbed |
| Stripe checkout could be created twice by a retry | Idempotency keys, explicit timeouts, SDK retries off |
| `POST /client-logs` was open to scripts | Browser-only, size and rate limits |

## Knowingly accepted
- `style-src 'unsafe-inline'`: React sets inline style attributes (charts, positioning). Scripts stay nonce-only.
- Fonts (Instrument Sans, Fraunces) are self-hosted and bundled by Vite: no third-party font origin, nothing extra in the CSP.
- Traffic between the app and Postgres on the internal `data` network is not encrypted; the network has no external route.
- TLS is terminated in front of the stack (load balancer or proxy); HSTS is sent when the request arrives over HTTPS. Set `TRUSTED_PROXIES` so the app sees the real scheme and client IP.
- No WAF or bot protection; the edge rate limits login, registration, client logs and public submissions.
