"""Builds the OpenAPI 3.1 document from endpoints.py and writes openapi.yaml / openapi.json."""
import copy
import json
import re

import endpoints as E

DESCRIPTION = """\
HTTP surface of Kudos, a testimonial collector (Laravel 13 + Inertia 3). Kudos is a server-rendered web app, not a
token API: every page route doubles as a JSON endpoint when you speak the Inertia protocol, and every form route
answers with redirects. This document lists every route the app registers and every response its code can produce.

## Who may call what

| Audience | Routes | Needs |
| --- | --- | --- |
| Anyone | `/livez`, `/readyz`, `/up`, `/client-logs`, `/{slug}` (GET, POST), `/embed/...`, `/stripe/webhook` | Nothing for GETs. POSTs need the CSRF cookie flow, except `/client-logs` and the webhook. |
| Guests only | `/register`, `/login`, `/forgot-password`, `/reset-password` | No session user. Signed-in users are redirected to `/dashboard`. |
| Signed-in owners | `/logout`, `/settings/*`, `/confirm-password`, `/email/verification-notification`, `/verify-email*` | Session cookie. |
| Verified owners | `/dashboard`, `/spaces*`, `/testimonials/*`, `/billing*` | Session cookie and a verified email. An unverified user is redirected to `/verify-email`. |

There are no API keys or bearer tokens. Authentication is the Laravel session cookie (`kudos_session`, HttpOnly,
SameSite=Lax, 120 minutes). Ownership is checked per record: another owner's space or testimonial gives 403.

## CSRF cookie flow

1. Send any GET (for example `GET /login`). The response sets two cookies: `XSRF-TOKEN` (readable) and `kudos_session`.
2. URL-decode the `XSRF-TOKEN` value and send it as the `X-XSRF-TOKEN` header on every `POST`, `PUT`, `PATCH` and `DELETE`,
   with the same cookie jar.
3. Signing in regenerates the session, so the token changes: read the cookie again after `POST /login`.
4. Exempt: `POST /client-logs` (checked by Origin instead) and `POST /stripe/webhook` (checked by Stripe signature).
5. A missing or wrong token gives `419`.

## Inertia protocol

Page routes return an HTML document by default. Send `X-Inertia: true` and `X-Inertia-Version: <version>` and the same
route returns a JSON page object `{component, props, url, version, sharedProps}` with `Vary: X-Inertia`. Get the version
from the first HTML page (`"version"` inside the `data-page` script) or from any earlier page object.

* A GET with `X-Inertia: true` and a stale or missing version returns `409` with `X-Inertia-Location` (reload the URL).
* Any other failure with `X-Inertia: true` (404, 403, 419, 429, 500) returns an Inertia page object for the component `errors/error` with the real status code (props `status`, `copyKey`, `retryAfter`, `requestId`). Only a dependency outage (503) returns `409` + `X-Inertia-Location`, so the browser loads the database-free outage page in full.
* After `PUT`, `PATCH` and `DELETE` an Inertia client gets `303` where others get `302`.
* Flash messages (`props.flash.success`, `props.flash.error`) and validation errors (`props.errors`) of a redirect appear
  once, in the next page object, then vanish.

## Two ways to talk to the form routes

| You send | Success | Validation failure | Unauthenticated | Other failures |
| --- | --- | --- | --- | --- |
| `Accept: application/json` (no X-Inertia) | 302/303 redirect (do not follow it blindly) or 204 | `422` `{message, errors}` | `401` `{message}` | `{error, code, dependency, request_id}` |
| Neither header (plain HTML) | redirect | redirect back | `302` to `/login` | HTML error page |
| `X-Inertia: true` or a browser form post | redirect | redirect back, errors in the next page's `props.errors` | `302` to `/login` | `errors/error` page object with the real status (503: 409 + `X-Inertia-Location`) |

The collections in `docs/api` use the JSON style for error cases and the Inertia style to read page props.

## Error shapes

* `ErrorResponse` `{error, code, dependency, request_id}`: 403, 404, 419, 429, 500, 503. `error` is generic text; use the status.
  `code` is `unavailable` and `dependency` is `database`, `billing` or `app` for a 503; otherwise `error` and `null`.
* `ValidationError` `{message, errors}`: 422.
* `Unauthenticated` `{message}`: 401.
* `EdgeErrorResponse`: like ErrorResponse plus `source: "edge"`, produced by nginx when the app does not answer.

## Headers

* `X-Request-ID`: send your own (8 to 64 chars of `A-Za-z0-9._-`) or get one; it is echoed on every response, including errors.
  `traceparent` (W3C) is also read for log correlation.
* `Retry-After`: on 429 and on every 503 (5 seconds for dependency failures).
* `X-Inertia`, `X-Inertia-Version`, `X-Inertia-Location`: see above.
* `Cache-Control: no-store, private` on error bodies; probes send `no-store`.
* Every response from the app carries `Permissions-Policy` and `Cross-Origin-Opener-Policy: same-origin`, plus `Strict-Transport-Security` over HTTPS.
  A nonce-based `Content-Security-Policy` is added when `CSP_ENABLED` is true (default in production only; `CSP_REPORT_ONLY=true` makes it report-only).
  Embed routes get `frame-ancestors *` in it and lose `X-Frame-Options`; every other route has `frame-ancestors 'self'` and, behind nginx, `X-Frame-Options: SAMEORIGIN`.

## Rate limits

| Route | Limit | Over the limit |
| --- | --- | --- |
| `POST /login` | 5 failed attempts per email + IP | `422` with the throttle message on `email`, not 429 |
| `POST /{slug}` | 20 per minute | `429` + `Retry-After` |
| `POST /client-logs` | 60 per minute | `429` + `Retry-After` |
| `POST /email/verification-notification`, `GET /verify-email/{id}/{hash}` | 6 per minute | `429` + `Retry-After` |
| Edge nginx: `/login`, `/register`, `/forgot-password`, `/reset-password` | 10 per minute per IP, burst 10 | nginx 503, shown as the edge outage response |
| Edge nginx: `/client-logs` | 5 per second per IP, burst 20, body at most 16 KB | nginx 503 (outage response) or 413 |

The four `throttle:N,1` routes use Laravel's unnamed limiter, whose key is the user id (signed in) or the IP (anonymous),
not the route. They therefore share one counter: 60 log lines in a minute also lock `POST /{slug}` for the rest of that minute.
Verified against the running app.

## Plan limits (Free)

One space, ten testimonials per space. Limits never delete data on downgrade. Hitting them is not an HTTP error:
creating a second space redirects to `/billing` with a flash error, and a full or closed space redirects back from
`POST /{slug}` with a flash error. See the operations for the exact messages.

## Servers

Local dev serves `php artisan serve` on port 8010 (no nginx). The prod-style stack puts nginx in front of php-fpm; run it on
another port with `APP_PORT=8011` to keep dev running. Edge-level responses (outage 503 JSON, `/healthz`, the `limit_req`
zones) exist only there.
"""


def server_list():
    return [
        {"url": "http://localhost:8010", "description": "Local dev stack (docker compose, php artisan serve, no nginx). Demo owner demo@kudos.test / password is local seed data."},
        {"url": "http://localhost:8011", "description": "Prod-style stack (docker-compose.prod.yml, nginx edge in front of php-fpm) published with APP_PORT=8011."},
        {"url": "https://{host}", "description": "Edge in front of a real deployment (TLS terminated by your proxy). The `edge` 503 JSON appears here.",
         "variables": {"host": {"default": "kudos.example.com", "description": "Public host name."}}},
    ]


def security(op):
    unsafe = op["method"] != "get"
    csrf = op["csrf"] if op["csrf"] is not None else unsafe
    if op["auth"] == "session":
        return [{"sessionCookie": [], "csrfToken": []}] if csrf else [{"sessionCookie": []}]
    if op["auth"] in ("guest", "public") and csrf and unsafe:
        return [{"sessionCookie": [], "csrfToken": []}]
    return []


GENERATED = {}


def build_responses(op):
    res = copy.deepcopy(op["responses"])
    unsafe = op["method"] != "get"
    csrf = op["csrf"] if op["csrf"] is not None else unsafe
    if op["auth"] == "session":
        res.setdefault("302", E.R("LoginRedirect"))
        res.setdefault("401", E.R("Unauthenticated"))
        if csrf:
            res.setdefault("419", E.R("CsrfMismatch"))
    if op["auth"] == "guest":
        res.setdefault("302", E.R("GuestOnlyRedirect"))
    if op["path"] not in ("/livez", "/readyz", "/up") and not op["path"].startswith("/_inertia"):
        res.setdefault("500", E.R("ServerError"))
        res.setdefault("503", E.R("Unavailable"))
    # inline extra examples for refs that cannot carry them
    for code, examples in op["extra"]:
        base = res[code]
        name = base["$ref"].rsplit("/", 1)[1] if "$ref" in base else None
        comp = copy.deepcopy(E.RESPONSES[name]) if name else base
        content = comp.setdefault("content", {})
        js = content.setdefault("application/json", {"schema": E.S("ValidationError")})
        js.pop("example", None)
        js["examples"] = {k: {"summary": s, "value": E.EXAMPLES[v]} for k, (s, v) in examples.items()}
        cname = op["id"][0].upper() + op["id"][1:] + "ValidationFailed"
        GENERATED[cname] = comp
        res[code] = E.R(cname)
    return dict(sorted(res.items(), key=lambda kv: kv[0]))


def build_operation(op):
    o = {"operationId": op["id"], "tags": [op["tag"]], "summary": op["summary"], "description": op["description"]}
    if op["params"]:
        o["parameters"] = op["params"]
    if op["body"]:
        o["requestBody"] = op["body"]
    o["security"] = security(op)
    o["responses"] = build_responses(op)
    if op["throttle"]:
        o["x-rate-limit"] = op["throttle"]
    return o


def used_responses(paths):
    allr = {**E.RESPONSES, **GENERATED}
    text = json.dumps(paths)
    return {k: v for k, v in sorted(allr.items()) if f"#/components/responses/{k}\"" in text}


def build():
    paths = {}
    GENERATED.clear()
    for op in E.OPS:
        item = paths.setdefault(op["path"], {})
        item[op["method"]] = build_operation(op)
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Kudos HTTP API",
            "version": E.VERSION,
            "summary": "Every route of the Kudos testimonial app, with auth, limits and error shapes.",
            "description": DESCRIPTION,
            "license": {"name": "Proprietary (course project)", "identifier": "LicenseRef-Proprietary"},
            "contact": {"name": "Kudos maintainers", "url": "http://localhost:8010"},
        },
        "servers": server_list(),
        "tags": E.TAGS,
        "paths": paths,
        "components": {
            "securitySchemes": {
                "sessionCookie": {"type": "apiKey", "in": "cookie", "name": "kudos_session",
                                  "description": "Laravel session cookie set by `POST /login` (and by any first GET, as an anonymous session). Send it back on every request; a cookie jar does this for you."},
                "csrfToken": {"type": "apiKey", "in": "header", "name": "X-XSRF-TOKEN",
                              "description": "URL-decoded value of the `XSRF-TOKEN` cookie. Required together with the session cookie on state-changing requests."},
            },
            "schemas": E.SCHEMAS,
            "parameters": E.PARAMETERS,
            "headers": E.HEADERS,
            "responses": used_responses(paths),
        },
    }


# ---- minimal YAML emitter (stdlib only) -------------------------------------------------------------------
_PLAIN = re.compile(r"^[A-Za-z][A-Za-z0-9 _./()#-]*$")
_RESERVED = {"true", "false", "null", "yes", "no", "on", "off", "y", "n", "~"}


def _scalar(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return json.dumps(v)
    if _PLAIN.match(v) and v.lower() not in _RESERVED and not v.endswith(" ") and ": " not in v and " #" not in v:
        return v
    return json.dumps(v, ensure_ascii=False)


def _key(k):
    k = str(k)
    if re.match(r"^[A-Za-z_][A-Za-z0-9_./-]*$", k) and k.lower() not in _RESERVED:
        return k
    return json.dumps(k)


def dump_yaml(obj, indent=0):
    pad = "  " * indent
    lines = []
    if isinstance(obj, dict):
        if not obj:
            return [pad + "{}"]
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v:
                lines.append(f"{pad}{_key(k)}:")
                lines.extend(dump_yaml(v, indent + 1))
            elif isinstance(v, str) and "\n" in v:
                lines.append(f"{pad}{_key(k)}: |-")
                lines.extend(f"{pad}  {ln}" if ln else "" for ln in v.split("\n"))
            else:
                lines.append(f"{pad}{_key(k)}: {'{}' if v == {} else '[]' if v == [] else _scalar(v)}")
    elif isinstance(obj, list):
        for v in obj:
            if isinstance(v, (dict, list)) and v:
                sub = dump_yaml(v, indent + 1)
                first = sub[0].lstrip()
                lines.append(f"{pad}- {first}")
                lines.extend(sub[1:])
            elif isinstance(v, str) and "\n" in v:
                lines.append(f"{pad}- |-")
                lines.extend(f"{pad}  {ln}" if ln else "" for ln in v.split("\n"))
            else:
                lines.append(f"{pad}- {'{}' if v == {} else '[]' if v == [] else _scalar(v)}")
    return lines


def write(outdir):
    doc = build()
    (outdir / "openapi.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
    (outdir / "openapi.yaml").write_text("\n".join(dump_yaml(doc)) + "\n")
    return doc
