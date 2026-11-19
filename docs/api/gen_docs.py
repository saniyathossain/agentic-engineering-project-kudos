"""Generates docs/api/README.md and docs/configuration.md, and warns when the code reads an env var nobody documented."""
import re
import sys

import cases as C
import endpoints as E
import envvars as V
import scan_env

ROOT = scan_env.ROOT

# Update when you re-run the clients against the dev stack (see README "Verified").
VERIFIED = {
    "date": "2026-11-19",
    "newman": "newman 6.2.3, clean path (owner without a space): 120 requests, 442 assertions, 0 failed; with `runOptional=true` and the foreign-space ids: 193 requests (loops included), 466 assertions, 0 failed; demo owner who already had a space (skip path): 79 requests, 275 assertions, 0 failed",
    "bruno": "Bruno CLI 4.3.0, clean path: 442 of 442 tests passed (120 requests run, the 8 optional ones skipped)",
    "redocly": "Redocly CLI lint: valid, 0 errors, 0 warnings with docs/api/redocly.yaml (without it: 0 errors and warnings only for redirect-only operations, probes without a 4xx, and localhost servers)",
}


def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


# ---------------------------------------------------------------------------------------------------------------
# README
# ---------------------------------------------------------------------------------------------------------------
def op_regex(path):
    return re.compile("^" + re.sub(r"\{[^}]+\}", "[^/]+", path) + "$")


def normalise_case_path(p):
    return re.sub(r"\{\{[^}]+\}\}", "x", p.split("?")[0])


def match_op(c):
    path = normalise_case_path(c["path"])
    best, best_score = None, None
    for op in E.OPS:
        if op["method"].upper() != c["method"]:
            continue
        if not op_regex(op["path"]).match(path):
            continue
        score = (-op["path"].count("{"), len(op["path"]))
        if best_score is None or score > best_score:
            best, best_score = op, score
    return best


def status_label(c):
    for a in c["expect"]:
        if a["k"] == "status":
            return "/".join(str(x) for x in a["codes"])
    return "?"


def readme():
    by_op = {}
    unmatched = []
    for f in C.FOLDERS:
        for c in f["cases"]:
            op = match_op(c)
            if op is None:
                unmatched.append(c)
                continue
            by_op.setdefault((op["method"], op["path"]), []).append((f["name"], c))
    n_cases = sum(len(f["cases"]) for f in C.FOLDERS)
    L = []
    w = L.append
    w("# Kudos API documentation\n")
    w("Everything in this folder is generated from three data files by one script. Edit the data, run the script, commit the output.\n")
    w("| File | What it is |")
    w("| --- | --- |")
    w("| `openapi.yaml`, `openapi.json` | OpenAPI 3.1 description of every route: auth, parameters, request bodies with validation limits, every response the code can produce, error shapes, headers, rate limits |")
    w("| `postman/kudos.postman_collection.json` (v2.1) + `kudos.local.postman_environment.json`, `kudos.prod-style.postman_environment.json` | Postman collection and environments |")
    w("| `insomnia/kudos.insomnia.json` | Insomnia v4 export with the collection and two sub-environments |")
    w("| `bruno/` | Bruno collection (`bruno.json`, `environments/*.bru`, one folder per area) |")
    w("| `scripts/foreign-space.sh` | Helper that creates a second verified owner with a space, for the 403 cases |")
    w("| `endpoints.py`, `cases.py`, `envvars.py` | The data: OpenAPI source, client cases, configuration reference |")
    w("| `build.py` (+ `gen_*.py`, `scan_env.py`) | The generator. Python 3 standard library only |")
    w("| `redocly.yaml` | Lint config for `redocly lint` |")
    w("| `../configuration.md` | Every environment variable and every collection variable (generated here too) |")
    w("")
    w("## Regenerate\n")
    w("```bash")
    w("python3 docs/api/build.py")
    w("```\n")
    w("This rewrites `openapi.*`, `postman/`, `insomnia/`, `bruno/`, this README and `docs/configuration.md`. It also prints a warning for every environment variable the PHP config reads that `envvars.py` does not describe, so the configuration reference cannot silently go stale. Do not edit generated files by hand; the next run overwrites them.\n")
    w("## Before you run a collection\n")
    w("1. Start the dev stack: `docker compose -f docker/docker-compose.yml up -d` (app on http://localhost:8010). The prod-style stack (nginx edge) works too: start it with `APP_PORT=8011` and pick the `prod-style` environment.")
    w("2. The collections sign in as `demo@kudos.test` / `password`, the owner `DatabaseSeeder` creates. This is local seed data, not a secret. Put another verified owner into the `email` and `password` variables to use a different account.")
    w("3. The run is **idempotent**: it creates one space named `API Probe <runId>`, one testimonial, then deletes both and signs out. The Free plan allows one space, so if the owner already has a space the create request is refused with a redirect to `/billing` (that is asserted), and every request that needs the new space skips itself. Nothing is created or deleted in that case; the space-dependent cases then do not run. Use an owner without a space for the full sequence.")
    w("4. Run the folders in order, in one run. They share one session and one set of variables (`00 Setup` fetches the cookies and the Inertia asset version; `03 Auth` signs in once; `13 Cleanup` deletes and signs out).")
    w("5. **Rate limits.** `POST /{slug}` (20 per minute) and `POST /client-logs` (60 per minute) share one counter per signed-in user, together with the verification-mail routes (6 per minute). A full run sends about 15 throttled requests, so wait 60 seconds before starting the next run or the submission cases answer 429. `POST /login` locks an email and IP pair after 5 failures; the run makes 1 to 3 failed attempts and then succeeds, which clears the counter.")
    w("6. Folder `99 Optional (side effects, throttling)` is skipped unless `runOptional=true`. It contains the 403 cross-owner cases (need `foreignSpaceId`, see below), the permanent banner dismissal, a loop that drives `/client-logs` into 429, the shared-bucket 429 on `POST /{slug}` and the 422 login lockout message. Run it last and expect to wait a minute afterwards.")
    w("7. **Foreign space for the 403 cases.** Run `docs/api/scripts/foreign-space.sh up` (dev stack only; it uses `artisan tinker`). It prints `foreignSpaceId` and `foreignTestimonialId`; set both variables and `runOptional=true`. Remove the second owner with `docs/api/scripts/foreign-space.sh down`.\n")
    w("## Postman\n")
    w("Import `postman/kudos.postman_collection.json` and `postman/kudos.local.postman_environment.json` (File, Import), select the environment, then Run collection (keep the order, leave 'Persist responses' off, do not enable 'Follow redirects' overrides: each request pins `followRedirects: false`). Saved example responses are attached to the requests.\n")
    w("Command line (newman):\n")
    w("```bash")
    w("npx --yes newman run docs/api/postman/kudos.postman_collection.json \\")
    w("  -e docs/api/postman/kudos.local.postman_environment.json")
    w("# a Dockerised run, reaching the host's published port:")
    w('docker run --rm -v "$PWD/docs/api:/api" -w /api node:26-alpine npx --yes newman run postman/kudos.postman_collection.json \\')
    w("  -e postman/kudos.local.postman_environment.json --env-var baseUrl=http://host.docker.internal:8010")
    w("# the optional folder:")
    w("newman run ... --env-var runOptional=true --env-var foreignSpaceId=<id> --env-var foreignTestimonialId=<id>")
    w("```\n")
    w("## Bruno\n")
    w("Open the folder `docs/api/bruno` in Bruno (Open Collection), choose the `local` or `prod-style` environment, run the collection. Command line:\n")
    w("```bash")
    w("cd docs/api/bruno && npx --yes @usebruno/cli run --env local")
    w("# Dockerised:")
    w('docker run --rm -v "$PWD/docs/api/bruno:/bruno" -w /bruno node:26-alpine npx --yes @usebruno/cli run --env local --env-var baseUrl=http://host.docker.internal:8010')
    w("```\n")
    w("Override any variable with `--env-var name=value` (for example `email`, `password`, `runOptional`). Scripts use `bru.runner.skipRequest()` and `bru.runner.setNextRequest()`, so use a current Bruno (the CLI above is 4.x).\n")
    w("## Insomnia\n")
    w("Import `insomnia/kudos.insomnia.json` (Application, Import), pick the sub-environment `Kudos local` or `Kudos prod-style`, then run the folders in order with the Collection Runner. Requests carry pre-request and after-response scripts (Insomnia 11 or newer) for the CSRF refresh, variable capture and assertions. Two limits of Insomnia's script engine shape this export: a script cannot skip a request, so the optional folder `99` and the loop-until-429 requests are left out, and requests that depend on the new space cannot skip themselves, so use an owner without a space (or accept failures for the space-dependent requests when one exists).\n")
    w("Command line: `inso run collection` needs the `inso` binary from the Insomnia releases page (`https://github.com/Kong/insomnia/releases`); the npm package `insomnia-inso` stops at 3.6.0, predates request scripts and does not run on current Node. The binary was not downloaded or run when this was written (see Verified).\n")
    w("## Verified\n")
    w(f"Last verified {VERIFIED['date']} against the dev stack (`http://localhost:8010`):\n")
    w(f"* OpenAPI: {VERIFIED['redocly']}.")
    w(f"* Postman: {VERIFIED['newman']}.")
    w(f"* Bruno: {VERIFIED['bruno']}.")
    w("* Insomnia: JSON structure and script syntax checked; not imported into the Insomnia app and not run with `inso` (no binary). Treat it as best effort.")
    w("* Edge-only behaviour (the nginx outage JSON with `source: edge`, `limit_req` zones) and the Stripe paths that need real keys (Checkout redirect, portal, webhook signature failure) are documented from the code and templates but were not exercised.\n")
    w("## How requests are written\n")
    w("* **JSON mode** (`Accept: application/json`): validation errors come back as 422 `{message, errors}`, unauthenticated as 401, other failures as `{error, code, dependency, request_id}`. Used for every error case.")
    w("* **Inertia mode** (`X-Inertia: true`, `X-Inertia-Version: {{inertiaVersion}}`): page routes return `{component, props, url, version}`; used to read props, flash messages and counts.")
    w("* **HTML mode** (`Accept: text/html`): documents, redirects to `/login`, the HTML error pages.")
    w("* Every request sends `X-Request-ID: {{requestId}}` (new per request) and asserts the response echoes it. Every unsafe request sends `X-XSRF-TOKEN: {{xsrfToken}}`, refreshed from the `XSRF-TOKEN` cookie after each response. Redirects are never followed, so `302` and `Location` can be asserted.")
    w("* Redirect-back responses (`back()`) depend on the `Referer`; the requests set it explicitly, otherwise the app redirects to the last page the session visited.")
    w("* Flash messages and validation errors of a redirect appear only in the next Inertia page object, so the requests that read them come right after the request that sets them.\n")
    w(f"## Endpoints and cases ({len(E.OPS)} operations, {n_cases} collection requests)\n")
    w("`Auth` is who may call: **public** (no login), **guest** (signed-out only), **session** (signed in), **verified** (signed in and email verified). Cases are the collection requests that hit the operation; the status is what the request asserts. Operations without cases are either destructive (account deletion, `PATCH /spaces/{id}`), need external parties (verification mail links, Stripe), or are framework-internal.\n")
    w("| Method | Path | Auth | Limit | Documented responses | Collection cases (asserted status) |")
    w("| --- | --- | --- | --- | --- | --- |")
    verified_paths = ("/dashboard", "/spaces", "/testimonials", "/billing")
    import gen_openapi
    for op in E.OPS:
        res = sorted(gen_openapi.build_responses(op).keys())
        if op["auth"] == "session":
            auth = "verified" if op["path"].startswith(verified_paths) else "session"
        else:
            auth = op["auth"]
        cs = by_op.get((op["method"], op["path"]), [])
        cell = "<br>".join(f"{md_escape(c['name'])} ({status_label(c)})" for _, c in cs) or "none"
        w(f"| {op['method'].upper()} | `{op['path']}` | {auth} | {md_escape(op['throttle'] or '')} | {', '.join(res)} | {cell} |")
    if unmatched:
        w("")
        w("Requests that hit no documented route (they test the unknown-route 404): " + ", ".join(md_escape(c["name"]) for c in unmatched) + ".")
    w("")
    w("## Folders of the collections\n")
    w("| Folder | Requests | Purpose |")
    w("| --- | --- | --- |")
    for f in C.FOLDERS:
        w(f"| {f['name']} | {len(f['cases'])} | {md_escape(f['desc'])} |")
    w("")
    w("## Variables\n")
    w("See [../configuration.md](../configuration.md#api-collection-variables).\n")
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------------------------
# configuration.md
# ---------------------------------------------------------------------------------------------------------------
def clean_default(expr):
    if expr is None:
        return "none"
    e = expr.strip()
    if e.startswith("'") and e.endswith("'") and len(e) >= 2:
        e = e[1:-1] or "(empty)"
    return e


def default_for(name, spec, scan):
    if spec["default"] is not None:
        return spec["default"]
    for _, d in scan.get(name, []):
        if d is not None:
            return clean_default(d)
    return "none"


def is_secret_name(name):
    return bool(re.search(r"PASSWORD|SECRET|TOKEN|_KEY$|ACCESS_KEY|WEBHOOK_URL|^REDIS_URL|^DB_URL|^MAIL_URL", name)) and name not in V.SECRET_EXACT_NOT


def table(rows):
    out = ["| Variable | Default | Read by | Meaning | Example | Secret |", "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        out.append("| " + " | ".join(r) + " |")
    return out


def documented_names():
    names = set()
    for _, _, entries in V.GROUPS + V.DOCKER_GROUPS:
        for k in entries:
            names.add(k.split(" ")[0])
            names.update(x.strip() for x in k.split(","))
    return names


def configuration(scan):
    L = []
    w = L.append
    w("# Configuration reference\n")
    w("Generated by `python3 docs/api/build.py` from `docs/api/envvars.py` and a scan of `codes/config/*.php`. Do not edit by hand.\n")
    w("## How configuration reaches the containers\n")
    w("* **Dev** (`docker/docker-compose.yml`): `docker/.envs/app.env.example` holds the defaults and is bind-mounted into the containers. The `app` container (the only one with `SETUP_ENV=1`) merges it with your private `docker/.envs/app.env` (your values win), generates `APP_KEY` when empty and writes `codes/.env` atomically; `queue` waits for that file. Do not edit `codes/.env` or `app.env` by hand for project settings: add new settings to `app.env.example` (and `app.prod.env.example`).")
    w("* **Prod** (`docker-compose.yml` + `docker-compose.prod.yml`, `make prod`): no `.env` file is baked into an image. The container environment comes from `docker/.envs/app.prod.env` (git-ignored; template `app.prod.env.example`), plus `docker/.envs/outage.env` for the two outage values, plus Docker secrets for the database password (`docker/.envs/secrets/db_password`, git-ignored). Any `NAME_FILE=/path` variable is turned into `NAME` by `entrypoint.prod.sh`.")
    w("* **Tests** use sqlite in memory through `codes/phpunit.xml`; the compose services must not pass database variables to the test process.")
    w("* **Secrets**: keys marked secret below must never be committed. The example files contain only empty values or local demo values (`DB_PASSWORD=kudos`, the seeded demo login).")
    w("* **Read by**: `app` = php-fpm or `artisan serve`; `queue` = the queue worker; `scheduler` = prod scheduler; `edge` = nginx; `db` = Postgres; `compose` = read by `docker compose` on the host.\n")
    for title, intro, entries in V.GROUPS:
        w(f"## {title}\n")
        w(intro + "\n")
        rows = []
        for name, spec in entries.items():
            rows.append([f"`{name}`", md_escape(f"`{default_for(name, spec, scan)}`" if default_for(name, spec, scan) not in ("none",) else "none"),
                         md_escape(spec["where"]), md_escape(spec["meaning"]), md_escape(f"`{spec['example']}`" if spec["example"] else ""),
                         "yes" if spec["secret"] else "no"])
        L.extend(table(rows))
        w("")
    for title, intro, entries in V.DOCKER_GROUPS:
        w(f"## {title}\n")
        w(intro + "\n")
        rows = []
        for name, spec in entries.items():
            rows.append([f"`{name}`", md_escape(f"`{spec['default']}`"), md_escape(spec["where"]), md_escape(spec["meaning"]),
                         md_escape(f"`{spec['example']}`" if spec["example"] else ""), "yes" if spec["secret"] else "no"])
        L.extend(table(rows))
        w("")
    # other settings found by the scan
    known = documented_names()
    others = sorted(n for n in scan if n not in known)
    w("## Other settings read by the PHP config\n")
    w("Stock Laravel options that Kudos leaves at their defaults. Found by scanning `env()` calls, so the list follows the code. Set one in the container environment only if you change that subsystem.\n")
    rows = []
    for n in others:
        note = next((t for p, t in V.OTHER_NOTES if n.startswith(p)), "Stock Laravel option.")
        files = sorted({f.replace("codes/", "") for f, _ in scan[n]})
        defaults = []
        for _, d in scan[n]:
            cd = clean_default(d)
            if cd not in defaults:
                defaults.append(cd)
        rows.append([f"`{n}`", md_escape("`" + " / ".join(defaults) + "`"), md_escape(", ".join(files)), md_escape(note), "", "yes" if is_secret_name(n) else "no"])
    L.extend(table(rows))
    w("")
    w("## API collection variables\n")
    w("Set in the Postman environment, the Insomnia environment, or the Bruno environment (`environments/local.bru`, `prod-style.bru`). Variables marked *run time* are written by the scripts during a run; leave them empty. Override on the command line with `--env-var name=value` (newman, Bruno).\n")
    w("| Variable | Default | Set by | Meaning | Secret |")
    w("| --- | --- | --- | --- | --- |")
    run_time = {"runId", "spaceName", "spaceSlug", "spaceId", "testimonialId", "userName", "xsrfToken", "requestId", "inertiaVersion", "canCreate"}
    for n in C.ENV_VARIABLES:
        default, desc, secret = C.VARIABLES[n]
        who = "run time" if n in run_time else ("you" if n in ("foreignSpaceId", "foreignTestimonialId", "runOptional") else "environment file")
        shown = "(empty)" if default == "" else default
        if n == "baseUrl":
            shown = "`http://localhost:8010` (local), `http://localhost:8011` (prod-style)"
        elif default != "":
            shown = f"`{default}`"
        w(f"| `{n}` | {md_escape(shown)} | {who} | {md_escape(desc)} | {'yes (local demo value)' if secret else 'no'} |")
    w("")
    w("`password` is the seeded demo login, so it is committed. Never put a real password or a Stripe key into an environment file that is committed; use the app's own variable-secret feature or `--env-var`.\n")
    w("## Docker secrets and files that are never committed\n")
    w("* `docker/.envs/app.env` (private overrides, dev), `docker/.envs/app.prod.env` (prod environment), `docker/.envs/secrets/db_password` (prod database password), `codes/.env` (written by the app container).")
    w("* Committed on purpose: `app.env.example`, `app.prod.env.example` and `outage.env`.\n")
    return "\n".join(L)


def check_env_coverage(scan):
    known = documented_names()
    missing = sorted(n for n in scan if n not in known)
    compose_vars = set()
    for f in (ROOT / "docker").glob("docker-compose*.yml"):
        compose_vars.update(re.findall(r"\$\{([A-Z][A-Z0-9_]*)", f.read_text()))
    for f in (ROOT / "docker" / ".envs").glob("*.example"):
        compose_vars.update(re.findall(r"^([A-Z][A-Z0-9_]*)=", f.read_text(), re.M))
    undocumented = sorted(n for n in compose_vars if n not in known and n not in scan)
    if undocumented:
        print("warning: compose or example-env variables not described in envvars.py: " + ", ".join(undocumented), file=sys.stderr)
    return missing


def write(outdir, openapi_doc):
    scan = scan_env.scan()
    (outdir / "README.md").write_text(readme() + "\n")
    (ROOT / "docs" / "configuration.md").write_text(configuration(scan) + "\n")
    check_env_coverage(scan)
