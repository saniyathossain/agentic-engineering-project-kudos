"""Single source of truth for the API-client collections (Postman, Insomnia, Bruno).

Every request, assertion, captured variable and saved example below is rendered into all three formats by gen_clients.py.

Request modes (how the request talks to the app):
  json     Accept: application/json            -> 422 / 401 / JSON errors; redirects are not followed
  inertia  X-Inertia: true + version header    -> page objects as JSON (props, flash, errors)
  html     Accept: text/html                   -> full documents, redirects to /login, error pages
  plain    no Accept header

Assertion helpers return small dicts, capture helpers too; the generators turn them into JavaScript.
"""
import endpoints as E

# ---- variables ------------------------------------------------------------------------------------------------
# name -> (default value, description, secret?)
VARIABLES = {
    "baseUrl": ("http://localhost:8010", "Origin of the app under test, no trailing slash.", False),
    "email": ("demo@kudos.test", "Owner login. Seeded by DatabaseSeeder; local only.", False),
    "password": ("password", "Owner password. Seeded local demo value; never use a real password here.", True),
    "runId": ("", "Set by the first request of every run (base-36 timestamp). Makes the space name and slug unique.", False),
    "spaceName": ("", "Name of the space this run creates (`API Probe <runId>`). Set with runId.", False),
    "spaceSlug": ("", "Slug of the created space. Captured from the inbox page.", False),
    "spaceId": ("", "Public ID (ULID) of the created space. Captured from the Location header of the create call.", False),
    "testimonialId": ("", "Public ID of the submitted testimonial. Captured from the inbox page.", False),
    "userName": ("", "Display name of the signed-in owner. Captured from the profile page so the no-op profile update keeps it.", False),
    "xsrfToken": ("", "URL-decoded XSRF-TOKEN cookie. Refreshed after every response.", False),
    "requestId": ("", "X-Request-ID sent with the current request. Generated before every request; the response must echo it.", False),
    "inertiaVersion": ("", "Inertia asset version. Captured from the HTML of GET /login.", False),
    "canCreate": ("", "`true` when the demo owner may still create a space (Free plan: none exists yet). Captured from the spaces page.", False),
    "missingId": ("01zzzzzzzzzzzzzzzzzzzzzzzz", "A well-formed ULID that matches no record. Used for 404 cases.", False),
    "foreignSpaceId": ("", "Optional. Public ID of a space owned by another verified user, for the 403 case. See README, `scripts/foreign-space.sh`.", False),
    "foreignTestimonialId": ("", "Optional. Public ID of a testimonial in that foreign space (printed by the helper script).", False),
    "runOptional": ("false", "Set to `true` to run the folder `99 Optional (side effects, throttling)`.", False),
}
# variables placed in the environment files (the rest are created at run time)
ENV_VARIABLES = ["baseUrl", "email", "password", "runId", "spaceName", "spaceSlug", "spaceId", "testimonialId", "userName", "xsrfToken", "requestId",
                 "inertiaVersion", "canCreate", "missingId", "foreignSpaceId", "foreignTestimonialId", "runOptional"]
ENVIRONMENTS = {
    "local": {"label": "Kudos local (dev stack, port 8010)", "baseUrl": "http://localhost:8010"},
    "prod-style": {"label": "Kudos prod-style (nginx edge, port 8011)", "baseUrl": "http://localhost:8011"},
}


# ---- assertion / capture helpers ------------------------------------------------------------------------------
def status(*codes):
    return {"k": "status", "codes": list(codes)}


def header(name, pattern=None):
    return {"k": "header", "name": name, "pattern": pattern}


def header_opt(name, pattern):
    """Passes when the header is absent, otherwise it must match (for headers that depend on configuration, such as CSP)."""
    return {"k": "header_opt", "name": name, "pattern": pattern}


def cookie(name):
    return {"k": "cookie", "name": name}


def no_header(name):
    return {"k": "no_header", "name": name}


def location(pattern):
    return {"k": "location", "pattern": pattern}


def js(path, op="exists", value=None):
    """JSON body assertion. op: exists, missing, eq, type, match, gte, len_gte, includes, in."""
    return {"k": "json", "path": path, "op": op, "value": value}


def text(substr):
    return {"k": "text", "value": substr}


def no_text(substr):
    return {"k": "no_text", "value": substr}


def cap_json(var, path):
    return {"var": var, "from": "json", "arg": path}


def cap_location(var, regex):
    return {"var": var, "from": "location", "arg": regex}


def cap_body(var, regex):
    return {"var": var, "from": "body", "arg": regex}


def case(name, method, path, mode="json", body=None, query=None, headers=None, referer=None, csrf=None, expect=(), capture=(),
         example=None, needs=(), optional=False, desc="", loop_until=None, csrf_value=None, version_value=None):
    """One request. `example` is (statusCode, exampleKey or None, extra response headers dict)."""
    return dict(name=name, method=method, path=path, mode=mode, body=body, query=query or [], headers=headers or {}, referer=referer,
                csrf=(method != "GET") if csrf is None else csrf, expect=list(expect), capture=list(capture), example=example,
                needs=list(needs), optional=optional, desc=desc, loop_until=loop_until, csrf_value=csrf_value, version_value=version_value)


SPACE_PATH = "/spaces/{{spaceId}}"
SPACE_BODY = {"name": "{{spaceName}}", "header_title": "Tell us what you think", "message": "Say **hi**", "collect_rating": True,
              "theme": "brand", "is_accepting": True, "fields": {"company": {"enabled": True, "required": False}}}
SUBMISSION = {"name": "Ada Lovelace", "email": "ada@example.com", "body": "Great <b>stuff</b> from {{spaceName}}", "consent": True,
              "rating": 5, "company": "Acme"}
LOC_LOGIN = r"/login$"
LOC_DASHBOARD = r"/dashboard$"
LOC_BILLING = r"/billing$"
BACK_INBOX = "{{baseUrl}}/spaces/{{spaceId}}"
BACK_PUBLIC = "{{baseUrl}}/{{spaceSlug}}"

F = []


def folder(name, desc, cases):
    F.append({"name": name, "desc": desc, "cases": cases})


# 00 ---------------------------------------------------------------------------------------------------------------
folder("00 Setup", "Fetches the CSRF and session cookies and the Inertia asset version. Always run first. Sets runId and spaceName.", [
    case("Bootstrap: GET /login (cookies, Inertia version)", "GET", "/login", mode="html",
         desc="Any GET sets the XSRF-TOKEN and session cookies. The asset version is read from the page's data-page JSON.",
         expect=[status(200), cookie("XSRF-TOKEN"), cookie("kudos_session"), text('data-page="app"'),
                 header("Permissions-Policy", r"camera=\(\)"), header("Cross-Origin-Opener-Policy", "^same-origin$")],
         capture=[cap_body("inertiaVersion", r'"version":"([0-9a-f]+)"')],
         example=(200, None, {"Set-Cookie": "XSRF-TOKEN=eyJpdiI6...; Max-Age=7200; path=/; samesite=lax", "Content-Type": "text/html; charset=utf-8"})),
])

# 01 ---------------------------------------------------------------------------------------------------------------
folder("01 Health", "Probes. No session needed.", [
    case("GET /livez", "GET", "/livez", expect=[status(200), js("status", "eq", "ok"), header("Cache-Control", "no-store")], example=(200, "live", {})),
    case("GET /readyz", "GET", "/readyz", expect=[status(200), js("status", "eq", "ok"), js("checks", "len_gte", 3),
                                                   js("checks[0].name", "eq", "database"), js("checks[0].critical", "eq", True)],
         example=(200, "ready", {})),
    case("GET / (Inertia welcome page)", "GET", "/", mode="inertia", expect=[status(200), js("component", "eq", "welcome"), js("props.build.name", "exists")],
         desc="Public. Every page carries the shared props (name, auth, flash, build, plan ...).", example=(200, "page_login", {})),
    case("GET /up (Laravel health check)", "GET", "/up", expect=[status(200), js("status", "eq", "up")], example=(200, "up", {})),
    case("Unknown route returns the JSON 404 shape", "GET", "/no-such-page/at/all", expect=[
        status(404), js("code", "eq", "error"), js("dependency", "eq", None), js("request_id", "eq", "{{requestId}}")],
         desc="Shape is {error, code, dependency, request_id}; request_id equals the id we sent.", example=(404, "error_404", {})),
])

# 02 ---------------------------------------------------------------------------------------------------------------
folder("02 Unauthenticated", "Protected routes before signing in, plus CSRF and Inertia-version failures.", [
    case("GET /billing (browser) redirects to /login", "GET", "/billing", mode="html", expect=[status(302), location(LOC_LOGIN)],
         example=(302, None, {"Location": "http://localhost:8010/login"})),
    case("GET /dashboard (JSON) is 401", "GET", "/dashboard", expect=[status(401), js("message", "eq", "Unauthenticated.")],
         example=(401, "unauthenticated", {})),
    case("GET /spaces (JSON) is 401", "GET", "/spaces", expect=[status(401), js("message", "eq", "Unauthenticated.")], example=(401, "unauthenticated", {})),
    case("POST /spaces (JSON) is 401", "POST", "/spaces", body=SPACE_BODY, expect=[status(401)], example=(401, "unauthenticated", {})),
    case("PATCH /testimonials/{id}/status (JSON) is 401", "PATCH", "/testimonials/{{missingId}}/status", body={"status": "published"},
         expect=[status(401)], example=(401, "unauthenticated", {})),
    case("POST /logout (JSON) is 401", "POST", "/logout", expect=[status(401)], example=(401, "unauthenticated", {})),
    case("POST /login without a CSRF token is 419", "POST", "/login", body={"email": "{{email}}", "password": "{{password}}"}, csrf_value="not-a-token",
         expect=[status(419), js("code", "eq", "error"), js("request_id", "eq", "{{requestId}}")],
         desc="The token is deliberately wrong. The body is the generic error shape; branch on the status.", example=(419, "error_419", {})),
    case("GET /login with a stale Inertia version is 409", "GET", "/login", mode="inertia", version_value="stale-version",
         expect=[status(409), header("X-Inertia-Location", r"/login$")],
         desc="Inertia location trick: the client must reload the URL as a normal page.",
         example=(409, None, {"X-Inertia-Location": "http://localhost:8010/login"})),
    case("Stale Inertia version on a protected page: auth runs first (302)", "GET", "/dashboard", mode="inertia", version_value="stale-version",
         expect=[status(302), location(LOC_LOGIN)], desc="The auth middleware runs before the Inertia version check, so a signed-out client is sent to /login, not told to reload.",
         example=(302, None, {"Location": "http://localhost:8010/login"})),
    case("GET /dashboard (browser) redirects to /login and is remembered", "GET", "/dashboard", mode="html", expect=[status(302), location(LOC_LOGIN)],
         desc="Runs last in this folder on purpose: the app remembers this URL as the intended destination, so the sign-in below redirects to /dashboard.",
         example=(302, None, {"Location": "http://localhost:8010/login"})),
])

# 03 ---------------------------------------------------------------------------------------------------------------
folder("03 Auth", "Guest pages, validation failures and the single sign-in every later folder depends on.", [
    case("GET /login (Inertia page)", "GET", "/login", mode="inertia",
         expect=[status(200), header("X-Inertia", "true"), js("component", "eq", "auth/login"), js("props.canResetPassword", "eq", True), js("props.auth.user", "eq", None)],
         example=(200, "page_login", {"X-Inertia": "true", "Vary": "X-Inertia"})),
    case("GET /register (Inertia page)", "GET", "/register", mode="inertia", expect=[status(200), js("component", "eq", "auth/register")], example=(200, None, {})),
    case("GET /forgot-password (Inertia page)", "GET", "/forgot-password", mode="inertia", expect=[status(200), js("component", "eq", "auth/forgot-password")], example=(200, None, {})),
    case("GET /reset-password/{token} echoes the token", "GET", "/reset-password/demo-token", mode="inertia", query=[("email", "demo@kudos.test")],
         expect=[status(200), js("component", "eq", "auth/reset-password"), js("props.token", "eq", "demo-token"), js("props.email", "eq", "demo@kudos.test")], example=(200, None, {})),
    case("POST /login with an empty body is 422", "POST", "/login", body={}, expect=[status(422), js("errors.email[0]", "eq", "The email field is required."),
                                                                                       js("errors.password", "exists")],
         example=(422, "invalid_login_empty", {})),
    case("POST /login with a malformed email is 422", "POST", "/login", body={"email": "not-an-email", "password": "x"},
         expect=[status(422), js("errors.email", "exists")], example=(422, None, {})),
    case("POST /login with the wrong password is 422", "POST", "/login", body={"email": "{{email}}", "password": "definitely-wrong"},
         expect=[status(422), js("message", "eq", "These credentials do not match our records."), js("errors.email[0]", "eq", "These credentials do not match our records.")],
         desc="Counts as one failed attempt toward the 5-per-email-and-IP lockout; the successful login below clears it.", example=(422, "invalid_login_credentials", {})),
    case("POST /register with a taken email and weak password is 422", "POST", "/register",
         body={"name": "Probe", "email": "{{email}}", "password": "short", "password_confirmation": "different"},
         expect=[status(422), js("errors.email[0]", "eq", "The email has already been taken."), js("errors.password", "len_gte", 1)],
         desc="Nothing is created: the email is taken, so validation stops the request.", example=(422, "invalid_register", {})),
    case("POST /forgot-password with a malformed email is 422", "POST", "/forgot-password", body={"email": "bad"},
         expect=[status(422), js("errors.email[0]", "eq", "The email field must be a valid email address.")], example=(422, "invalid_forgot", {})),
    case("POST /forgot-password for an unknown address redirects back", "POST", "/forgot-password", body={"email": "nobody-{{runId}}@example.com"},
         referer="{{baseUrl}}/forgot-password", expect=[status(302), location(r"/forgot-password$")],
         desc="The answer is identical whether or not the account exists, and no mail is sent for an unknown address.",
         example=(302, None, {"Location": "http://localhost:8010/forgot-password"})),
    case("POST /reset-password with a bad token is 422", "POST", "/reset-password",
         body={"token": "bad-token", "email": "{{email}}", "password": "new-password-123", "password_confirmation": "new-password-123"},
         expect=[status(422), js("errors.email[0]", "eq", "This password reset token is invalid.")], example=(422, "invalid_reset_token", {})),
    case("POST /login signs in (302 to /dashboard)", "POST", "/login", body={"email": "{{email}}", "password": "{{password}}"},
         expect=[status(302), location(LOC_DASHBOARD), cookie("kudos_session"), cookie("XSRF-TOKEN")],
         desc="Runs once. Regenerates the session, so the XSRF token cookie changes and is re-read after this response.",
         example=(302, None, {"Location": "http://localhost:8010/dashboard", "Set-Cookie": "kudos_session=eyJpdiI6...; path=/; httponly; samesite=lax"})),
    case("GET /login while signed in redirects to /dashboard", "GET", "/login", mode="html", expect=[status(302), location(LOC_DASHBOARD)],
         desc="The guest middleware.", example=(302, None, {"Location": "http://localhost:8010/dashboard"})),
    case("GET /verify-email for a verified user redirects to /dashboard", "GET", "/verify-email", mode="html", expect=[status(302), location(LOC_DASHBOARD)],
         example=(302, None, {"Location": "http://localhost:8010/dashboard"})),
    case("GET /confirm-password (Inertia page)", "GET", "/confirm-password", mode="inertia", expect=[status(200), js("component", "eq", "auth/confirm-password")], example=(200, "page_confirm_password", {})),
    case("POST /confirm-password with the wrong password is 422", "POST", "/confirm-password", body={"password": "wrong"},
         expect=[status(422), js("errors.password[0]", "eq", "The provided password is incorrect.")], example=(422, "invalid_confirm_password", {})),
    case("POST /confirm-password with the right password redirects", "POST", "/confirm-password", body={"password": "{{password}}"},
         referer="{{baseUrl}}/confirm-password", expect=[status(302), location(LOC_DASHBOARD)], example=(302, None, {"Location": "http://localhost:8010/dashboard"})),
])

# 04 ---------------------------------------------------------------------------------------------------------------
folder("04 Settings", "Profile and password. Only invalid or no-op changes: the demo account keeps its data.", [
    case("GET /settings redirects to /settings/profile", "GET", "/settings", mode="html", expect=[status(302), header("Location", r"settings/profile$")],
         desc="Relative Location header.", example=(302, None, {"Location": "settings/profile"})),
    case("GET /settings/profile (Inertia page)", "GET", "/settings/profile", mode="inertia",
         expect=[status(200), js("component", "eq", "settings/profile"), js("props.auth.user.email", "eq", "{{email}}")],
         capture=[cap_json("userName", "props.auth.user.name")], example=(200, "page_profile", {})),
    case("PATCH /settings/profile with bad values is 422", "PATCH", "/settings/profile", body={"name": "", "email": "bad"},
         expect=[status(422), js("errors.name", "exists"), js("errors.email[0]", "eq", "The email field must be a valid email address.")], example=(422, "invalid_profile", {})),
    case("PATCH /settings/profile with the current values redirects", "PATCH", "/settings/profile", body={"name": "{{userName}}", "email": "{{email}}"},
         referer="{{baseUrl}}/settings/profile", expect=[status(302), location(r"/settings/profile$")],
         desc="Sends the current name and email back, so nothing changes and verification is kept.", example=(302, None, {"Location": "http://localhost:8010/settings/profile"})),
    case("GET /settings/password (Inertia page)", "GET", "/settings/password", mode="inertia", expect=[status(200), js("component", "eq", "settings/password")], example=(200, "page_password", {})),
    case("PUT /settings/password with the wrong current password is 422", "PUT", "/settings/password",
         body={"current_password": "wrong", "password": "new-password-123", "password_confirmation": "new-password-123"},
         expect=[status(422), js("errors.current_password[0]", "eq", "The password is incorrect.")], example=(422, "invalid_current_password", {})),
    case("PUT /settings/password with a mismatched confirmation is 422", "PUT", "/settings/password",
         body={"current_password": "{{password}}", "password": "new-password-123", "password_confirmation": "other-password-123"},
         expect=[status(422), js("errors.password", "exists")], desc="The current password is right; only the confirmation fails, so the password is unchanged."),
    case("DELETE /settings/profile with the wrong password is 422", "DELETE", "/settings/profile", body={"password": "wrong"},
         expect=[status(422), js("errors.password[0]", "eq", "The password is incorrect.")],
         desc="Never send the real password here: it deletes the account.", example=(422, "invalid_delete_account", {})),
    case("GET /settings/appearance (Inertia page)", "GET", "/settings/appearance", mode="inertia", expect=[status(200), js("component", "eq", "settings/appearance")], example=(200, None, {})),
])

# 05 ---------------------------------------------------------------------------------------------------------------
folder("05 Dashboard", "Read-only. The banner dismissal changes the demo account permanently, so it lives in the optional folder.", [
    case("GET /dashboard (Inertia page)", "GET", "/dashboard", mode="inertia",
         expect=[status(200), js("component", "eq", "dashboard"), js("props.stats.range", "eq", 30), js("props.stats.series", "len_gte", 30),
                 js("props.stats.usage.max_spaces", "eq", 1), js("props.stats.usage.max_testimonials_per_space", "eq", 10)],
         desc="Free plan numbers: 1 space, 10 testimonials per space. Fails on a Pro account.", example=(200, "page_dashboard", {})),
    case("GET /dashboard?range=7", "GET", "/dashboard", mode="inertia", query=[("range", "7")],
         expect=[status(200), js("props.stats.range", "eq", 7), js("props.stats.series", "len_gte", 7)], example=(200, None, {})),
    case("GET /dashboard with a stale Inertia version is 409", "GET", "/dashboard", mode="inertia", version_value="stale-version",
         expect=[status(409), header("X-Inertia-Location", r"/dashboard$"), no_header("X-Inertia")],
         desc="Signed in, so the version check is reached: the client must reload the URL as a normal page.",
         example=(409, None, {"X-Inertia-Location": "http://localhost:8010/dashboard"})),
    case("GET /dashboard?range=5 is 422", "GET", "/dashboard", query=[("range", "5")],
         expect=[status(422), js("errors.range[0]", "eq", "The selected range is invalid.")], example=(422, "invalid_range", {})),
])

# 06 ---------------------------------------------------------------------------------------------------------------
folder("06 Spaces", "Creates one space (unique name per run) and exercises the free-plan limit. Skips the dependent requests when the demo owner already has a space and the create is refused.", [
    case("GET /spaces (Inertia page) records whether a space can be created", "GET", "/spaces", mode="inertia",
         expect=[status(200), js("component", "eq", "spaces/index"), js("props.spaces", "type", "array"), js("props.canCreate", "type", "boolean")],
         capture=[cap_json("canCreate", "props.canCreate")], example=(200, "page_spaces_index", {})),
    case("GET /spaces/create (Inertia page)", "GET", "/spaces/create", mode="inertia", needs=["canCreate"],
         expect=[status(200), js("component", "eq", "spaces/form"), js("props.space", "eq", None), js("props.themes", "len_gte", 3),
                 js("props.optionalFields", "includes", "social_link")], example=(200, "page_spaces_form_new", {}),
         desc="Skipped when a space already exists (the server redirects to /billing then)."),
    case("POST /spaces with invalid fields is 422", "POST", "/spaces",
         body={"name": "x" * 81, "header_title": "H", "message": "m", "theme": "neon"},
         expect=[status(422), js("errors.name[0]", "eq", "The name field must not be greater than 80 characters."), js("errors.theme[0]", "eq", "The selected theme is invalid.")],
         example=(422, "invalid_space", {})),
    case("POST /spaces with an empty body is 422", "POST", "/spaces", body={},
         expect=[status(422), js("errors.name", "exists"), js("errors.header_title", "exists"), js("errors.message", "exists"), js("errors.theme", "exists")],
         example=(422, "invalid_space_empty", {})),
    case("POST /spaces creates the space (302 to /spaces/{id})", "POST", "/spaces", body=SPACE_BODY, referer="{{baseUrl}}/spaces/create",
         expect=[status(302), location(r"/(spaces/[0-9a-z]{26}|billing)$")],
         capture=[cap_location("spaceId", r"/spaces/([0-9a-z]{26})$")],
         desc="Success: Location is /spaces/{id}. If the owner already has a space (Free plan) it is /billing and spaceId stays empty, so the rest of the space flow is skipped.",
         example=(302, None, {"Location": "http://localhost:8010/spaces/" + E.SPACE_ID})),
    case("POST /spaces again hits the Free plan limit (302 to /billing)", "POST", "/spaces", body={**SPACE_BODY, "name": "{{spaceName}} second"},
         referer="{{baseUrl}}/spaces/create", expect=[status(302), location(LOC_BILLING)],
         desc="Not an error status. The flash message on the next page says why.", example=(302, None, {"Location": "http://localhost:8010/billing"})),
    case("GET /billing shows the space-limit flash message", "GET", "/billing", mode="inertia",
         expect=[status(200), js("props.flash.error", "eq", "Your Free plan includes 1 space. Upgrade to Pro to create more.")],
         desc="Flash messages are one-shot: this is the only request that can read it."),
    case("GET /spaces/{id} (Inertia inbox)", "GET", SPACE_PATH, mode="inertia", needs=["spaceId"],
         expect=[status(200), js("component", "eq", "spaces/show"), js("props.space.name", "eq", "{{spaceName}}"), js("props.space.theme", "eq", "brand"),
                 js("props.space.fields.company.enabled", "eq", True), js("props.testimonials.data", "len", 0), js("props.counts.all", "eq", 0),
                 js("props.filter", "eq", "all")],
         capture=[cap_json("spaceSlug", "props.space.slug")], example=(200, "page_space_show", {})),
    case("GET /spaces/{id}/edit (Inertia form)", "GET", SPACE_PATH + "/edit", mode="inertia", needs=["spaceId"],
         expect=[status(200), js("component", "eq", "spaces/form"), js("props.space.public_id", "eq", "{{spaceId}}")], example=(200, None, {})),
    case("PUT /spaces/{id} with an empty body is 422", "PUT", SPACE_PATH, body={}, needs=["spaceId"],
         expect=[status(422), js("errors.name", "exists"), js("errors.theme", "exists")], example=(422, "invalid_space_empty", {})),
    case("PUT /spaces/{id} updates the space (302)", "PUT", SPACE_PATH, needs=["spaceId"], referer=BACK_INBOX,
         body={**SPACE_BODY, "message": "Updated by the API collection", "theme": "dark"},
         expect=[status(302, 303), location(r"/spaces/[0-9a-z]{26}$")], desc="The slug does not change on update.",
         example=(302, None, {"Location": "http://localhost:8010/spaces/" + E.SPACE_ID})),
    case("GET /spaces/{id} shows the update and keeps the slug", "GET", SPACE_PATH, mode="inertia", needs=["spaceId"],
         expect=[status(200), js("props.space.message", "eq", "Updated by the API collection"), js("props.space.theme", "eq", "dark"),
                 js("props.space.slug", "eq", "{{spaceSlug}}"), js("props.flash.success", "eq", "Space updated.")]),
    case("GET /spaces/{missing} (JSON) is 404", "GET", "/spaces/{{missingId}}", expect=[status(404), js("code", "eq", "error"), js("request_id", "eq", "{{requestId}}")],
         example=(404, "error_404", {})),
    case("GET /spaces/{missing} (Inertia visit) is the errors/error page", "GET", "/spaces/{{missingId}}", mode="inertia",
         expect=[status(404), header("X-Inertia", "true"), js("component", "eq", "errors/error"), js("props.status", "eq", 404), js("props.copyKey", "eq", "404"),
                 js("props.requestId", "eq", "{{requestId}}")],
         desc="Inertia clients get the failure as a page object (the React error page) with the real status, not a JSON error body or a reload.",
         example=(404, "inertia_error_404", {"X-Inertia": "true"})),
    case("GET /spaces/{missing} (browser) is the HTML 404 page", "GET", "/spaces/{{missingId}}", mode="html",
         expect=[status(404), header("Content-Type", "text/html"), text("Page not found")], example=(404, None, {"Content-Type": "text/html; charset=utf-8"})),
])

# 07 ---------------------------------------------------------------------------------------------------------------
folder("07 Public collection", "What a respondent does at /{slug}. The collection uses the owner's session for convenience; the routes are public.", [
    case("GET /{slug} (Inertia page)", "GET", "/{{spaceSlug}}", mode="inertia", needs=["spaceSlug"],
         expect=[status(200), js("component", "eq", "public/collect"), js("props.accepting", "eq", True), js("props.space.name", "eq", "{{spaceName}}"),
                 no_text("respondent_email")], example=(200, "page_collect", {})),
    case("GET /{slug} (browser) is an HTML document", "GET", "/{{spaceSlug}}", mode="html", needs=["spaceSlug"],
         expect=[status(200), header("Content-Type", "text/html"), text('data-page="app"')], example=(200, None, {"Content-Type": "text/html; charset=utf-8"})),
    case("GET /{unknown slug} (JSON) is 404", "GET", "/no-such-space-{{runId}}", expect=[status(404), js("code", "eq", "error")], example=(404, "error_404", {})),
    case("GET /{unknown slug} (browser) is the HTML 404 page", "GET", "/no-such-space-{{runId}}", mode="html", expect=[status(404), text("Page not found")]),
    case("POST /{slug} with an empty body is 422", "POST", "/{{spaceSlug}}", body={}, needs=["spaceSlug"],
         expect=[status(422), js("errors.name", "exists"), js("errors.email", "exists"), js("errors.body", "exists"),
                 js("errors.consent[0]", "eq", "The consent field must be accepted."), js("errors.rating", "exists")],
         desc="The space collects ratings, so rating is required too.", example=(422, "invalid_submission_empty", {})),
    case("POST /{slug} with a bad rating and a disabled field is 422", "POST", "/{{spaceSlug}}", needs=["spaceSlug"],
         body={"name": "Ada", "email": "ada@example.com", "body": "Nice one", "consent": True, "rating": 9, "title": "CEO"},
         expect=[status(422), js("errors.rating[0]", "eq", "The rating field must be between 1 and 5."), js("errors.title[0]", "eq", "The title field is prohibited.")],
         desc="`title` is not enabled on this space, so sending it is rejected.", example=(422, "invalid_submission_rating", {})),
    case("POST /{slug} with an invalid email is 422", "POST", "/{{spaceSlug}}", needs=["spaceSlug"],
         body={**SUBMISSION, "email": "not-an-email"}, expect=[status(422), js("errors.email", "exists")]),
    case("POST /{slug} submits a testimonial (302 back)", "POST", "/{{spaceSlug}}", needs=["spaceSlug"], body=SUBMISSION, referer=BACK_PUBLIC,
         expect=[status(302), location(r"/api-probe-[0-9a-z]+$")],
         desc="Always a redirect back, success or not. The flash on the next load tells which.", example=(302, None, {"Location": "http://localhost:8010/api-probe-xyz"})),
    case("GET /{slug} shows the thank-you flash", "GET", "/{{spaceSlug}}", mode="inertia", needs=["spaceSlug"],
         expect=[status(200), js("props.flash.success", "eq", "Thank you! Your testimonial was sent.")]),
])

# 08 ---------------------------------------------------------------------------------------------------------------
folder("08 Inbox and testimonial actions", "Reads the inbox with filters and runs every testimonial action once.", [
    case("GET /spaces/{id} lists the new testimonial", "GET", SPACE_PATH, mode="inertia", needs=["spaceId"],
         expect=[status(200), js("props.testimonials.data", "len", 1), js("props.testimonials.data[0].status", "eq", "pending"),
                 js("props.testimonials.data[0].respondent_email", "eq", "ada@example.com"),
                 js("props.testimonials.data[0].body", "eq", "Great stuff from {{spaceName}}"),
                 js("props.testimonials.data[0].is_favorite", "eq", False), js("props.counts.pending", "eq", 1), js("props.counts.all", "eq", 1)],
         capture=[cap_json("testimonialId", "props.testimonials.data[0].public_id")],
         desc="HTML tags are stripped on submit: `<b>` is gone. The owner's view includes the respondent email.", example=(200, "page_space_show", {})),
    case("GET /spaces/{id}?filter=pending", "GET", SPACE_PATH, mode="inertia", query=[("filter", "pending")], needs=["spaceId"],
         expect=[status(200), js("props.filter", "eq", "pending"), js("props.testimonials.data", "len", 1)]),
    case("GET /spaces/{id}?filter=published is empty", "GET", SPACE_PATH, mode="inertia", query=[("filter", "published")], needs=["spaceId"],
         expect=[status(200), js("props.filter", "eq", "published"), js("props.testimonials.data", "len", 0)]),
    case("GET /spaces/{id}?from=&to= (date range)", "GET", SPACE_PATH, mode="inertia", query=[("from", "2020-01-01"), ("to", "2099-12-31")], needs=["spaceId"],
         expect=[status(200), js("props.range.from", "eq", "2020-01-01"), js("props.testimonials.data", "len", 1)]),
    case("GET /spaces/{id}?filter=bogus is 422", "GET", SPACE_PATH, query=[("filter", "bogus")], needs=["spaceId"],
         expect=[status(422), js("errors.filter[0]", "eq", "The selected filter is invalid.")], example=(422, "invalid_inbox_filter", {})),
    case("GET /spaces/{id}?from>to is 422", "GET", SPACE_PATH, query=[("from", "2026-01-01"), ("to", "2025-01-01")], needs=["spaceId"],
         expect=[status(422), js("errors.to[0]", "eq", "The to field must be a date after or equal to from.")], example=(422, "invalid_inbox_range", {})),
    case("PATCH /testimonials/{id}/status with an unknown status is 422", "PATCH", "/testimonials/{{testimonialId}}/status", body={"status": "bad"}, needs=["testimonialId"],
         expect=[status(422), js("errors.status[0]", "eq", "The selected status is invalid.")], example=(422, "invalid_status", {})),
    case("PATCH /testimonials/{id}/status publishes it", "PATCH", "/testimonials/{{testimonialId}}/status", body={"status": "published"}, needs=["testimonialId"],
         referer=BACK_INBOX, expect=[status(302, 303), location(r"/spaces/[0-9a-z]{26}$")],
         example=(302, None, {"Location": "http://localhost:8010/spaces/" + E.SPACE_ID})),
    case("PATCH /testimonials/{id}/favorite marks it", "PATCH", "/testimonials/{{testimonialId}}/favorite", needs=["testimonialId"], referer=BACK_INBOX,
         expect=[status(302, 303)], example=(302, None, {"Location": "http://localhost:8010/spaces/" + E.SPACE_ID})),
    case("PATCH /testimonials/{id} with a too-short body is 422", "PATCH", "/testimonials/{{testimonialId}}", body={"body": "x"}, needs=["testimonialId"],
         expect=[status(422), js("errors.body[0]", "eq", "The body field must be at least 3 characters.")], example=(422, "invalid_body", {})),
    case("PATCH /testimonials/{id} edits the text", "PATCH", "/testimonials/{{testimonialId}}", body={"body": "Edited by the <i>API</i> collection"}, needs=["testimonialId"],
         referer=BACK_INBOX, expect=[status(302, 303)], desc="Tags are stripped again."),
    case("GET /spaces/{id} shows published, favorite and edited", "GET", SPACE_PATH, mode="inertia", needs=["spaceId"],
         expect=[status(200), js("props.testimonials.data[0].status", "eq", "published"), js("props.testimonials.data[0].is_favorite", "eq", True),
                 js("props.testimonials.data[0].body", "eq", "Edited by the API collection"), js("props.counts.published", "eq", 1),
                 js("props.counts.favorite", "eq", 1), js("props.flash.success", "eq", "Testimonial updated.")]),
    case("GET /spaces/{id}?filter=favorite", "GET", SPACE_PATH, mode="inertia", query=[("filter", "favorite")], needs=["spaceId"],
         expect=[status(200), js("props.testimonials.data", "len", 1)]),
    case("PATCH /testimonials/{missing}/status is 404", "PATCH", "/testimonials/{{missingId}}/status", body={"status": "hidden"},
         expect=[status(404), js("code", "eq", "error")], example=(404, "error_404", {})),
    case("DELETE /testimonials/{missing} is 404", "DELETE", "/testimonials/{{missingId}}", expect=[status(404)], example=(404, "error_404", {})),
])

# 09 ---------------------------------------------------------------------------------------------------------------
folder("09 Embed", "Public embed routes: published testimonials only, frameable, never an email.", [
    case("GET /embed/{id}/testimonials.json lists the published testimonial", "GET", "/embed/{{spaceId}}/testimonials.json", needs=["spaceId"],
         expect=[status(200), js("data", "len", 1), js("data[0].body", "eq", "Edited by the API collection"), js("data[0].respondent_name", "eq", "Ada Lovelace"),
                 js("data[0].company", "eq", "Acme"), js("space.public_id", "eq", "{{spaceId}}"), js("space.theme", "eq", "dark"),
                 header_opt("Content-Security-Policy", r"frame-ancestors \*"), no_header("X-Frame-Options"), no_text("respondent_email"), no_text("ada@example.com"), no_text("is_favorite"),
                 no_text('"status"')], desc="The email, status and favorite flag never appear here. When the CSP is enabled (production default) it carries frame-ancestors * on this route.", example=(200, "embed_json", {})),
    case("GET /embed/{id} (browser) can be framed anywhere", "GET", "/embed/{{spaceId}}", mode="html", needs=["spaceId"],
         expect=[status(200), header_opt("Content-Security-Policy", r"frame-ancestors \*"), no_header("X-Frame-Options"), no_text("ada@example.com")],
         example=(200, None, {"Content-Type": "text/html; charset=utf-8"})),
    case("GET /embed/{id} (Inertia page) carries only public props", "GET", "/embed/{{spaceId}}", mode="inertia", needs=["spaceId"],
         expect=[status(200), js("component", "eq", "embed/wall"), js("props.testimonials", "len", 1), js("props.testimonials[0].respondent_email", "missing"),
                 no_text("ada@example.com")], example=(200, "page_embed", {})),
    case("GET /embed/{missing}/testimonials.json is 404", "GET", "/embed/{{missingId}}/testimonials.json", expect=[status(404), js("code", "eq", "error")], example=(404, "error_404", {})),
])

# 10 ---------------------------------------------------------------------------------------------------------------
folder("10 Closed form", "Closes the space to new submissions, checks the redirect-with-flash behaviour, then reopens it.", [
    case("PUT /spaces/{id} closes the form (is_accepting=false)", "PUT", SPACE_PATH, needs=["spaceId"], referer=BACK_INBOX,
         body={**SPACE_BODY, "is_accepting": False}, expect=[status(302, 303)]),
    case("GET /{slug} reports accepting=false", "GET", "/{{spaceSlug}}", mode="inertia", needs=["spaceSlug"],
         expect=[status(200), js("props.accepting", "eq", False)], example=(200, "page_collect_closed", {})),
    case("POST /{slug} to a closed space redirects back and stores nothing", "POST", "/{{spaceSlug}}", needs=["spaceSlug"], body=SUBMISSION, referer=BACK_PUBLIC,
         expect=[status(302)], desc="Not a 4xx: the refusal is the flash message on the next page."),
    case("GET /{slug} shows the not-accepting flash", "GET", "/{{spaceSlug}}", mode="inertia", needs=["spaceSlug"],
         expect=[status(200), js("props.flash.error", "eq", "This space is not accepting testimonials right now.")]),
    case("PUT /spaces/{id} reopens the form", "PUT", SPACE_PATH, needs=["spaceId"], referer=BACK_INBOX, body={**SPACE_BODY, "is_accepting": True},
         expect=[status(302, 303)]),
])

# 11 ---------------------------------------------------------------------------------------------------------------
folder("11 Billing", "Stripe is not configured on the dev stack, so checkout and portal redirect back with a message. With Stripe keys the checkout answers 302 (or 409 for Inertia) to checkout.stripe.com.", [
    case("GET /billing (Inertia page)", "GET", "/billing", mode="inertia",
         expect=[status(200), js("component", "eq", "billing/show"), js("props.overview.plan.value", "eq", "free"), js("props.overview.spaces_max", "eq", 1),
                 js("props.overview.testimonials_per_space_max", "eq", 10), js("props.overview.can_manage_billing", "eq", False)],
         desc="Free plan assumptions; fails on a Pro account.", example=(200, "page_billing", {})),
    case("POST /billing/checkout without Stripe configured redirects to /billing", "POST", "/billing/checkout", referer="{{baseUrl}}/billing",
         expect=[status(302), location(r"(/billing$|^https://checkout\.stripe\.com/)")],
         desc="Unconfigured: back to /billing with a flash error naming the missing keys. Configured: a redirect to Stripe."),
    case("POST /billing/checkout as an Inertia visit", "POST", "/billing/checkout", mode="inertia", referer="{{baseUrl}}/billing",
         expect=[status(302, 303, 409)], desc="Configured: 409 with X-Inertia-Location = the Stripe URL. Unconfigured: a redirect to /billing."),
    case("POST /billing/portal without a Stripe customer redirects to /billing", "POST", "/billing/portal", referer="{{baseUrl}}/billing",
         expect=[status(302), location(LOC_BILLING)]),
    case("GET /billing shows the no-profile flash", "GET", "/billing", mode="inertia", expect=[status(200), js("props.flash.error", "eq", "No billing profile yet.")]),
    case("GET /billing/success without a session id redirects with an error", "GET", "/billing/success", mode="html",
         expect=[status(302), location(LOC_BILLING)], desc="The redirect from Stripe proves nothing; without a confirmed session the app says so."),
    case("GET /billing shows the could-not-confirm flash", "GET", "/billing", mode="inertia",
         expect=[status(200), js("props.flash.error", "eq", "We could not confirm that payment.")]),
    case("POST /stripe/webhook without a signature header", "POST", "/stripe/webhook", csrf=False, body={"id": "evt_collection", "type": "collection.ping", "data": {"object": {}}},
         expect=[status(200, 403)], desc="Unsigned test event of an unknown type. 200 when STRIPE_WEBHOOK_SECRET is unset (local default), 403 when it is set. The webhook is CSRF-exempt.",
         example=(200, None, {})),
])

# 12 ---------------------------------------------------------------------------------------------------------------
ORIGIN = {"Origin": "{{baseUrl}}"}
LOG_LINE = {"lines": [{"level": "warn", "message": "slow request", "tag": "api", "url": "/spaces", "data": {"ms": 1800}}]}
folder("12 Client logs", "Browser log intake. Open endpoint without CSRF; 60 requests per minute. Same-origin browsers only: the request must carry Sec-Fetch-Site (same-origin or none) or an Origin header whose host equals the request host. Scripts that send neither are refused.", [
    case("POST /client-logs accepts a batch from the page's own Origin (204)", "POST", "/client-logs", csrf=False, headers=ORIGIN, body=E.EXAMPLES["client_log"],
         expect=[status(204)], example=(204, None, {})),
    case("POST /client-logs with Sec-Fetch-Site: same-origin (204)", "POST", "/client-logs", csrf=False, headers={"Sec-Fetch-Site": "same-origin"},
         body=LOG_LINE, expect=[status(204)], desc="What a browser sends for a fetch or beacon from the app's own pages."),
    case("POST /client-logs with an invalid payload is 422", "POST", "/client-logs", csrf=False, headers=ORIGIN,
         body={"lines": [{"level": "fatal", "message": ""}]},
         expect=[status(422), js("errors['lines.0.level'][0]", "eq", "The selected lines.0.level is invalid."),
                 js("errors['lines.0.message'][0]", "eq", "The lines.0.message field is required.")],
         example=(422, "invalid_client_log", {})),
    case("POST /client-logs with no lines is 422", "POST", "/client-logs", csrf=False, headers=ORIGIN, body={},
         expect=[status(422), js("errors.lines[0]", "eq", "The lines field is required.")]),
    case("POST /client-logs with more than 20 lines is 422", "POST", "/client-logs", csrf=False, headers=ORIGIN,
         body={"lines": [{"level": "info", "message": "line %d" % i} for i in range(21)]}, expect=[status(422), js("errors.lines", "exists")]),
    case("POST /client-logs with oversized data is 422", "POST", "/client-logs", csrf=False, headers=ORIGIN,
         body={"lines": [{"level": "info", "message": "big", "data": {"blob": "x" * 4100}}]}, expect=[status(422), js("errors['lines.0.data']", "exists")],
         desc="`data` is capped at 4000 bytes of JSON per line."),
    case("POST /client-logs from another origin is 403", "POST", "/client-logs", csrf=False, headers={"Origin": "https://evil.example.com"},
         body=E.EXAMPLES["client_log"], expect=[status(403), js("code", "eq", "error"), js("request_id", "eq", "{{requestId}}")],
         desc="The Origin host must equal the request host.", example=(403, "error_403", {})),
    case("POST /client-logs with Sec-Fetch-Site: cross-site is 403", "POST", "/client-logs", csrf=False,
         headers={"Origin": "{{baseUrl}}", "Sec-Fetch-Site": "cross-site"}, body=LOG_LINE, expect=[status(403)],
         desc="When Sec-Fetch-Site is present it decides, even if Origin looks right."),
    case("POST /client-logs with neither Origin nor Sec-Fetch-Site is 403", "POST", "/client-logs", csrf=False, body=LOG_LINE, expect=[status(403)],
         desc="Plain scripts (curl, newman without an Origin header) are refused on purpose."),
])

# 13 ---------------------------------------------------------------------------------------------------------------
folder("13 Cleanup", "Deletes everything this run created and signs out. Must run last (before the optional folder).", [
    case("DELETE /testimonials/{id}", "DELETE", "/testimonials/{{testimonialId}}", needs=["testimonialId"], referer=BACK_INBOX, expect=[status(302, 303)]),
    case("GET /spaces/{id} shows the testimonial gone", "GET", SPACE_PATH, mode="inertia", needs=["spaceId"],
         expect=[status(200), js("props.testimonials.data", "len", 0), js("props.flash.success", "eq", "Testimonial deleted.")]),
    case("DELETE /spaces/{id} (302 to /spaces)", "DELETE", SPACE_PATH, needs=["spaceId"], referer=BACK_INBOX, expect=[status(302, 303), location(r"/spaces$")],
         example=(302, None, {"Location": "http://localhost:8010/spaces"})),
    case("GET /spaces/{id} after deletion is 404", "GET", SPACE_PATH, needs=["spaceId"], expect=[status(404)], example=(404, "error_404", {})),
    case("GET /{slug} after deletion is 404", "GET", "/{{spaceSlug}}", needs=["spaceSlug"], expect=[status(404)]),
    case("GET /embed/{id}/testimonials.json after deletion is 404", "GET", "/embed/{{spaceId}}/testimonials.json", needs=["spaceId"], expect=[status(404)]),
    case("DELETE /spaces/{id} twice is 404", "DELETE", SPACE_PATH, needs=["spaceId"], expect=[status(404)]),
    case("POST /logout (302 to /)", "POST", "/logout", referer="{{baseUrl}}/dashboard", expect=[status(302), location(r"^https?://[^/]+/?$")],
         example=(302, None, {"Location": "http://localhost:8010/"})),
    case("GET /dashboard after logout redirects to /login", "GET", "/dashboard", mode="html", expect=[status(302), location(LOC_LOGIN)],
         example=(302, None, {"Location": "http://localhost:8010/login"})),
])

# 99 ---------------------------------------------------------------------------------------------------------------
folder("99 Optional (side effects, throttling)", "Skipped unless runOptional=true. Contains requests that change the demo account for good, need extra setup, or lock the rate-limit bucket for up to a minute.", [
    case("Sign in again for the optional requests", "POST", "/login", optional=True, body={"email": "{{email}}", "password": "{{password}}"},
         expect=[status(302), location(LOC_DASHBOARD)], desc="The cleanup folder signed out."),
    case("POST /dashboard/banner/dismiss (permanent)", "POST", "/dashboard/banner/dismiss", optional=True, referer="{{baseUrl}}/dashboard", expect=[status(302, 303)],
         desc="Sets banner_dismissed_at on the demo user. Reset with: php artisan tinker --execute='App\\Models\\User::query()->update([\"banner_dismissed_at\"=>null]);'"),
    case("GET /spaces/{foreign id} is 403 (another owner's space)", "GET", "/spaces/{{foreignSpaceId}}", optional=True, needs=["foreignSpaceId"],
         expect=[status(403), js("code", "eq", "error"), js("request_id", "eq", "{{requestId}}")],
         desc="Needs a verified second user who owns a space. Create one with docs/api/scripts/foreign-space.sh up, put the printed id in foreignSpaceId.", example=(403, "error_403", {})),
    case("PATCH /testimonials/{foreign id}/status is 403", "PATCH", "/testimonials/{{foreignTestimonialId}}/status", optional=True, needs=["foreignSpaceId"],
         body={"status": "hidden"}, expect=[status(403)], desc="Uses foreignTestimonialId printed by the helper script.", example=(403, "error_403", {})),
    case("POST /logout before the throttle test", "POST", "/logout", optional=True, expect=[status(302, 303)]),
    case("POST /client-logs until the limit answers 429", "POST", "/client-logs", optional=True, csrf=False, loop_until=429, headers=ORIGIN, body=E.EXAMPLES["client_log"],
         expect=[status(429), header("Retry-After", r"^\d+$"), js("code", "eq", "error"), js("request_id", "eq", "{{requestId}}")],
         desc="Repeats itself (at most 70 times) until the 60-per-minute limit answers 429.", example=(429, "error_429", {"Retry-After": "46"})),
    case("POST /{slug} is throttled too (shared bucket)", "POST", "/no-such-space-{{runId}}", optional=True, body=SUBMISSION,
         expect=[status(429), header("Retry-After", r"^\d+$")],
         desc="Unnamed throttle:N,1 limiters share one counter per IP, so the full client-logs bucket also blocks submissions. The 429 comes before the 404.",
         example=(429, "error_429", {"Retry-After": "46"})),
    case("POST /login locks out after 5 failures (422, not 429)", "POST", "/login", optional=True, loop_until=("count", 6),
         body={"email": "lockout-{{runId}}@example.com", "password": "wrong"},
         expect=[status(422), js("errors.email[0]", "match", r"^Too many login attempts\. Please try again in \d+ seconds\.$")],
         desc="Repeats itself 6 times with a throwaway email; the sixth answer is the lockout message as a 422 (the first five say the credentials do not match).",
         example=(422, "invalid_login_throttled", {})),
])

FOLDERS = F
