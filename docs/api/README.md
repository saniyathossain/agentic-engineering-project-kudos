# Kudos API documentation

Everything in this folder is generated from three data files by one script. Edit the data, run the script, commit the output.

| File | What it is |
| --- | --- |
| `openapi.yaml`, `openapi.json` | OpenAPI 3.1 description of every route: auth, parameters, request bodies with validation limits, every response the code can produce, error shapes, headers, rate limits |
| `postman/kudos.postman_collection.json` (v2.1) + `kudos.local.postman_environment.json`, `kudos.prod-style.postman_environment.json` | Postman collection and environments |
| `insomnia/kudos.insomnia.json` | Insomnia v4 export with the collection and two sub-environments |
| `bruno/` | Bruno collection (`bruno.json`, `environments/*.bru`, one folder per area) |
| `scripts/foreign-space.sh` | Helper that creates a second verified owner with a space, for the 403 cases |
| `endpoints.py`, `cases.py`, `envvars.py` | The data: OpenAPI source, client cases, configuration reference |
| `build.py` (+ `gen_*.py`, `scan_env.py`) | The generator. Python 3 standard library only |
| `redocly.yaml` | Lint config for `redocly lint` |
| `../configuration.md` | Every environment variable and every collection variable (generated here too) |

## Regenerate

```bash
python3 docs/api/build.py
```

This rewrites `openapi.*`, `postman/`, `insomnia/`, `bruno/`, this README and `docs/configuration.md`. It also prints a warning for every environment variable the PHP config reads that `envvars.py` does not describe, so the configuration reference cannot silently go stale. Do not edit generated files by hand; the next run overwrites them.

## Before you run a collection

1. Start the dev stack: `docker compose -f docker/docker-compose.yml up -d` (app on http://localhost:8010). The prod-style stack (nginx edge) works too: start it with `APP_PORT=8011` and pick the `prod-style` environment.
2. The collections sign in as `demo@kudos.test` / `password`, the owner `DatabaseSeeder` creates. This is local seed data, not a secret. Put another verified owner into the `email` and `password` variables to use a different account.
3. The run is **idempotent**: it creates one space named `API Probe <runId>`, one testimonial, then deletes both and signs out. The Free plan allows one space, so if the owner already has a space the create request is refused with a redirect to `/billing` (that is asserted), and every request that needs the new space skips itself. Nothing is created or deleted in that case; the space-dependent cases then do not run. Use an owner without a space for the full sequence.
4. Run the folders in order, in one run. They share one session and one set of variables (`00 Setup` fetches the cookies and the Inertia asset version; `03 Auth` signs in once; `13 Cleanup` deletes and signs out).
5. **Rate limits.** `POST /{slug}` (20 per minute) and `POST /client-logs` (60 per minute) share one counter per signed-in user, together with the verification-mail routes (6 per minute). A full run sends about 15 throttled requests, so wait 60 seconds before starting the next run or the submission cases answer 429. `POST /login` locks an email and IP pair after 5 failures; the run makes 1 to 3 failed attempts and then succeeds, which clears the counter.
6. Folder `99 Optional (side effects, throttling)` is skipped unless `runOptional=true`. It contains the 403 cross-owner cases (need `foreignSpaceId`, see below), the permanent banner dismissal, a loop that drives `/client-logs` into 429, the shared-bucket 429 on `POST /{slug}` and the 422 login lockout message. Run it last and expect to wait a minute afterwards.
7. **Foreign space for the 403 cases.** Run `docs/api/scripts/foreign-space.sh up` (dev stack only; it uses `artisan tinker`). It prints `foreignSpaceId` and `foreignTestimonialId`; set both variables and `runOptional=true`. Remove the second owner with `docs/api/scripts/foreign-space.sh down`.

## Postman

Import `postman/kudos.postman_collection.json` and `postman/kudos.local.postman_environment.json` (File, Import), select the environment, then Run collection (keep the order, leave 'Persist responses' off, do not enable 'Follow redirects' overrides: each request pins `followRedirects: false`). Saved example responses are attached to the requests.

Command line (newman):

```bash
npx --yes newman run docs/api/postman/kudos.postman_collection.json \
  -e docs/api/postman/kudos.local.postman_environment.json
# a Dockerised run, reaching the host's published port:
docker run --rm -v "$PWD/docs/api:/api" -w /api node:26-alpine npx --yes newman run postman/kudos.postman_collection.json \
  -e postman/kudos.local.postman_environment.json --env-var baseUrl=http://host.docker.internal:8010
# the optional folder:
newman run ... --env-var runOptional=true --env-var foreignSpaceId=<id> --env-var foreignTestimonialId=<id>
```

## Bruno

Open the folder `docs/api/bruno` in Bruno (Open Collection), choose the `local` or `prod-style` environment, run the collection. Command line:

```bash
cd docs/api/bruno && npx --yes @usebruno/cli run --env local
# Dockerised:
docker run --rm -v "$PWD/docs/api/bruno:/bruno" -w /bruno node:26-alpine npx --yes @usebruno/cli run --env local --env-var baseUrl=http://host.docker.internal:8010
```

Override any variable with `--env-var name=value` (for example `email`, `password`, `runOptional`). Scripts use `bru.runner.skipRequest()` and `bru.runner.setNextRequest()`, so use a current Bruno (the CLI above is 4.x).

## Insomnia

Import `insomnia/kudos.insomnia.json` (Application, Import), pick the sub-environment `Kudos local` or `Kudos prod-style`, then run the folders in order with the Collection Runner. Requests carry pre-request and after-response scripts (Insomnia 11 or newer) for the CSRF refresh, variable capture and assertions. Two limits of Insomnia's script engine shape this export: a script cannot skip a request, so the optional folder `99` and the loop-until-429 requests are left out, and requests that depend on the new space cannot skip themselves, so use an owner without a space (or accept failures for the space-dependent requests when one exists).

Command line: `inso run collection` needs the `inso` binary from the Insomnia releases page (`https://github.com/Kong/insomnia/releases`); the npm package `insomnia-inso` stops at 3.6.0, predates request scripts and does not run on current Node. The binary was not downloaded or run when this was written (see Verified).

## Verified

Last verified 2026-11-19 against the dev stack (`http://localhost:8010`):

* OpenAPI: Redocly CLI lint: valid, 0 errors, 0 warnings with docs/api/redocly.yaml (without it: 0 errors and warnings only for redirect-only operations, probes without a 4xx, and localhost servers).
* Postman: newman 6.2.3, clean path (owner without a space): 120 requests, 442 assertions, 0 failed; with `runOptional=true` and the foreign-space ids: 193 requests (loops included), 466 assertions, 0 failed; demo owner who already had a space (skip path): 79 requests, 275 assertions, 0 failed.
* Bruno: Bruno CLI 4.3.0, clean path: 442 of 442 tests passed (120 requests run, the 8 optional ones skipped).
* Insomnia: JSON structure and script syntax checked; not imported into the Insomnia app and not run with `inso` (no binary). Treat it as best effort.
* Edge-only behaviour (the nginx outage JSON with `source: edge`, `limit_req` zones) and the Stripe paths that need real keys (Checkout redirect, portal, webhook signature failure) are documented from the code and templates but were not exercised.

## How requests are written

* **JSON mode** (`Accept: application/json`): validation errors come back as 422 `{message, errors}`, unauthenticated as 401, other failures as `{error, code, dependency, request_id}`. Used for every error case.
* **Inertia mode** (`X-Inertia: true`, `X-Inertia-Version: {{inertiaVersion}}`): page routes return `{component, props, url, version}`; used to read props, flash messages and counts.
* **HTML mode** (`Accept: text/html`): documents, redirects to `/login`, the HTML error pages.
* Every request sends `X-Request-ID: {{requestId}}` (new per request) and asserts the response echoes it. Every unsafe request sends `X-XSRF-TOKEN: {{xsrfToken}}`, refreshed from the `XSRF-TOKEN` cookie after each response. Redirects are never followed, so `302` and `Location` can be asserted.
* Redirect-back responses (`back()`) depend on the `Referer`; the requests set it explicitly, otherwise the app redirects to the last page the session visited.
* Flash messages and validation errors of a redirect appear only in the next Inertia page object, so the requests that read them come right after the request that sets them.

## Endpoints and cases (54 operations, 128 collection requests)

`Auth` is who may call: **public** (no login), **guest** (signed-out only), **session** (signed in), **verified** (signed in and email verified). Cases are the collection requests that hit the operation; the status is what the request asserts. Operations without cases are either destructive (account deletion, `PATCH /spaces/{id}`), need external parties (verification mail links, Stripe), or are framework-internal.

| Method | Path | Auth | Limit | Documented responses | Collection cases (asserted status) |
| --- | --- | --- | --- | --- | --- |
| GET | `/livez` | public |  | 200 | GET /livez (200) |
| GET | `/readyz` | public |  | 200, 503 | GET /readyz (200) |
| GET | `/up` | public |  | 200 | GET /up (Laravel health check) (200) |
| POST | `/client-logs` | public | 60 requests per minute (shared bucket, see TooManyRequests) | 204, 403, 422, 500, 503 | POST /client-logs accepts a batch from the page's own Origin (204) (204)<br>POST /client-logs with Sec-Fetch-Site: same-origin (204) (204)<br>POST /client-logs with an invalid payload is 422 (422)<br>POST /client-logs with no lines is 422 (422)<br>POST /client-logs with more than 20 lines is 422 (422)<br>POST /client-logs with oversized data is 422 (422)<br>POST /client-logs from another origin is 403 (403)<br>POST /client-logs with Sec-Fetch-Site: cross-site is 403 (403)<br>POST /client-logs with neither Origin nor Sec-Fetch-Site is 403 (403)<br>POST /client-logs until the limit answers 429 (429) |
| GET | `/{slug}` | public |  | 200, 500, 503 | GET /{slug} (Inertia page) (200)<br>GET /{slug} (browser) is an HTML document (200)<br>GET /{unknown slug} (JSON) is 404 (404)<br>GET /{unknown slug} (browser) is the HTML 404 page (404)<br>GET /{slug} shows the thank-you flash (200)<br>GET /{slug} reports accepting=false (200)<br>GET /{slug} shows the not-accepting flash (200)<br>GET /{slug} after deletion is 404 (404) |
| POST | `/{slug}` | public | 20 requests per minute (shared bucket) | 302, 404, 419, 422, 429, 500, 503 | POST /{slug} with an empty body is 422 (422)<br>POST /{slug} with a bad rating and a disabled field is 422 (422)<br>POST /{slug} with an invalid email is 422 (422)<br>POST /{slug} submits a testimonial (302 back) (302)<br>POST /{slug} to a closed space redirects back and stores nothing (302)<br>POST /{slug} is throttled too (shared bucket) (429) |
| GET | `/embed/{spaceId}` | public |  | 200, 404, 500, 503 | GET /embed/{id} (browser) can be framed anywhere (200)<br>GET /embed/{id} (Inertia page) carries only public props (200) |
| GET | `/embed/{spaceId}/testimonials.json` | public |  | 200, 404, 500, 503 | GET /embed/{id}/testimonials.json lists the published testimonial (200)<br>GET /embed/{missing}/testimonials.json is 404 (404)<br>GET /embed/{id}/testimonials.json after deletion is 404 (404) |
| GET | `/register` | guest |  | 200, 302, 500, 503 | GET /register (Inertia page) (200) |
| POST | `/register` | guest |  | 302, 419, 422, 500, 503 | POST /register with a taken email and weak password is 422 (422) |
| GET | `/login` | guest |  | 200, 302, 500, 503 | Bootstrap: GET /login (cookies, Inertia version) (200)<br>GET /login with a stale Inertia version is 409 (409)<br>GET /login (Inertia page) (200)<br>GET /login while signed in redirects to /dashboard (302) |
| POST | `/login` | guest | 5 failed attempts per email+IP (422), 10/min per IP at the edge | 302, 419, 422, 500, 503 | POST /login without a CSRF token is 419 (419)<br>POST /login with an empty body is 422 (422)<br>POST /login with a malformed email is 422 (422)<br>POST /login with the wrong password is 422 (422)<br>POST /login signs in (302 to /dashboard) (302)<br>Sign in again for the optional requests (302)<br>POST /login locks out after 5 failures (422, not 429) (422) |
| POST | `/logout` | session |  | 302, 401, 419, 500, 503 | POST /logout (JSON) is 401 (401)<br>POST /logout (302 to /) (302)<br>POST /logout before the throttle test (302/303) |
| GET | `/forgot-password` | guest |  | 200, 302, 500, 503 | GET /forgot-password (Inertia page) (200) |
| POST | `/forgot-password` | guest |  | 302, 419, 422, 500, 503 | POST /forgot-password with a malformed email is 422 (422)<br>POST /forgot-password for an unknown address redirects back (302) |
| GET | `/reset-password/{token}` | guest |  | 200, 302, 500, 503 | GET /reset-password/{token} echoes the token (200) |
| POST | `/reset-password` | guest |  | 302, 419, 422, 500, 503 | POST /reset-password with a bad token is 422 (422) |
| GET | `/verify-email` | session |  | 200, 302, 401, 500, 503 | GET /verify-email for a verified user redirects to /dashboard (302) |
| GET | `/verify-email/{id}/{hash}` | session | 6 per minute (shared bucket) | 302, 401, 403, 429, 500, 503 | none |
| POST | `/email/verification-notification` | session | 6 per minute (shared bucket) | 302, 401, 419, 429, 500, 503 | none |
| GET | `/confirm-password` | session |  | 200, 302, 401, 500, 503 | GET /confirm-password (Inertia page) (200) |
| POST | `/confirm-password` | session |  | 302, 401, 419, 422, 500, 503 | POST /confirm-password with the wrong password is 422 (422)<br>POST /confirm-password with the right password redirects (302) |
| GET | `/settings` | session |  | 302, 401, 500, 503 | GET /settings redirects to /settings/profile (302) |
| GET | `/settings/profile` | session |  | 200, 302, 401, 500, 503 | GET /settings/profile (Inertia page) (200) |
| PATCH | `/settings/profile` | session |  | 302, 401, 419, 422, 500, 503 | PATCH /settings/profile with bad values is 422 (422)<br>PATCH /settings/profile with the current values redirects (302) |
| DELETE | `/settings/profile` | session |  | 302, 401, 419, 422, 500, 503 | DELETE /settings/profile with the wrong password is 422 (422) |
| GET | `/settings/password` | session |  | 200, 302, 401, 500, 503 | GET /settings/password (Inertia page) (200) |
| PUT | `/settings/password` | session |  | 302, 401, 419, 422, 500, 503 | PUT /settings/password with the wrong current password is 422 (422)<br>PUT /settings/password with a mismatched confirmation is 422 (422) |
| GET | `/settings/appearance` | session |  | 200, 302, 401, 500, 503 | GET /settings/appearance (Inertia page) (200) |
| GET | `/dashboard` | verified |  | 200, 302, 401, 409, 422, 500, 503 | GET /dashboard (JSON) is 401 (401)<br>Stale Inertia version on a protected page: auth runs first (302) (302)<br>GET /dashboard (browser) redirects to /login and is remembered (302)<br>GET /dashboard (Inertia page) (200)<br>GET /dashboard?range=7 (200)<br>GET /dashboard with a stale Inertia version is 409 (409)<br>GET /dashboard?range=5 is 422 (422)<br>GET /dashboard after logout redirects to /login (302) |
| POST | `/dashboard/banner/dismiss` | verified |  | 302, 401, 419, 500, 503 | POST /dashboard/banner/dismiss (permanent) (302/303) |
| GET | `/spaces` | verified |  | 200, 302, 401, 409, 500, 503 | GET /spaces (JSON) is 401 (401)<br>GET /spaces (Inertia page) records whether a space can be created (200) |
| POST | `/spaces` | verified |  | 302, 401, 419, 422, 500, 503 | POST /spaces (JSON) is 401 (401)<br>POST /spaces with invalid fields is 422 (422)<br>POST /spaces with an empty body is 422 (422)<br>POST /spaces creates the space (302 to /spaces/{id}) (302)<br>POST /spaces again hits the Free plan limit (302 to /billing) (302) |
| GET | `/spaces/create` | verified |  | 200, 302, 401, 500, 503 | GET /spaces/create (Inertia page) (200) |
| GET | `/spaces/{spaceId}` | verified |  | 200, 302, 401, 403, 404, 409, 422, 500, 503 | GET /spaces/{id} (Inertia inbox) (200)<br>GET /spaces/{id} shows the update and keeps the slug (200)<br>GET /spaces/{missing} (JSON) is 404 (404)<br>GET /spaces/{missing} (Inertia visit) is the errors/error page (404)<br>GET /spaces/{missing} (browser) is the HTML 404 page (404)<br>GET /spaces/{id} lists the new testimonial (200)<br>GET /spaces/{id}?filter=pending (200)<br>GET /spaces/{id}?filter=published is empty (200)<br>GET /spaces/{id}?from=&to= (date range) (200)<br>GET /spaces/{id}?filter=bogus is 422 (422)<br>GET /spaces/{id}?from>to is 422 (422)<br>GET /spaces/{id} shows published, favorite and edited (200)<br>GET /spaces/{id}?filter=favorite (200)<br>GET /spaces/{id} shows the testimonial gone (200)<br>GET /spaces/{id} after deletion is 404 (404)<br>GET /spaces/{foreign id} is 403 (another owner's space) (403) |
| GET | `/spaces/{spaceId}/edit` | verified |  | 200, 302, 401, 403, 404, 409, 500, 503 | GET /spaces/{id}/edit (Inertia form) (200) |
| PUT | `/spaces/{spaceId}` | verified |  | 302, 401, 403, 404, 419, 422, 500, 503 | PUT /spaces/{id} with an empty body is 422 (422)<br>PUT /spaces/{id} updates the space (302) (302/303)<br>PUT /spaces/{id} closes the form (is_accepting=false) (302/303)<br>PUT /spaces/{id} reopens the form (302/303) |
| PATCH | `/spaces/{spaceId}` | verified |  | 302, 401, 403, 404, 419, 422, 500, 503 | none |
| DELETE | `/spaces/{spaceId}` | verified |  | 302, 401, 403, 404, 419, 500, 503 | DELETE /spaces/{id} (302 to /spaces) (302/303)<br>DELETE /spaces/{id} twice is 404 (404) |
| PATCH | `/testimonials/{testimonialId}` | verified |  | 302, 401, 403, 404, 419, 422, 500, 503 | PATCH /testimonials/{id} with a too-short body is 422 (422)<br>PATCH /testimonials/{id} edits the text (302/303) |
| PATCH | `/testimonials/{testimonialId}/status` | verified |  | 302, 401, 403, 404, 419, 422, 500, 503 | PATCH /testimonials/{id}/status (JSON) is 401 (401)<br>PATCH /testimonials/{id}/status with an unknown status is 422 (422)<br>PATCH /testimonials/{id}/status publishes it (302/303)<br>PATCH /testimonials/{missing}/status is 404 (404)<br>PATCH /testimonials/{foreign id}/status is 403 (403) |
| PATCH | `/testimonials/{testimonialId}/favorite` | verified |  | 302, 401, 403, 404, 419, 500, 503 | PATCH /testimonials/{id}/favorite marks it (302/303) |
| DELETE | `/testimonials/{testimonialId}` | verified |  | 302, 401, 403, 404, 419, 500, 503 | DELETE /testimonials/{missing} is 404 (404)<br>DELETE /testimonials/{id} (302/303) |
| GET | `/billing` | verified |  | 200, 302, 401, 409, 500, 503 | GET /billing (browser) redirects to /login (302)<br>GET /billing shows the space-limit flash message (200)<br>GET /billing (Inertia page) (200)<br>GET /billing shows the no-profile flash (200)<br>GET /billing shows the could-not-confirm flash (200) |
| POST | `/billing/checkout` | verified |  | 302, 401, 409, 419, 500, 503 | POST /billing/checkout without Stripe configured redirects to /billing (302)<br>POST /billing/checkout as an Inertia visit (302/303/409) |
| GET | `/billing/success` | verified |  | 302, 401, 500, 503 | GET /billing/success without a session id redirects with an error (302) |
| POST | `/billing/portal` | verified |  | 302, 401, 409, 419, 500, 503 | POST /billing/portal without a Stripe customer redirects to /billing (302) |
| POST | `/stripe/webhook` | public |  | 200, 403, 500, 503 | POST /stripe/webhook without a signature header (200/403) |
| GET | `/stripe/payment/{id}` | public |  | 200, 500, 503 | none |
| GET | `/` | public |  | 200, 500, 503 | GET / (Inertia welcome page) (200) |
| GET | `/storage/{path}` | public |  | 200, 403, 500, 503 | none |
| PUT | `/storage/{path}` | public |  | 204, 403, 500, 503 | none |
| GET | `/_inertia/devtools/entries` | public |  | 200, 403 | none |
| GET | `/_inertia/devtools/entries/{id}` | public |  | 200, 403, 404 | none |

Requests that hit no documented route (they test the unknown-route 404): Unknown route returns the JSON 404 shape.

## Folders of the collections

| Folder | Requests | Purpose |
| --- | --- | --- |
| 00 Setup | 1 | Fetches the CSRF and session cookies and the Inertia asset version. Always run first. Sets runId and spaceName. |
| 01 Health | 5 | Probes. No session needed. |
| 02 Unauthenticated | 10 | Protected routes before signing in, plus CSRF and Inertia-version failures. |
| 03 Auth | 17 | Guest pages, validation failures and the single sign-in every later folder depends on. |
| 04 Settings | 9 | Profile and password. Only invalid or no-op changes: the demo account keeps its data. |
| 05 Dashboard | 4 | Read-only. The banner dismissal changes the demo account permanently, so it lives in the optional folder. |
| 06 Spaces | 15 | Creates one space (unique name per run) and exercises the free-plan limit. Skips the dependent requests when the demo owner already has a space and the create is refused. |
| 07 Public collection | 9 | What a respondent does at /{slug}. The collection uses the owner's session for convenience; the routes are public. |
| 08 Inbox and testimonial actions | 15 | Reads the inbox with filters and runs every testimonial action once. |
| 09 Embed | 4 | Public embed routes: published testimonials only, frameable, never an email. |
| 10 Closed form | 5 | Closes the space to new submissions, checks the redirect-with-flash behaviour, then reopens it. |
| 11 Billing | 8 | Stripe is not configured on the dev stack, so checkout and portal redirect back with a message. With Stripe keys the checkout answers 302 (or 409 for Inertia) to checkout.stripe.com. |
| 12 Client logs | 9 | Browser log intake. Open endpoint without CSRF; 60 requests per minute. Same-origin browsers only: the request must carry Sec-Fetch-Site (same-origin or none) or an Origin header whose host equals the request host. Scripts that send neither are refused. |
| 13 Cleanup | 9 | Deletes everything this run created and signs out. Must run last (before the optional folder). |
| 99 Optional (side effects, throttling) | 8 | Skipped unless runOptional=true. Contains requests that change the demo account for good, need extra setup, or lock the rate-limit bucket for up to a minute. |

## Variables

See [../configuration.md](../configuration.md#api-collection-variables).

