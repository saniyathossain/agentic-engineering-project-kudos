"""Single source of truth for the Kudos HTTP surface (OpenAPI side).

Everything in docs/api/openapi.{yaml,json} comes from this module. The API-client collections come from cases.py,
which reuses EXAMPLES from here, and docs/configuration.md comes from envvars.py. Run `python3 docs/api/build.py`.

Plain dicts only (no third-party imports), so the generator runs on a bare python3.
"""

VERSION = "1.0.0"
REQUEST_ID = "kudos-api-4f2a9c1d"
SPACE_ID = "01m7rzejn7mpxgzr5n4d9kwxp3"
TESTIMONIAL_ID = "01m7rzejt1nczp470ne0vxs9b1"


def ref(kind, name):
    return {"$ref": f"#/components/{kind}/{name}"}


def S(name):
    return ref("schemas", name)


def P(name):
    return ref("parameters", name)


def R(name):
    return ref("responses", name)


def H(name):
    return ref("headers", name)


# --------------------------------------------------------------------------------------------------------------
# Examples shared by OpenAPI and the client collections
# --------------------------------------------------------------------------------------------------------------
GENERIC_ERROR = "Something went wrong. Please try again."
UNAVAILABLE_ERROR = "Temporarily unavailable. Try again shortly."


def err(error=GENERIC_ERROR, code="error", dependency=None, **extra):
    body = {"error": error, "code": code, "dependency": dependency, "request_id": REQUEST_ID}
    body.update(extra)
    return body


def invalid(msg, /, **errors):
    return {"message": msg, "errors": {k: v if isinstance(v, list) else [v] for k, v in errors.items()}}


SHARED_PROPS = {
    "errors": {},
    "name": "Kudos",
    "quote": {"message": "Simplicity is the ultimate sophistication.", "author": "Leonardo da Vinci"},
    "auth": {
        "user": {
            "id": 1,
            "name": "Demo Owner",
            "email": "demo@kudos.test",
            "email_verified_at": "2026-11-19T03:36:32.000000Z",
            "created_at": "2026-11-19T03:36:32.000000Z",
            "updated_at": "2026-11-19T03:36:32.000000Z",
            "banner_dismissed_at": None,
            "stripe_id": None,
            "pm_type": None,
            "pm_last_four": None,
            "trial_ends_at": None,
        }
    },
    "locale": "en",
    "build": {"name": "Kudos", "version": "dev", "commit": "", "env": "local"},
    "resilience": {"first_ms": 4000, "longest_ms": 15000},
    "plan": {"value": "free", "label": "Free"},
    "flash": {"success": None, "error": None},
}
SHARED_PROP_NAMES = ["errors", "name", "quote", "auth", "locale", "build", "resilience", "plan", "flash"]


def page(component, url, props=None, flash=None, guest=False):
    shared = dict(SHARED_PROPS)
    shared["flash"] = {"success": None, "error": None, **(flash or {})}
    if guest:
        shared["auth"] = {"user": None}
        shared["plan"] = None
    return {
        "component": component,
        "props": {**shared, **(props or {})},
        "url": url,
        "version": "41fdb55e5d4f6e59d569e1dd2aac24e7",
        "sharedProps": SHARED_PROP_NAMES,
    }


SPACE_EXAMPLE = {
    "public_id": SPACE_ID,
    "name": "API Docs Probe",
    "slug": "api-docs-probe",
    "logo_url": None,
    "header_title": "Tell us what you think",
    "message": "Say **hi**",
    "collect_rating": True,
    "theme": "brand",
    "fields": {
        "company": {"enabled": True, "required": False},
        "title": {"enabled": False, "required": False},
        "social_link": {"enabled": False, "required": False},
        "photo": {"enabled": False, "required": False},
    },
    "is_accepting": True,
}
TESTIMONIAL_EXAMPLE = {
    "public_id": TESTIMONIAL_ID,
    "rating": 5,
    "body": "Great stuff",
    "respondent_name": "Ada",
    "respondent_email": "ada@example.com",
    "company": "Acme",
    "title": None,
    "social_link": None,
    "photo_url": None,
    "status": "pending",
    "is_favorite": False,
    "submitted_at": "2026-11-19T04:01:18+00:00",
}
PAGE_LINKS = {
    "first": f"http://localhost:8010/spaces/{SPACE_ID}?page=1",
    "last": f"http://localhost:8010/spaces/{SPACE_ID}?page=1",
    "prev": None,
    "next": None,
}
PAGE_META = {"current_page": 1, "from": 1, "last_page": 1, "path": f"http://localhost:8010/spaces/{SPACE_ID}",
             "per_page": 15, "to": 1, "total": 1,
             "links": [{"url": None, "label": "&laquo; Previous", "page": None, "active": False},
                       {"url": f"http://localhost:8010/spaces/{SPACE_ID}?page=1", "label": "1", "page": 1, "active": True},
                       {"url": None, "label": "Next &raquo;", "page": None, "active": False}]}

EXAMPLES = {
    # error shapes
    "error_403": err(),
    "error_404": err(),
    "error_419": err(),
    "error_429": err(),
    "error_500": err(),
    "error_503_database": err(UNAVAILABLE_ERROR, "unavailable", "database"),
    "error_503_billing": err(UNAVAILABLE_ERROR, "unavailable", "billing"),
    "error_503_edge": err(UNAVAILABLE_ERROR, "unavailable", "app", source="edge"),
    "unauthenticated": {"message": "Unauthenticated."},
    # validation
    "invalid_login_credentials": invalid("These credentials do not match our records.", email="These credentials do not match our records."),
    "invalid_login_empty": invalid("The email field is required. (and 1 more error)", email="The email field is required.", password="The password field is required."),
    "invalid_login_throttled": invalid("Too many login attempts. Please try again in 58 seconds.", email="Too many login attempts. Please try again in 58 seconds."),
    "invalid_register": invalid("The email has already been taken. (and 2 more errors)", email="The email has already been taken.",
                                password=["The password field confirmation does not match.", "The password field must be at least 8 characters."]),
    "invalid_forgot": invalid("The email field must be a valid email address.", email="The email field must be a valid email address."),
    "invalid_reset_token": invalid("This password reset token is invalid.", email="This password reset token is invalid."),
    "invalid_confirm_password": invalid("The provided password is incorrect.", password="The provided password is incorrect."),
    "invalid_profile": invalid("The name field is required. (and 1 more error)", name="The name field is required.", email="The email field must be a valid email address."),
    "invalid_current_password": invalid("The password is incorrect.", current_password="The password is incorrect."),
    "invalid_delete_account": invalid("The password is incorrect.", password="The password is incorrect."),
    "invalid_range": invalid("The selected range is invalid.", range="The selected range is invalid."),
    "invalid_space": invalid("The name field must not be greater than 80 characters. (and 1 more error)",
                             name="The name field must not be greater than 80 characters.", theme="The selected theme is invalid."),
    "invalid_space_empty": invalid("The name field is required. (and 3 more errors)", name="The name field is required.",
                                   header_title="The header title field is required.", message="The message field is required.",
                                   theme="The theme field is required."),
    "invalid_inbox_filter": invalid("The selected filter is invalid.", filter="The selected filter is invalid."),
    "invalid_inbox_range": invalid("The to field must be a date after or equal to from.", to="The to field must be a date after or equal to from."),
    "invalid_status": invalid("The selected status is invalid.", status="The selected status is invalid."),
    "invalid_body": invalid("The body field must be at least 3 characters.", body="The body field must be at least 3 characters."),
    "invalid_submission_empty": invalid("The name field is required. (and 4 more errors)", name="The name field is required.",
                                        email="The email field is required.", body="The body field is required.",
                                        consent="The consent field must be accepted.", rating="The rating field is required."),
    "invalid_submission_rating": invalid("The rating field must be between 1 and 5. (and 1 more error)",
                                         rating="The rating field must be between 1 and 5.", title="The title field is prohibited."),
    "invalid_client_log": invalid("The selected lines.0.level is invalid. (and 1 more error)",
                                  **{"lines.0.level": "The selected lines.0.level is invalid.", "lines.0.message": "The lines.0.message field is required."}),
    # health
    "live": {"status": "ok"},
    "ready": {"status": "ok", "checks": [{"name": "database", "up": True, "critical": True},
                                         {"name": "cache", "up": True, "critical": False},
                                         {"name": "storage", "up": True, "critical": False}]},
    "ready_down": {"status": "unavailable", "checks": [{"name": "database", "up": False, "critical": True},
                                                        {"name": "cache", "up": False, "critical": False},
                                                        {"name": "storage", "up": True, "critical": False}]},
    "up": {"status": "up"},
    # pages
    "page_login": page("auth/login", "/login", {"canResetPassword": True, "status": None}, guest=True),
    "page_dashboard": page("dashboard", "/dashboard", {"stats": {
        "total_spaces": 1, "total_testimonials": 1, "unique_respondents": 1, "collected_in_range": 1,
        "plan": {"value": "free", "label": "Free"},
        "usage": {"spaces_used": 1, "max_spaces": 1, "max_testimonials_per_space": 10},
        "range": 30,
        "series": [{"date": "2026-11-18", "count": 0}, {"date": "2026-11-19", "count": 1}],
        "show_upgrade_banner": True}}),
    "page_spaces_index": page("spaces/index", "/spaces", {"spaces": [{**SPACE_EXAMPLE, "testimonials_count": 1}], "canCreate": False}),
    "page_spaces_form_new": page("spaces/form", "/spaces/create", {
        "space": None, "themes": [{"value": "light", "label": "Light"}, {"value": "dark", "label": "Dark"}, {"value": "brand", "label": "Brand"}],
        "optionalFields": ["company", "title", "social_link", "photo"]}),
    "page_space_show": page("spaces/show", f"/spaces/{SPACE_ID}", {
        "space": SPACE_EXAMPLE,
        "testimonials": {"data": [TESTIMONIAL_EXAMPLE], "links": PAGE_LINKS, "meta": PAGE_META},
        "filter": "all", "range": {"from": None, "to": None},
        "counts": {"all": 1, "favorite": 0, "pending": 1, "published": 0, "hidden": 0},
        "publicUrl": "http://localhost:8010/api-docs-probe"}, flash={"success": "Space created. Share its link to collect testimonials."}),
    "page_collect": page("public/collect", "/api-docs-probe", {"space": SPACE_EXAMPLE, "accepting": True}, guest=True),
    "page_collect_closed": page("public/collect", "/api-docs-probe", {"space": SPACE_EXAMPLE, "accepting": False}, guest=True),
    "page_embed": page("embed/wall", f"/embed/{SPACE_ID}", {
        "space": {"public_id": SPACE_ID, "name": "API Docs Probe", "theme": "brand", "logo_url": None},
        "testimonials": []}, guest=True),
    "page_billing": page("billing/show", "/billing", {"overview": {
        "plan": {"value": "free", "label": "Free"}, "spaces_used": 1, "spaces_max": 1, "testimonials_per_space_max": 10,
        "subscription_status": "none", "can_manage_billing": False, "billing_configured": False}}),
    "page_profile": page("settings/profile", "/settings/profile", {"mustVerifyEmail": True, "status": None}),
    "page_password": page("settings/password", "/settings/password", {"mustVerifyEmail": True, "status": None}),
    "page_confirm_password": page("auth/confirm-password", "/confirm-password"),
    "embed_json": {
        "data": [{
            "public_id": TESTIMONIAL_ID, "rating": 5, "body": "Great stuff", "respondent_name": "Ada", "company": "Acme",
            "title": None, "social_link": None, "photo_url": None, "submitted_at": "2026-11-19T04:01:18+00:00"}],
        "space": {"public_id": SPACE_ID, "name": "API Docs Probe", "theme": "brand", "logo_url": None}},
    "client_log": {
        "lines": [{"level": "warn", "message": "Cannot read properties of undefined", "tag": "inbox", "url": "/spaces/" + SPACE_ID,
                   "data": {"component": "TestimonialCard"}}],
        "device": {"timezone": "UTC", "screen": "1440x900", "language": "en-US"},
        "page_view_id": "pv_8f2c1d"},
}


# --------------------------------------------------------------------------------------------------------------
# Components
# --------------------------------------------------------------------------------------------------------------
def obj(props, required=None, description=None, additional=None):
    s = {"type": "object", "properties": props}
    if required:
        s["required"] = required
    if description:
        s["description"] = description
    if additional is not None:
        s["additionalProperties"] = additional
    return s


def string(description=None, **kw):
    s = {"type": "string"}
    if description:
        s["description"] = description
    s.update(kw)
    return s


def nullable(schema):
    return {"oneOf": [schema, {"type": "null"}]}


def enum(values, description=None):
    s = {"type": "string", "enum": values}
    if description:
        s["description"] = description
    return s


def array(items, **kw):
    return {"type": "array", "items": items, **kw}


FIELD_ENTRY = obj({"enabled": {"type": "boolean"}, "required": {"type": "boolean"}}, ["enabled", "required"])

SCHEMAS = {
    "ErrorResponse": obj({
        "error": string("Human-readable summary. Generic by design; branch on the HTTP status and `code`, not on this text."),
        "code": enum(["error", "unavailable"], "`unavailable` for a failed dependency (503), `error` for everything else."),
        "dependency": nullable(enum(["database", "billing", "app"], "Which dependency failed; null unless the status is 503. `app` only in the nginx edge body.")),
        "request_id": string("Same value as the X-Request-ID response header. Quote it when reporting a problem."),
    }, ["error", "code", "dependency", "request_id"],
        "Error body for every failure the framework does not already shape, returned when the client sends `Accept: application/json` (and no X-Inertia header)."),
    "EdgeErrorResponse": {
        "allOf": [S("ErrorResponse"), obj({
            "dependency": {"const": "app"},
            "source": {"const": "edge", "description": "Present only when nginx, not the Laravel app, produced the response."},
        }, ["source"])],
        "description": "503 produced by the edge nginx when the app does not answer (502, 503 and 504 from php-fpm all become this).",
    },
    "ValidationError": obj({
        "message": string("First validation message, plus `(and N more errors)` when there are several."),
        "errors": {"type": "object", "additionalProperties": array(string()),
                   "description": "Field name (dotted for nested fields) mapped to its messages."},
    }, ["message", "errors"], "Laravel validation failure, returned as 422 when the client sends `Accept: application/json`."),
    "Unauthenticated": obj({"message": {"const": "Unauthenticated."}}, ["message"],
                           "401 body from the auth middleware. This one is Laravel's own shape, not ErrorResponse."),
    "Plan": enum(["free", "pro"]),
    "PlanLabel": obj({"value": S("Plan"), "label": string()}, ["value", "label"]),
    "SpaceTheme": enum(["light", "dark", "brand"]),
    "TestimonialStatus": enum(["pending", "published", "hidden"]),
    "InboxFilter": enum(["all", "favorite", "pending", "published", "hidden"]),
    "FieldEntry": FIELD_ENTRY,
    "SpaceFields": obj({"company": S("FieldEntry"), "title": S("FieldEntry"), "social_link": S("FieldEntry"), "photo": S("FieldEntry")},
                       description="Per-field configuration for the optional fields. Name and email are always required and are not listed."),
    "Space": obj({
        "public_id": string("ULID, lowercase.", pattern="^[0-9a-z]{26}$"),
        "name": string(),
        "slug": string("Public collection page path segment.", pattern="^[a-z0-9-]+$"),
        "logo_url": nullable(string(format="uri")),
        "header_title": string(),
        "message": string("Markdown shown above the form."),
        "collect_rating": {"type": "boolean"},
        "theme": S("SpaceTheme"),
        "fields": S("SpaceFields"),
        "is_accepting": {"type": "boolean"},
        "testimonials_count": {"type": "integer", "description": "Only on the spaces list."},
    }, ["public_id", "name", "slug", "header_title", "message", "collect_rating", "theme", "fields", "is_accepting"]),
    "OwnerTestimonial": obj({
        "public_id": string(pattern="^[0-9a-z]{26}$"),
        "rating": nullable({"type": "integer", "minimum": 1, "maximum": 5}),
        "body": string(),
        "respondent_name": string(),
        "respondent_email": string(format="email", description="Owner-only. Never present in embed or public output."),
        "company": nullable(string()),
        "title": nullable(string()),
        "social_link": nullable(string(format="uri")),
        "photo_url": nullable(string(format="uri")),
        "status": S("TestimonialStatus"),
        "is_favorite": {"type": "boolean"},
        "submitted_at": string(format="date-time", description="ISO 8601, UTC."),
    }, ["public_id", "body", "respondent_name", "respondent_email", "status", "is_favorite", "submitted_at"]),
    "EmbedTestimonial": obj({
        "public_id": string(pattern="^[0-9a-z]{26}$"),
        "rating": nullable({"type": "integer", "minimum": 1, "maximum": 5}),
        "body": string("Text with HTML tags already stripped on submit."),
        "respondent_name": string(),
        "company": nullable(string()),
        "title": nullable(string()),
        "social_link": nullable(string(format="uri")),
        "photo_url": nullable(string(format="uri")),
        "submitted_at": string(format="date-time"),
    }, ["public_id", "body", "respondent_name", "submitted_at"], "Public view of a published testimonial. No email field exists here."),
    "EmbedSpace": obj({"public_id": string(), "name": string(), "theme": S("SpaceTheme"), "logo_url": nullable(string(format="uri"))},
                      ["public_id", "name", "theme"]),
    "EmbedWall": obj({"data": array(S("EmbedTestimonial")), "space": S("EmbedSpace")}, ["data", "space"],
                     "Published testimonials of one space, newest first as the app orders them."),
    "PaginationLinks": obj({"first": nullable(string()), "last": nullable(string()), "prev": nullable(string()), "next": nullable(string())}),
    "PaginationMeta": obj({
        "current_page": {"type": "integer"}, "from": nullable({"type": "integer"}), "last_page": {"type": "integer"},
        "links": array(obj({"url": nullable(string()), "label": string(), "page": nullable({"type": "integer"}), "active": {"type": "boolean"}})),
        "path": string(), "per_page": {"type": "integer", "const": 15}, "to": nullable({"type": "integer"}), "total": {"type": "integer"},
    }),
    "DashboardStats": obj({
        "total_spaces": {"type": "integer"}, "total_testimonials": {"type": "integer"}, "unique_respondents": {"type": "integer"},
        "collected_in_range": {"type": "integer"}, "plan": S("PlanLabel"),
        "usage": obj({"spaces_used": {"type": "integer"}, "max_spaces": nullable({"type": "integer"}),
                      "max_testimonials_per_space": nullable({"type": "integer"})}),
        "range": {"type": "integer", "enum": [7, 30, 90]},
        "series": array(obj({"date": string(format="date"), "count": {"type": "integer"}})),
        "show_upgrade_banner": {"type": "boolean"},
    }),
    "BillingOverview": obj({
        "plan": S("PlanLabel"), "spaces_used": {"type": "integer"}, "spaces_max": nullable({"type": "integer"}),
        "testimonials_per_space_max": nullable({"type": "integer"}),
        "subscription_status": string("`none` when the user never subscribed; otherwise the Cashier subscription status."),
        "can_manage_billing": {"type": "boolean"}, "billing_configured": {"type": "boolean"},
    }),
    "Flash": obj({"success": nullable(string()), "error": nullable(string())},
                 description="One-shot messages from the previous redirect. Read once, then gone."),
    "SharedProps": obj({
        "errors": {"type": "object", "additionalProperties": string(), "description": "Validation errors flashed by the previous redirect (first message per field)."},
        "name": string("App name."), "quote": obj({"message": string(), "author": string()}),
        "auth": obj({"user": nullable({"type": "object", "additionalProperties": True,
                                       "description": "The User model: id, name, email, email_verified_at, created_at, updated_at, banner_dismissed_at, stripe_id, pm_type, pm_last_four, trial_ends_at."})}),
        "locale": string(), "build": obj({"name": string(), "version": string("APP_VERSION."), "commit": string("APP_COMMIT, empty in dev."), "env": string("Application environment name.")}),
        "resilience": obj({"first_ms": {"type": "integer"}, "longest_ms": {"type": "integer"}}),
        "plan": nullable(S("PlanLabel")), "flash": S("Flash"),
    }, ["errors", "name", "auth", "flash"], "Props the server adds to every Inertia page. Each page adds its own props next to these.", additional=True),
    "InertiaErrorPage": obj({
        "component": {"const": "errors/error"},
        "props": obj({
            "status": {"type": "integer", "description": "The real HTTP status of the response."},
            "copyKey": enum(["403", "404", "419", "429", "4xx", "500"], "Which wording the React error page shows."),
            "retryAfter": nullable({"type": "integer"}), "requestId": string(),
        }, ["status", "copyKey", "requestId"]),
        "url": string(), "version": string("Empty on error pages."),
    }, ["component", "props", "url"],
        "What an Inertia request (X-Inertia: true) receives for a 403, 404, 419, 429, other 4xx or 500: a page object for the component `errors/error`, with the real status code on the response. Unlike normal pages it carries only its own props, no shared props."),
    "InertiaPage": obj({
        "component": string("Name of the React page component, for example `spaces/show`."),
        "props": {"$ref": "#/components/schemas/SharedProps"},
        "url": string("Path and query of the page."),
        "version": string("Asset version. Send it back as X-Inertia-Version on GET visits."),
        "sharedProps": array(string()),
    }, ["component", "props", "url", "version"], "Page object that every Inertia route returns when the request carries `X-Inertia: true`."),
    "LoginRequest": obj({
        "email": string(format="email"), "password": string(), "remember": {"type": "boolean", "description": "Keep the session after the browser closes."},
    }, ["email", "password"]),
    "RegisterRequest": obj({
        "name": string(maxLength=255), "email": string(format="email", maxLength=255, description="Lowercase, unique among users."),
        "password": string(minLength=8, description="Laravel default password rules (min 8)."), "password_confirmation": string(),
    }, ["name", "email", "password", "password_confirmation"]),
    "ForgotPasswordRequest": obj({"email": string(format="email")}, ["email"]),
    "ResetPasswordRequest": obj({
        "token": string(), "email": string(format="email"), "password": string(minLength=8), "password_confirmation": string(),
    }, ["token", "email", "password", "password_confirmation"]),
    "ConfirmPasswordRequest": obj({"password": string()}, ["password"]),
    "ProfileUpdateRequest": obj({"name": string(maxLength=255), "email": string(format="email", maxLength=255, description="Lowercase. Changing it clears email verification.")},
                                ["name", "email"]),
    "PasswordUpdateRequest": obj({"current_password": string(), "password": string(minLength=8), "password_confirmation": string()},
                                 ["current_password", "password", "password_confirmation"]),
    "DeleteAccountRequest": obj({"password": string("Current password.")}, ["password"]),
    "SpaceRequest": obj({
        "name": string(maxLength=80), "header_title": string(maxLength=120), "message": string(maxLength=1000, description="Markdown."),
        "collect_rating": {"type": "boolean"}, "theme": S("SpaceTheme"),
        "is_accepting": {"type": "boolean", "description": "Turn the public form on or off."},
        "logo": string("PNG, JPG, JPEG or WEBP, at most 2 MB. Only valid in multipart bodies. Send `_method=PUT` in a multipart POST to update.",
                       format="binary"),
        "fields": S("SpaceFields"),
    }, ["name", "header_title", "message", "theme"],
        "Create or update a space. In multipart or form bodies use bracket names such as `fields[company][enabled]=1`. The slug is generated from the name and stays the same on update, so shared links keep working. A body replaces the whole configuration: an omitted `collect_rating` becomes false, an omitted `is_accepting` becomes true, an omitted entry in `fields` becomes disabled and not required."),
    "SubmissionRequest": obj({
        "name": string(maxLength=100), "email": string(format="email", maxLength=190, description="Validated with the RFC rule. Stored, shown to the owner only."),
        "body": string(minLength=3, maxLength=2000, description="HTML tags are stripped before saving."),
        "consent": {"type": "boolean", "const": True, "description": "Must be accepted (true, 1, yes, on)."},
        "rating": {"type": "integer", "minimum": 1, "maximum": 5, "description": "Required when the space collects ratings; prohibited (422) when it does not."},
        "company": string(maxLength=100, description="Allowed only when enabled on the space; required when marked required."),
        "title": string(maxLength=100, description="Same rule as company."),
        "social_link": string(format="uri", maxLength=255, description="http or https URL. Same enabled/required rule."),
        "photo": string("PNG, JPG, JPEG or WEBP, at most 2 MB. Multipart only. Same enabled/required rule.", format="binary"),
    }, ["name", "email", "body", "consent"],
        "Respondent submission. Fields the space has not enabled are rejected with `The <field> field is prohibited.`"),
    "StatusRequest": obj({"status": S("TestimonialStatus")}, ["status"]),
    "EditBodyRequest": obj({"body": string(minLength=3, maxLength=2000, description="HTML tags are stripped.")}, ["body"]),
    "ClientLogRequest": obj({
        "lines": array(obj({
            "level": enum(["debug", "info", "warn", "error"]), "message": string(maxLength=500),
            "tag": nullable(string(maxLength=60)), "url": nullable(string(maxLength=300)),
            "data": nullable({"type": "object", "additionalProperties": True}),
        }, ["level", "message"]), minItems=1, maxItems=20),
        "device": nullable({"type": "object", "additionalProperties": nullable(string(maxLength=100))}),
        "page_view_id": nullable(string(maxLength=40)),
    }, ["lines"], "Batch of browser log lines."),
    "HealthLive": obj({"status": {"const": "ok"}}, ["status"]),
    "HealthCheck": obj({"name": enum(["database", "cache", "storage"]), "up": {"type": "boolean"}, "critical": {"type": "boolean"}},
                       ["name", "up", "critical"]),
    "HealthReady": obj({"status": enum(["ok", "unavailable"]), "checks": array(S("HealthCheck"))}, ["status", "checks"]),
    "HtmlDocument": {"type": "string", "description": "HTML document. Inertia pages embed their page object in a script element with the attribute data-page=\"app\" and type application/json."},
    "DashboardProps": obj({"stats": S("DashboardStats")}, ["stats"]),
    "SpacesIndexProps": obj({"spaces": array(S("Space")), "canCreate": {"type": "boolean"}}, ["spaces", "canCreate"]),
    "SpaceShowProps": obj({
        "space": S("Space"),
        "testimonials": obj({"data": array(S("OwnerTestimonial")), "links": S("PaginationLinks"), "meta": S("PaginationMeta")}, ["data", "links", "meta"]),
        "filter": S("InboxFilter"), "range": obj({"from": nullable(string(format="date")), "to": nullable(string(format="date"))}),
        "counts": obj({k: {"type": "integer"} for k in ["all", "favorite", "pending", "published", "hidden"]}),
        "publicUrl": string(format="uri"),
    }, ["space", "testimonials", "filter", "range", "counts", "publicUrl"]),
    "BillingProps": obj({"overview": S("BillingOverview")}, ["overview"]),
    "CollectProps": obj({"space": S("Space"), "accepting": {"type": "boolean", "description": "False when the owner closed the form or the Free plan's 10-testimonial cap is reached."}}, ["space", "accepting"]),
    "EmbedWallProps": obj({"space": S("EmbedSpace"), "testimonials": array(S("EmbedTestimonial"))}, ["space", "testimonials"]),
}

PARAMETERS = {
    "SpaceId": {"name": "spaceId", "in": "path", "required": True, "schema": string(pattern="^[0-9a-z]{26}$"),
                "description": "Space public ID (lowercase ULID). Numeric database ids are never used.", "example": SPACE_ID},
    "TestimonialId": {"name": "testimonialId", "in": "path", "required": True, "schema": string(pattern="^[0-9a-z]{26}$"),
                      "description": "Testimonial public ID (lowercase ULID).", "example": TESTIMONIAL_ID},
    "Slug": {"name": "slug", "in": "path", "required": True,
             "schema": string(pattern="^[a-z0-9-]+$", description="Lowercase letters, digits and hyphens. Reserved names (login, register, dashboard, settings, embed, billing, spaces, stripe, up, livez, readyz, healthz, status, outage, client-logs, forgot-password, reset-password, verify-email, confirm-password, logout, email, testimonials, build, storage) never match this route."),
             "description": "Slug of the space.", "example": "api-docs-probe"},
    "XInertia": {"name": "X-Inertia", "in": "header", "required": False, "schema": {"type": "string", "const": "true"},
                 "description": "Send `true` to receive the page object as JSON instead of the HTML document. GET requests with this header must also send X-Inertia-Version."},
    "XInertiaVersion": {"name": "X-Inertia-Version", "in": "header", "required": False, "schema": string(),
                        "description": "Asset version from the last page object (also in the HTML's `data-page` script). A mismatch on GET returns 409 with X-Inertia-Location.",
                        "example": "41fdb55e5d4f6e59d569e1dd2aac24e7"},
    "XRequestId": {"name": "X-Request-ID", "in": "header", "required": False, "schema": string(pattern="^[A-Za-z0-9._-]{8,64}$"),
                   "description": "Your own correlation id. Used as the request id when it matches the pattern, otherwise the server generates one. It is echoed in the response.",
                   "example": REQUEST_ID},
    "XXsrfToken": {"name": "X-XSRF-TOKEN", "in": "header", "required": False, "schema": string(),
                   "description": "URL-decoded value of the XSRF-TOKEN cookie. Required on every state-changing request except /client-logs and /stripe/webhook; missing or wrong gives 419."},
    "Referer": {"name": "Referer", "in": "header", "required": False, "schema": string(format="uri"),
                "description": "Where `back()` redirects go. Without it the app redirects to the last page this session visited, which is rarely what a script wants."},
    "InboxFilterQuery": {"name": "filter", "in": "query", "schema": S("InboxFilter"), "description": "Status filter. Default `all`."},
    "InboxFrom": {"name": "from", "in": "query", "schema": string(format="date", description="Y-m-d"), "description": "Earliest submission date, inclusive."},
    "InboxTo": {"name": "to", "in": "query", "schema": string(format="date", description="Y-m-d"),
                "description": "Latest submission date. Must be on or after `from`."},
    "InboxPage": {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}, "description": "Page number, 15 testimonials per page."},
    "DashboardRange": {"name": "range", "in": "query", "schema": {"type": "integer", "enum": [7, 30, 90]}, "description": "Days in the chart. Default 30."},
    "VerifyId": {"name": "id", "in": "path", "required": True, "schema": {"type": "integer"}, "description": "User id from the signed link in the verification email."},
    "VerifyHash": {"name": "hash", "in": "path", "required": True, "schema": string(), "description": "SHA-1 of the user's email, from the signed link."},
    "ResetToken": {"name": "token", "in": "path", "required": True, "schema": string(), "description": "Token from the reset email."},
    "ResetEmail": {"name": "email", "in": "query", "schema": string(format="email"), "description": "Pre-fills the email field of the reset form."},
    "SessionIdQuery": {"name": "session_id", "in": "query", "schema": string(), "description": "Stripe Checkout session id (`cs_...`). Stripe appends it to the success URL."},
}

HEADERS = {
    "XRequestId": {"description": "Request id: the caller's valid X-Request-ID, else one generated by nginx or the app. Present on every response, errors included.",
                   "schema": string(), "example": REQUEST_ID},
    "RetryAfter": {"description": "Seconds to wait before retrying.", "schema": {"type": "integer"}, "example": 5},
    "XInertiaLocation": {"description": "Absolute URL the Inertia client must load with a full page visit.", "schema": string(format="uri"),
                         "example": "http://localhost:8010/spaces/" + SPACE_ID},
    "XInertia": {"description": "`true` on Inertia JSON page responses.", "schema": {"type": "string", "const": "true"}},
    "Location": {"description": "Redirect target. Absolute URL.", "schema": string(format="uri"), "example": "http://localhost:8010/dashboard"},
    "CacheControlNoStore": {"description": "`no-store, private` on every error body so intermediaries never cache a failure.",
                            "schema": string(), "example": "no-store, private"},
    "ContentSecurityPolicyEmbed": {"description": "`frame-ancestors *`: embed routes may be framed by any site. X-Frame-Options is removed on these routes.",
                                   "schema": {"type": "string", "const": "frame-ancestors *"}},
}

ERR_HEADERS = {"X-Request-ID": H("XRequestId"), "Cache-Control": H("CacheControlNoStore")}


def inertia_error_example(status, copy_key=None, retry=None, url="/spaces/01zzzzzzzzzzzzzzzzzzzzzzzz"):
    return {"component": "errors/error", "props": {"status": status, "copyKey": copy_key or str(status), "retryAfter": retry, "requestId": REQUEST_ID},
            "url": url, "version": ""}


EXAMPLES.update({
    "inertia_error_404": inertia_error_example(404),
    "inertia_error_403": inertia_error_example(403, url=f"/spaces/{SPACE_ID}"),
    "inertia_error_419": inertia_error_example(419, url="/spaces"),
    "inertia_error_429": inertia_error_example(429, retry=46, url="/api-docs-probe"),
    "inertia_error_500": inertia_error_example(500, url="/dashboard"),
})


def error_content(schema_name, status, examples):
    """Error body for a plain JSON client and for an Inertia client, same status."""
    ex = {k: {"summary": s, "value": EXAMPLES[v]} for k, (s, v) in examples.items()}
    ex["inertia"] = {"summary": "Same failure for an Inertia request (X-Inertia: true)", "value": EXAMPLES[f"inertia_error_{status}"]}
    return {"application/json": {"schema": {"oneOf": [S(schema_name), S("InertiaErrorPage")]}, "examples": ex},
            "text/html": {"schema": S("HtmlDocument")}}


def json_content(schema, examples):
    return {"application/json": {"schema": schema, "examples": {k: {"summary": s, "value": EXAMPLES[v]} for k, (s, v) in examples.items()}}}


RESPONSES = {
    "LoginRedirect": {
        "description": "Browser or Inertia request without a session: 302 to `/login`. The target is remembered and used after sign-in.",
        "headers": {"Location": H("Location"), "X-Request-ID": H("XRequestId")},
        "content": {"text/html": {"schema": S("HtmlDocument")}},
    },
    "GuestOnlyRedirect": {
        "description": "Already signed in: the `guest` middleware sends the visitor to `/dashboard`.",
        "headers": {"Location": H("Location"), "X-Request-ID": H("XRequestId")},
        "content": {"text/html": {"schema": S("HtmlDocument")}},
    },
    "Redirect": {
        "description": "Redirect. Inertia clients get 303 instead of 302 after PUT, PATCH and DELETE so the browser follows with GET.",
        "headers": {"Location": H("Location"), "X-Request-ID": H("XRequestId")},
        "content": {"text/html": {"schema": S("HtmlDocument")}},
    },
    "Unauthenticated": {
        "description": "No valid session and the request sent `Accept: application/json`.",
        "headers": {"X-Request-ID": H("XRequestId")},
        "content": json_content(S("Unauthenticated"), {"unauthenticated": ("Not signed in", "unauthenticated")}),
    },
    "Forbidden": {
        "description": "Authenticated, but the space or testimonial belongs to another owner (policy `manage`); or a bad signature on a signed URL; or a /client-logs request that is not same-origin. Plain JSON clients get ErrorResponse, Inertia clients an `errors/error` page object, browsers the HTML error page.",
        "headers": ERR_HEADERS,
        "content": error_content("ErrorResponse", 403, {"forbidden": ("Policy refused", "error_403")}),
    },
    "NotFound": {
        "description": "No such space, slug, testimonial or route. Plain JSON clients get ErrorResponse, Inertia clients (even on GET) an `errors/error` page object with status 404, browsers the HTML 404 page.",
        "headers": ERR_HEADERS,
        "content": error_content("ErrorResponse", 404, {"missing": ("Unknown public id", "error_404")}),
    },
    "InertiaConflict": {
        "description": "Inertia location trick: 409 with an empty body and X-Inertia-Location, meaning \"load this URL as a normal page\". Used when (1) a GET visit sends a stale or missing X-Inertia-Version (after authentication has passed), (2) a dependency outage (503) hits an Inertia request: the full-page load then shows the database-free outage page (for an unsafe method the location is `/`), and (3) billing checkout and portal send the browser to Stripe.",
        "headers": {"X-Inertia-Location": H("XInertiaLocation"), "X-Request-ID": H("XRequestId"), "Cache-Control": H("CacheControlNoStore")},
    },
    "CsrfMismatch": {
        "description": "Missing, expired or wrong CSRF token. Fetch any page to get a fresh XSRF-TOKEN cookie and send it as X-XSRF-TOKEN. Same body variants as 403.",
        "headers": ERR_HEADERS,
        "content": error_content("ErrorResponse", 419, {"csrf": ("Token mismatch", "error_419")}),
    },
    "ValidationFailed": {
        "description": "Validation failed. With `Accept: application/json` (no X-Inertia) the body is the Laravel shape below. A browser or Inertia client instead gets a 302/303 back to the previous page with the messages flashed into `props.errors`.",
        "headers": {"X-Request-ID": H("XRequestId")},
        "content": {"application/json": {"schema": S("ValidationError")}},
    },
    "TooManyRequests": {
        "description": "Rate limit reached. Retry-After holds the seconds to wait. Counters of unnamed `throttle:N,1` routes (`/{slug}` POST, /client-logs, /email/verification-notification, /verify-email/...) share one bucket per user (signed in) or per IP (anonymous), so traffic to one of them can lock out the others. Same body variants as 403.",
        "headers": {"Retry-After": H("RetryAfter"), **ERR_HEADERS},
        "content": error_content("ErrorResponse", 429, {"throttled": ("Throttled", "error_429")}),
    },
    "ServerError": {
        "description": "Unexpected bug. Logged with the request id; the client sees a generic message. With APP_DEBUG=true Laravel's debug output replaces the friendly body for non-Inertia clients. Same body variants as 403.",
        "headers": ERR_HEADERS,
        "content": error_content("ErrorResponse", 500, {"bug": ("Unexpected error", "error_500")}),
    },
    "Unavailable": {
        "description": "A dependency is down (database, Stripe, or the whole app behind nginx). Always carries Retry-After (5 seconds by default). Database and billing failures come from the app; `source: edge` bodies come from nginx. HTML clients get the friendly page, or the static outage page when the edge answered. Inertia requests do not get this status: they get 409 + X-Inertia-Location (see InertiaConflict) so the outage page loads in full.",
        "headers": {"Retry-After": H("RetryAfter"), **ERR_HEADERS, "X-Edge": {"description": "`nginx` when the edge answered.", "schema": string(), "example": "nginx"}},
        "content": {**json_content({"oneOf": [S("ErrorResponse"), S("EdgeErrorResponse")]},
                                   {"database": ("Database down", "error_503_database"), "billing": ("Stripe retries exhausted or not configured", "error_503_billing"),
                                    "edge": ("nginx, app not answering", "error_503_edge")}),
                    "text/html": {"schema": S("HtmlDocument")}},
    },
    "NoContent": {"description": "Accepted. Empty body.", "headers": {"X-Request-ID": H("XRequestId")}},
}

TAGS = [
    {"name": "Health", "description": "Probes. Outside the web middleware group: no session, no cookies, no CSRF, no access log."},
    {"name": "Observability", "description": "Browser error and warning intake."},
    {"name": "Public collection", "description": "What a respondent sees. No account needed."},
    {"name": "Embed", "description": "Published testimonials for the iframe wall and for your own pages. Public, frameable, never exposes emails."},
    {"name": "Auth", "description": "Register, sign in and out, password reset, email verification, password confirmation."},
    {"name": "Settings", "description": "Owner profile and password."},
    {"name": "Dashboard", "description": "Totals, plan usage, chart, upgrade banner."},
    {"name": "Spaces", "description": "Owner spaces and the per-space inbox."},
    {"name": "Testimonials", "description": "Inbox actions on one testimonial."},
    {"name": "Billing", "description": "Free vs Pro, Stripe Checkout, success check, billing portal."},
    {"name": "Stripe", "description": "Routes registered by Laravel Cashier."},
    {"name": "Framework", "description": "Routes that exist but are not product API: home page, Laravel health check, local storage, dev-only Inertia devtools."},
]

# --------------------------------------------------------------------------------------------------------------
# Operations
# --------------------------------------------------------------------------------------------------------------
INERTIA_PARAMS = [P("XInertia"), P("XInertiaVersion"), P("XRequestId")]
WRITE_PARAMS = [P("XXsrfToken"), P("XRequestId"), P("Referer")]


def page_ok(component, example, props=None, desc="Page. The HTML document by default; the Inertia page object as JSON with `X-Inertia: true`."):
    json_schema = {"allOf": [S("InertiaPage"), obj({"props": props})]} if props else S("InertiaPage")
    return {
        "description": desc,
        "headers": {"X-Request-ID": H("XRequestId"), "X-Inertia": H("XInertia")},
        "content": {
            "text/html": {"schema": S("HtmlDocument")},
            "application/json": {"schema": json_schema, "examples": {"page": {"summary": f"Inertia page `{component}`", "value": EXAMPLES[example]}}},
        },
    }


def redirect(text, location="http://localhost:8010/dashboard"):
    return {"$ref": "#/components/responses/Redirect", "description": text}


OPS = []


def op(method, path, id, tag, summary, description, auth="session", params=(), body=None, responses=None, throttle=None,
       csrf=None, inertia=False, extra=()):
    OPS.append(dict(method=method, path=path, id=id, tag=tag, summary=summary, description=description, auth=auth, params=list(params),
                    body=body, responses=responses or {}, throttle=throttle, csrf=csrf, inertia=inertia, extra=list(extra)))


def form_body(schema, example, required=True, multipart=False):
    content = {
        "application/json": {"schema": S(schema), "example": example},
        "application/x-www-form-urlencoded": {"schema": S(schema)},
    }
    if multipart:
        content["multipart/form-data"] = {"schema": S(schema)}
    return {"required": required, "content": content}


# ---- health ----------------------------------------------------------------------------------------------
op("get", "/livez", "livez", "Health", "Liveness probe",
   "Answers 200 as long as PHP runs. No database read, no session.", auth="public",
   params=[P("XRequestId")],
   responses={"200": {"description": "Alive.", "headers": {"Cache-Control": {"description": "`no-store, private`", "schema": string()}, "X-Request-ID": H("XRequestId")},
                      "content": json_content(S("HealthLive"), {"ok": ("Alive", "live")})}})
op("get", "/readyz", "readyz", "Health", "Readiness probe",
   "Checks the database (critical), the cache and the public storage disk (both informational). 503 only when a critical check fails. Used by the edge and orchestrators.",
   auth="public", params=[P("XRequestId")],
   responses={"200": {"description": "Ready. A non-critical check can still be `up: false` here.", "headers": {"X-Request-ID": H("XRequestId")},
                      "content": json_content(S("HealthReady"), {"ok": ("All up", "ready")})},
              "503": {"description": "A critical dependency is down.", "headers": {"Retry-After": H("RetryAfter"), "X-Request-ID": H("XRequestId")},
                      "content": json_content(S("HealthReady"), {"down": ("Database down", "ready_down")})}})
op("get", "/up", "up", "Framework", "Laravel health check",
   "Framework route registered by `withRouting(health: '/up')`. Returns the app's own status and fires the DiagnosingHealth event. Prefer /livez and /readyz.",
   auth="public", responses={"200": {"description": "Up.", "content": {"application/json": {"schema": obj({"status": {"const": "up"}}), "example": EXAMPLES["up"]}}}})

# ---- observability ---------------------------------------------------------------------------------------
op("post", "/client-logs", "recordClientLogs", "Observability", "Send browser log lines",
   "Used by `resources/js/lib/logger.ts` (often through `navigator.sendBeacon`). Open endpoint: no session, no CSRF (a beacon cannot carry the token), so it only takes same-origin browser requests. If a `Sec-Fetch-Site` header is present it must be `same-origin` or `none`; otherwise an `Origin` header is required and its host must equal the request host. A request with neither header (a plain script) is refused with 403. Authorization is checked before validation, so a refused request never gets a 422. Limits: `throttle:60,1` in the app (shared bucket), and at the edge 5 requests per second with a burst of 20 and a 16 KB body cap. At most 20 lines per request, each `data` object at most 4000 bytes of JSON. Never put secrets or full bodies in `data`; the logger redacts keys such as password and token.",
   auth="public", csrf=False, throttle="60 requests per minute (shared bucket, see TooManyRequests)", params=[P("XRequestId")],
   body=form_body("ClientLogRequest", EXAMPLES["client_log"]),
   responses={"204": R("NoContent"), "403": R("Forbidden"), "422": R("ValidationFailed")},
   extra=[("422", {"invalid": ("Bad level and empty message", "invalid_client_log")})])

# ---- public collection page ------------------------------------------------------------------------------
op("get", "/{slug}", "showCollectionPage", "Public collection", "Collection page for a space",
   "The page a respondent opens. `props.accepting` is false when the owner switched the form off, or when the owner is on Free and the space already holds 10 testimonials; the form should then be hidden. Unknown or reserved slugs give 404. Public: no login.",
   auth="public", params=[P("Slug"), *INERTIA_PARAMS], inertia=True,
   responses={"200": page_ok("public/collect", "page_collect", S("CollectProps"))},
   extra=[("200", {"closed": ("Not accepting", "page_collect_closed")})])
op("post", "/{slug}", "submitTestimonial", "Public collection", "Submit a testimonial",
   "Creates a testimonial with status `pending`. Public, but the CSRF cookie flow still applies (any anonymous page view sets it). Limit: `throttle:20,1`, enforced before validation, so invalid posts count too. Optional fields are validated against the space's field configuration. HTML tags in text fields are stripped. Photo upload needs `multipart/form-data`.\n\nFree plan: a space accepts at most 10 testimonials while its owner has no subscription. Past that, or when the owner switched the form off, nothing is stored and the response is a redirect back with `flash.error` = \"This space is not accepting testimonials right now.\" (not a 4xx). Existing data is never deleted on downgrade.",
   auth="public", params=[P("Slug"), *WRITE_PARAMS], throttle="20 requests per minute (shared bucket)",
   body=form_body("SubmissionRequest", {"name": "Ada", "email": "ada@example.com", "body": "Great stuff", "consent": True, "rating": 5, "company": "Acme"}, multipart=True),
   responses={"302": redirect("Back to the previous page (Referer, or the last visited URL). On success `flash.success` = \"Thank you! Your testimonial was sent.\"; when the plan limit or the closed form stopped it, `flash.error` is set instead. Nothing in the status tells these apart: read the flash on the next page load."),
              "404": R("NotFound"), "419": R("CsrfMismatch"), "422": R("ValidationFailed"), "429": R("TooManyRequests")},
   extra=[("422", {"empty": ("Nothing sent, rating on", "invalid_submission_empty"), "rating": ("Rating out of range, disabled field sent", "invalid_submission_rating")})])

# ---- embed -----------------------------------------------------------------------------------------------
EMBED_HEADERS = {"X-Request-ID": H("XRequestId"), "Content-Security-Policy": H("ContentSecurityPolicyEmbed")}
op("get", "/embed/{spaceId}", "showEmbedWall", "Embed", "Embeddable wall (iframe page)",
   "HTML page listing the published testimonials of a space, meant for `<iframe src=\"…/embed/{spaceId}\">`. Sends `Content-Security-Policy: frame-ancestors *` and drops X-Frame-Options, so any site can frame it. Never contains respondent emails. Not rate limited; do not poll it, use the JSON route with your own cache.",
   auth="public", params=[P("SpaceId"), *INERTIA_PARAMS], inertia=True,
   responses={"200": {**page_ok("embed/wall", "page_embed", S("EmbedWallProps")), "headers": {**EMBED_HEADERS, "X-Inertia": H("XInertia")}}, "404": R("NotFound")})
op("get", "/embed/{spaceId}/testimonials.json", "listEmbedTestimonials", "Embed", "Published testimonials as JSON",
   "Same data as the wall, for custom rendering. Published testimonials only. Fields: no email, no status, no favorite flag. CORS headers are not sent, so browsers on other origins cannot read this response from script; use the iframe, or fetch it server-side.",
   auth="public", params=[P("SpaceId"), P("XRequestId")],
   responses={"200": {"description": "Published testimonials.", "headers": EMBED_HEADERS,
                      "content": json_content(S("EmbedWall"), {"wall": ("One published testimonial", "embed_json")})},
              "404": R("NotFound")})

# ---- auth ------------------------------------------------------------------------------------------------
GUEST = {"302": R("GuestOnlyRedirect")}
op("get", "/register", "showRegister", "Auth", "Registration page", "Inertia page `auth/register`. Signed-in users are redirected to /dashboard.",
   auth="guest", params=INERTIA_PARAMS, inertia=True, responses={"200": page_ok("auth/register", "page_login"), **GUEST})
op("post", "/register", "register", "Auth", "Create an account",
   "Creates the user, fires the Registered event (verification mail), signs the user in and redirects to /dashboard. Free plan applies from the start. Verification is required before dashboard, spaces and billing (middleware `verified`).",
   auth="guest", params=WRITE_PARAMS, body=form_body("RegisterRequest", {"name": "Grace Hopper", "email": "grace@example.com", "password": "correct-horse-1", "password_confirmation": "correct-horse-1"}),
   responses={"302": redirect("Success: to /dashboard (signed in). Already signed in: also /dashboard."), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"taken": ("Email taken, weak password, mismatch", "invalid_register")})])
op("get", "/login", "showLogin", "Auth", "Sign-in page", "Inertia page `auth/login`. This is also the easiest way to get the XSRF-TOKEN cookie, the session cookie and the Inertia asset version.",
   auth="guest", params=INERTIA_PARAMS, inertia=True, responses={"200": page_ok("auth/login", "page_login"), **GUEST})
op("post", "/login", "login", "Auth", "Sign in",
   "Checks the credentials, regenerates the session id (so the CSRF token changes: read the new XSRF-TOKEN cookie afterwards) and redirects to the URL the user tried to open, else /dashboard. Limit: 5 failed attempts per email + IP, then 422 with the throttle message (this is not a 429). The edge nginx also limits /login, /register, /forgot-password and /reset-password to 10 requests/minute per IP with a burst of 10 (excess requests get nginx's default limit_req status 503, which the edge's error_page then turns into the outage response with `source: edge`; it is not a 429).",
   auth="guest", params=WRITE_PARAMS, body=form_body("LoginRequest", {"email": "demo@kudos.test", "password": "password", "remember": False}),
   responses={"302": redirect("Success: to the intended URL or /dashboard, session cookie rotated."), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   throttle="5 failed attempts per email+IP (422), 10/min per IP at the edge",
   extra=[("422", {"wrong": ("Wrong credentials", "invalid_login_credentials"), "empty": ("Empty body", "invalid_login_empty"), "locked": ("Locked out after 5 failures", "invalid_login_throttled")})])
op("post", "/logout", "logout", "Auth", "Sign out", "Ends the session, rotates the CSRF token and redirects to `/`.",
   params=WRITE_PARAMS, responses={"302": redirect("To `/`."), "419": R("CsrfMismatch")})
op("get", "/forgot-password", "showForgotPassword", "Auth", "Forgot-password page", "Inertia page `auth/forgot-password`.", auth="guest",
   params=INERTIA_PARAMS, inertia=True, responses={"200": page_ok("auth/forgot-password", "page_login"), **GUEST})
op("post", "/forgot-password", "sendResetLink", "Auth", "Request a password-reset email",
   "Always answers the same way for a valid address, whether or not the account exists (`flash`/`status` = \"A reset link will be sent if the account exists.\"). The mail goes to Mailpit in dev.",
   auth="guest", params=WRITE_PARAMS, body=form_body("ForgotPasswordRequest", {"email": "demo@kudos.test"}),
   responses={"302": redirect("Back to the previous page with `props.status`."), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"bad_email": ("Not an email", "invalid_forgot")})])
op("get", "/reset-password/{token}", "showResetPassword", "Auth", "Reset-password page", "Inertia page `auth/reset-password`; props `token` and `email` echo the URL.",
   auth="guest", params=[P("ResetToken"), P("ResetEmail"), *INERTIA_PARAMS], inertia=True,
   responses={"200": page_ok("auth/reset-password", "page_login"), **GUEST})
op("post", "/reset-password", "resetPassword", "Auth", "Set a new password with a reset token",
   "Success redirects to /login with `status`. A bad or expired token is reported on the `email` field.",
   auth="guest", params=WRITE_PARAMS, body=form_body("ResetPasswordRequest", {"token": "abc", "email": "demo@kudos.test", "password": "new-password-1", "password_confirmation": "new-password-1"}),
   responses={"302": redirect("Success: to /login."), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"token": ("Invalid token", "invalid_reset_token")})])
op("get", "/verify-email", "showVerifyEmail", "Auth", "Verification notice page",
   "Inertia page `auth/verify-email` for users whose address is not verified. Verified users are redirected to /dashboard.",
   params=INERTIA_PARAMS, inertia=True, responses={"200": page_ok("auth/verify-email", "page_login"), "302": R("Redirect")})
op("get", "/verify-email/{id}/{hash}", "verifyEmail", "Auth", "Verify the email address (signed link)",
   "Target of the link in the verification mail. Needs a signed URL (`signed` middleware: bad or expired signature gives 403) and a signed-in user whose id and hash match. Limit `throttle:6,1`. Redirects to /dashboard?verified=1.",
   params=[P("VerifyId"), P("VerifyHash"), P("XRequestId")], throttle="6 per minute (shared bucket)",
   responses={"302": redirect("To `/dashboard?verified=1`.", "http://localhost:8010/dashboard?verified=1"), "403": R("Forbidden"), "429": R("TooManyRequests")})
op("post", "/email/verification-notification", "resendVerification", "Auth", "Resend the verification mail",
   "Limit `throttle:6,1` (shared bucket). Already-verified users are redirected to /dashboard without a mail.",
   params=WRITE_PARAMS, throttle="6 per minute (shared bucket)",
   responses={"302": redirect("Back with `status` = `verification-link-sent`, or to /dashboard when already verified."), "419": R("CsrfMismatch"), "429": R("TooManyRequests")})
op("get", "/confirm-password", "showConfirmPassword", "Auth", "Confirm-password page", "Inertia page `auth/confirm-password`.",
   params=INERTIA_PARAMS, inertia=True, responses={"200": page_ok("auth/confirm-password", "page_confirm_password")})
op("post", "/confirm-password", "confirmPassword", "Auth", "Confirm the current password",
   "Stores `auth.password_confirmed_at` in the session and redirects to the intended URL or /dashboard.",
   params=WRITE_PARAMS, body=form_body("ConfirmPasswordRequest", {"password": "password"}),
   responses={"302": redirect("To the intended URL or /dashboard."), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"wrong": ("Wrong password", "invalid_confirm_password")})])

# ---- settings --------------------------------------------------------------------------------------------
op("get", "/settings", "settingsRedirect", "Settings", "Redirect to profile settings",
   "A framework redirect route for every method. Answers 302 with the relative `Location: settings/profile`.",
   responses={"302": {"$ref": "#/components/responses/Redirect", "description": "To `settings/profile` (relative Location)."}})
op("get", "/settings/profile", "showProfile", "Settings", "Profile page", "Inertia page `settings/profile`.", params=INERTIA_PARAMS, inertia=True,
   responses={"200": page_ok("settings/profile", "page_profile")})
op("patch", "/settings/profile", "updateProfile", "Settings", "Update name and email",
   "Changing the email clears `email_verified_at`; the user must verify again before reaching dashboard, spaces or billing.",
   params=WRITE_PARAMS, body=form_body("ProfileUpdateRequest", {"name": "Demo Owner", "email": "demo@kudos.test"}),
   responses={"302": redirect("To /settings/profile (303 for Inertia).", "http://localhost:8010/settings/profile"), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"invalid": ("Empty name, bad email", "invalid_profile")})])
op("delete", "/settings/profile", "deleteAccount", "Settings", "Delete the account",
   "Requires the current password. Signs the user out, deletes the user and redirects to `/`. Destructive: the collection never calls it with the right password.",
   params=WRITE_PARAMS, body=form_body("DeleteAccountRequest", {"password": "password"}),
   responses={"302": redirect("To `/` after deletion.", "http://localhost:8010/"), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"wrong": ("Wrong password", "invalid_delete_account")})])
op("get", "/settings/password", "showPasswordSettings", "Settings", "Password settings page", "Inertia page `settings/password`.", params=INERTIA_PARAMS, inertia=True,
   responses={"200": page_ok("settings/password", "page_password")})
op("put", "/settings/password", "updatePassword", "Settings", "Change the password",
   "Needs the current password and a confirmed new one (min 8).", params=WRITE_PARAMS,
   body=form_body("PasswordUpdateRequest", {"current_password": "password", "password": "new-password-1", "password_confirmation": "new-password-1"}),
   responses={"302": redirect("Back to the previous page.", "http://localhost:8010/settings/password"), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"wrong": ("Wrong current password", "invalid_current_password")})])
op("get", "/settings/appearance", "showAppearance", "Settings", "Appearance page", "Inertia page `settings/appearance` (theme choice is stored in the browser).",
   params=INERTIA_PARAMS, inertia=True, responses={"200": page_ok("settings/appearance", "page_profile")})

# ---- dashboard -------------------------------------------------------------------------------------------
op("get", "/dashboard", "showDashboard", "Dashboard", "Dashboard",
   "Needs a verified email. Prop `stats`: totals, plan usage, a per-day series for the range, and `show_upgrade_banner` (Free plan and not dismissed). An invalid `range` is a validation error (422 as JSON, redirect with flashed error otherwise).",
   params=[P("DashboardRange"), *INERTIA_PARAMS], inertia=True,
   responses={"200": page_ok("dashboard", "page_dashboard", S("DashboardProps")), "302": R("LoginRedirect"), "409": R("InertiaConflict"), "422": R("ValidationFailed")},
   extra=[("422", {"range": ("Range not 7, 30 or 90", "invalid_range")})])
op("post", "/dashboard/banner/dismiss", "dismissUpgradeBanner", "Dashboard", "Dismiss the upgrade banner",
   "Sets `banner_dismissed_at` on the user. Permanent; there is no HTTP way to undo it.", params=WRITE_PARAMS,
   responses={"302": redirect("Back to the previous page."), "419": R("CsrfMismatch")})

# ---- spaces ----------------------------------------------------------------------------------------------
op("get", "/spaces", "listSpaces", "Spaces", "List your spaces",
   "Inertia page `spaces/index`: `spaces` (with `testimonials_count`) and `canCreate` (false on Free once one space exists).",
   params=INERTIA_PARAMS, inertia=True, responses={"200": page_ok("spaces/index", "page_spaces_index", S("SpacesIndexProps")), "302": R("LoginRedirect"), "409": R("InertiaConflict")})
op("post", "/spaces", "createSpace", "Spaces", "Create a space",
   "Free plan: one space. A second create does not return an error status: it redirects to /billing and flashes \"Your Free plan includes 1 space. Upgrade to Pro to create more.\" Success redirects to /spaces/{spaceId} and flashes \"Space created. Share its link to collect testimonials.\" Read the new id from the Location header. The slug is generated from the name (made unique, never a reserved word).",
   params=WRITE_PARAMS, body=form_body("SpaceRequest", {"name": "API Docs Probe", "header_title": "Tell us what you think", "message": "Say **hi**", "collect_rating": True,
                                                       "theme": "brand", "is_accepting": True, "fields": {"company": {"enabled": True, "required": False}}}, multipart=True),
   responses={"302": redirect("Created: `Location: /spaces/{spaceId}`. Plan limit: `Location: /billing` with `flash.error`.", "http://localhost:8010/spaces/" + SPACE_ID),
              "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"bad": ("Name too long, unknown theme", "invalid_space"), "empty": ("Empty body", "invalid_space_empty")})])
op("get", "/spaces/create", "showCreateSpace", "Spaces", "New-space form",
   "Inertia page `spaces/form` with `space: null`, `themes` and `optionalFields`. On Free with a space already present it redirects to /billing with the limit message.",
   params=INERTIA_PARAMS, inertia=True,
   responses={"200": page_ok("spaces/form", "page_spaces_form_new"), "302": {"$ref": "#/components/responses/Redirect", "description": "Not signed in: /login. Plan limit: /billing."}})
op("get", "/spaces/{spaceId}", "showSpace", "Spaces", "Space inbox",
   "Inertia page `spaces/show`: the space, paginated testimonials (15 per page, newest first, with respondent email), `counts` per filter, the applied `filter` and `range`, and `publicUrl`. Owner only: another owner's space is 403, an unknown id 404.",
   params=[P("SpaceId"), P("InboxFilterQuery"), P("InboxFrom"), P("InboxTo"), P("InboxPage"), *INERTIA_PARAMS], inertia=True,
   responses={"200": page_ok("spaces/show", "page_space_show", S("SpaceShowProps")), "302": R("LoginRedirect"), "403": R("Forbidden"), "404": R("NotFound"), "409": R("InertiaConflict"), "422": R("ValidationFailed")},
   extra=[("422", {"filter": ("Unknown filter", "invalid_inbox_filter"), "range": ("`to` before `from`", "invalid_inbox_range")})])
op("get", "/spaces/{spaceId}/edit", "showEditSpace", "Spaces", "Edit-space form", "Inertia page `spaces/form` with the space filled in. Owner only.",
   params=[P("SpaceId"), *INERTIA_PARAMS], inertia=True,
   responses={"200": page_ok("spaces/form", "page_spaces_form_new"), "302": R("LoginRedirect"), "403": R("Forbidden"), "404": R("NotFound"), "409": R("InertiaConflict")})
op("put", "/spaces/{spaceId}", "updateSpace", "Spaces", "Replace a space's settings",
   "Full update (all required fields again). `PATCH` is an alias with the same rules. Redirects to the inbox. Multipart bodies need `_method=PUT` in a POST.",
   params=[P("SpaceId"), *WRITE_PARAMS], body=form_body("SpaceRequest", {"name": "API Docs Probe", "header_title": "Tell us", "message": "Say hi", "theme": "brand",
                                                                       "collect_rating": True, "is_accepting": True}, multipart=True),
   responses={"302": redirect("To /spaces/{spaceId} with `flash.success` = \"Space updated.\" (303 for Inertia).", "http://localhost:8010/spaces/" + SPACE_ID),
              "403": R("Forbidden"), "404": R("NotFound"), "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"empty": ("Empty body", "invalid_space_empty")})])
op("patch", "/spaces/{spaceId}", "patchSpace", "Spaces", "Update a space (PATCH alias)", "Same handler and rules as PUT: every required field must be sent.",
   params=[P("SpaceId"), *WRITE_PARAMS], body=form_body("SpaceRequest", {"name": "API Docs Probe", "header_title": "Tell us", "message": "Say hi", "theme": "dark"}, multipart=True),
   responses={"302": redirect("To /spaces/{spaceId}.", "http://localhost:8010/spaces/" + SPACE_ID), "403": R("Forbidden"), "404": R("NotFound"),
              "419": R("CsrfMismatch"), "422": R("ValidationFailed")},
   extra=[("422", {"empty": ("Empty body", "invalid_space_empty")})])
op("delete", "/spaces/{spaceId}", "deleteSpace", "Spaces", "Delete a space",
   "Deletes the space and its testimonials. Owner only. Redirects to /spaces with `flash.success` = \"Space deleted.\" The Free-plan slot is free again.",
   params=[P("SpaceId"), *WRITE_PARAMS],
   responses={"302": redirect("To /spaces (303 for Inertia).", "http://localhost:8010/spaces"), "403": R("Forbidden"), "404": R("NotFound"), "419": R("CsrfMismatch")})

# ---- testimonials ----------------------------------------------------------------------------------------
T_COMMON = {"403": R("Forbidden"), "404": R("NotFound"), "419": R("CsrfMismatch")}
op("patch", "/testimonials/{testimonialId}", "editTestimonial", "Testimonials", "Edit the text",
   "Owner only. Sets the body (HTML stripped). Redirects back to the inbox.",
   params=[P("TestimonialId"), *WRITE_PARAMS], body=form_body("EditBodyRequest", {"body": "Edited text"}),
   responses={"302": redirect("Back (Referer) with `flash.success` = \"Testimonial updated.\" (303 for Inertia)."), "422": R("ValidationFailed"), **T_COMMON},
   extra=[("422", {"short": ("Body under 3 characters", "invalid_body")})])
op("patch", "/testimonials/{testimonialId}/status", "setTestimonialStatus", "Testimonials", "Publish, hide or reset",
   "Owner only. `published` makes it appear in the embed wall; `hidden` removes it; `pending` returns it to the queue.",
   params=[P("TestimonialId"), *WRITE_PARAMS], body=form_body("StatusRequest", {"status": "published"}),
   responses={"302": redirect("Back with `flash.success` = \"Status changed to published.\" (303 for Inertia)."), "422": R("ValidationFailed"), **T_COMMON},
   extra=[("422", {"enum": ("Unknown status", "invalid_status")})])
op("patch", "/testimonials/{testimonialId}/favorite", "toggleTestimonialFavorite", "Testimonials", "Toggle favorite",
   "Owner only. No body. Flips `is_favorite`; calling twice restores the original value.", params=[P("TestimonialId"), *WRITE_PARAMS],
   responses={"302": redirect("Back, no flash."), **T_COMMON})
op("delete", "/testimonials/{testimonialId}", "deleteTestimonial", "Testimonials", "Delete a testimonial", "Owner only. Permanent.",
   params=[P("TestimonialId"), *WRITE_PARAMS],
   responses={"302": redirect("Back with `flash.success` = \"Testimonial deleted.\" (303 for Inertia)."), **T_COMMON})

# ---- billing ---------------------------------------------------------------------------------------------
op("get", "/billing", "showBilling", "Billing", "Billing page", "Inertia page `billing/show`; prop `overview` has the plan, usage, subscription status and whether Stripe is configured.",
   params=INERTIA_PARAMS, inertia=True, responses={"200": page_ok("billing/show", "page_billing", S("BillingProps")), "302": R("LoginRedirect"), "409": R("InertiaConflict")})
op("post", "/billing/checkout", "startCheckout", "Billing", "Start Stripe Checkout",
   "Builds a Checkout session for the Pro price and sends the browser to Stripe: a plain request gets 302 to checkout.stripe.com, an Inertia request gets 409 + X-Inertia-Location (the Inertia location trick). Already Pro: redirect to /billing, flash \"You are already on the Pro plan.\" Stripe not configured (no STRIPE_SECRET / STRIPE_PRO_PRICE_ID): redirect to /billing with a generic `flash.error` (the missing setting is only logged). Stripe unreachable after retries: redirect to /billing with \"Billing is temporarily unavailable. Nothing was charged. Try again in a moment.\"",
   params=WRITE_PARAMS,
   responses={"302": redirect("To Stripe (non-Inertia) or to /billing with `flash.error`/`flash.success`.", "http://localhost:8010/billing"),
              "409": {"$ref": "#/components/responses/InertiaConflict", "description": "Inertia request: X-Inertia-Location is the Stripe Checkout URL."},
              "419": R("CsrfMismatch"), "503": R("Unavailable")})
op("get", "/billing/success", "checkoutSuccess", "Billing", "Stripe success return URL",
   "Stripe sends the browser here after payment with `?session_id=cs_...`. The redirect alone proves nothing: the app asks Stripe whether the session belongs to this user and is complete, then reports. The Pro plan itself turns on when the signed webhook arrives. Always redirects to /billing: `flash.success` (\"Welcome to Pro! Your upgrade is active.\" or \"Payment confirmed. Your Pro plan activates as soon as Stripe notifies us ...\") or `flash.error` (\"We could not confirm that payment.\" for a missing or foreign session id).",
   params=[P("SessionIdQuery"), P("XRequestId")],
   responses={"302": redirect("To /billing with a flash message.", "http://localhost:8010/billing"), "503": R("Unavailable")})
op("post", "/billing/portal", "openBillingPortal", "Billing", "Open the Stripe billing portal",
   "Needs a Stripe customer. Without one: redirect to /billing with \"No billing profile yet.\" Otherwise 302 to the portal URL (409 + X-Inertia-Location for Inertia clients).",
   params=WRITE_PARAMS,
   responses={"302": redirect("To the Stripe portal, or to /billing with `flash.error`.", "http://localhost:8010/billing"),
              "409": {"$ref": "#/components/responses/InertiaConflict", "description": "Inertia request: X-Inertia-Location is the portal URL."},
              "419": R("CsrfMismatch"), "503": R("Unavailable")})

# ---- stripe ----------------------------------------------------------------------------------------------
op("post", "/stripe/webhook", "stripeWebhook", "Stripe", "Stripe webhook (Cashier)",
   "Called by Stripe, not by clients. No session, no CSRF (exempt). Cashier verifies the `Stripe-Signature` header against STRIPE_WEBHOOK_SECRET and answers 403 for a bad signature. With no secret configured (local default) the check is skipped. Handles customer.subscription.* , invoice and payment events; unknown event types answer 200 and do nothing. Subscription events are what switch a user between Free and Pro.\n\nLocal testing: `docker compose -f docker/docker-compose.yml --profile billing up stripe` forwards real test-mode events here.",
   auth="public", csrf=False,
   params=[{"name": "Stripe-Signature", "in": "header", "required": False, "schema": string(), "description": "`t=<timestamp>,v1=<hmac>` computed by Stripe."}, P("XRequestId")],
   body={"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True, "description": "A Stripe Event object."},
                                                            "example": {"id": "evt_1", "type": "customer.subscription.updated", "data": {"object": {}}}}}},
   responses={"200": {"description": "Event accepted (or ignored).", "headers": {"X-Request-ID": H("XRequestId")}},
              "403": {"description": "Signature check failed (only when STRIPE_WEBHOOK_SECRET is set).", "headers": ERR_HEADERS,
                      "content": json_content(S("ErrorResponse"), {"bad_signature": ("Bad signature", "error_403")})}})
op("get", "/stripe/payment/{id}", "stripePayment", "Stripe", "Cashier payment confirmation page",
   "Page Cashier uses for off-session payment confirmation (3-D Secure). Not used by the Kudos UI. Behind Cashier's VerifyRedirectUrl middleware. Needs Stripe keys; without them the app answers 500 (a stack trace when APP_DEBUG=true).",
   auth="public", params=[{"name": "id", "in": "path", "required": True, "schema": string(), "description": "Stripe PaymentIntent id."}, P("XRequestId")],
   responses={"200": {"description": "Payment page.", "content": {"text/html": {"schema": S("HtmlDocument")}}}, "500": R("ServerError")})

# ---- framework -------------------------------------------------------------------------------------------
op("get", "/", "home", "Framework", "Home page", "Inertia page `welcome`. Public.", auth="public", params=INERTIA_PARAMS, inertia=True,
   responses={"200": page_ok("welcome", "page_login")})
op("get", "/storage/{path}", "storageFile", "Framework", "Local storage file",
   "Laravel's `storage.local` route. Uploaded logos and photos are served from `public/storage` (a symlink) by the web server first; this route is the fallback of the `local` disk and answers 403 for paths it does not serve.",
   auth="public", params=[{"name": "path", "in": "path", "required": True, "schema": string(), "description": "File path.", "allowReserved": True}],
   responses={"200": {"description": "File contents."}, "403": R("Forbidden")})
op("put", "/storage/{path}", "storageUpload", "Framework", "Local storage signed upload",
   "Laravel's `storage.local.upload` route for signed temporary upload URLs. Not used by Kudos.", auth="public", csrf=False,
   params=[{"name": "path", "in": "path", "required": True, "schema": string(), "description": "File path.", "allowReserved": True}],
   responses={"204": {"description": "Stored."}, "403": R("Forbidden")})
op("get", "/_inertia/devtools/entries", "inertiaDevtoolsEntries", "Framework", "Inertia devtools entries (dev only)",
   "Registered by the Inertia devtools package. Gated by its own Authorize middleware: local environment only. Do not rely on it.", auth="public",
   responses={"200": {"description": "Recorded entries.", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}, "403": R("Forbidden")})
op("get", "/_inertia/devtools/entries/{id}", "inertiaDevtoolsEntry", "Framework", "Inertia devtools entry (dev only)",
   "One recorded entry. Same gating as the list.", auth="public",
   params=[{"name": "id", "in": "path", "required": True, "schema": string(), "description": "Entry id."}],
   responses={"200": {"description": "Entry.", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}, "403": R("Forbidden"), "404": R("NotFound")})


# page props sit next to the shared props, so they must not forbid them
for _name in ("DashboardProps", "SpacesIndexProps", "SpaceShowProps", "BillingProps", "CollectProps", "EmbedWallProps"):
    SCHEMAS[_name]["additionalProperties"] = True
