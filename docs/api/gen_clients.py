"""Renders cases.py into Postman, Insomnia and Bruno collections (requests, scripts, examples, environments)."""
import json
import re
from datetime import datetime, timezone

import cases as C
import endpoints as E

COLLECTION_NAME = "Kudos API"
DESCRIPTION = (
    "Requests for every Kudos route, grouped by area, with assertions on status codes, headers and key fields.\n\n"
    "Run the folders in order (they share one session). The run signs in once as the seeded demo owner, creates one space "
    "with a unique name, exercises it, deletes it and signs out, so it leaves no data behind. Free plan: if the demo owner already "
    "has a space the create is refused with a redirect to /billing and the dependent requests skip themselves.\n\n"
    "Folder 99 only runs with runOptional=true. See docs/api/README.md."
)

STATUS_TEXT = {200: "OK", 204: "No Content", 302: "Found", 303: "See Other", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
               409: "Conflict", 419: "Page Expired", 422: "Unprocessable Entity", 429: "Too Many Requests", 503: "Service Unavailable"}


# ----------------------------------------------------------------------------------------------------------------
# request model shared by all tools
# ----------------------------------------------------------------------------------------------------------------
def headers_for(c):
    h = [("X-Request-ID", "{{requestId}}")]
    mode = c["mode"]
    if mode == "json":
        h.append(("Accept", "application/json"))
    elif mode == "inertia":
        h += [("Accept", "text/html, application/xhtml+xml"), ("X-Inertia", "true"), ("X-Inertia-Version", c["version_value"] or "{{inertiaVersion}}"),
              ("X-Requested-With", "XMLHttpRequest")]
    elif mode == "html":
        h.append(("Accept", "text/html"))
    for k, v in c["headers"].items():
        h.append((k, v))
    if c["csrf"]:
        h.append(("X-XSRF-TOKEN", c["csrf_value"] or "{{xsrfToken}}"))
    if c["referer"]:
        h.append(("Referer", c["referer"]))
    if c["body"] is not None:
        h.append(("Content-Type", "application/json"))
    return h


def query_string(c):
    return "&".join(f"{k}={v}" for k, v in c["query"])


def full_url(c):
    qs = query_string(c)
    return "{{baseUrl}}" + c["path"] + ("?" + qs if qs else "")


def body_text(c):
    return None if c["body"] is None else json.dumps(c["body"], indent=2, ensure_ascii=False)


def description(c):
    parts = [c["desc"]] if c["desc"] else []
    parts.append(f"Mode: {c['mode']}. Expected status: {' or '.join(str(x) for a in c['expect'] if a['k'] == 'status' for x in a['codes'])}.")
    if c["needs"]:
        parts.append("Skipped when these variables are empty: " + ", ".join(c["needs"]) + ".")
    if c["optional"]:
        parts.append("Optional: runs only when runOptional=true.")
    return "\n\n".join(parts)


# ----------------------------------------------------------------------------------------------------------------
# JavaScript generation
# ----------------------------------------------------------------------------------------------------------------
JS_GET = (
    "const __get = (o, p) => { const k = []; p.replace(/\\['([^']+)'\\]|\\[(\\d+)\\]|([^.\\[\\]]+)/g, (m, a, b, c) => "
    "{ k.push(a !== undefined ? a : b !== undefined ? Number(b) : c); return m; }); return k.reduce((x, y) => (x == null ? undefined : x[y]), o); };"
)


class Tool:
    """Per-tool JavaScript bindings. All generated code uses the __ names."""

    def __init__(self, name, set_var, get_var, test, expect, status, header, text, json_expr, set_cookies, skip=None, set_next=None, no_redirect=None,
                 cookie_refresh=""):
        self.name, self.set_var, self.get_var, self.test, self.expect = name, set_var, get_var, test, expect
        self.status, self.header, self.text, self.json_expr, self.set_cookies = status, header, text, json_expr, set_cookies
        self.skip, self.set_next, self.no_redirect, self.cookie_refresh = skip, set_next, no_redirect, cookie_refresh

    def prelude(self):
        return [
            f"const __setVar = (k, v) => {self.set_var};",
            f"const __getVar = (k) => {self.get_var};",
            f"const __status = {self.status};",
            f"const __hdr = (n) => {self.header};",
            f"const __text = {self.text};",
            f"const __setCookies = () => {self.set_cookies};",
            f"let __j; try {{ __j = {self.json_expr}; }} catch (e) {{ __j = undefined; }}",
            JS_GET,
        ]


POSTMAN = Tool("postman",
               set_var="pm.environment.set(k, v)", get_var="pm.environment.get(k)",
               test="pm.test", expect="pm.expect", status="pm.response.code", header="pm.response.headers.get(n)",
               text="pm.response.text()", json_expr="JSON.parse(pm.response.text())",
               set_cookies="pm.response.headers.filter((h) => String(h.key).toLowerCase() === 'set-cookie').map((h) => h.value)",
               skip="pm.execution.skipRequest()", set_next="pm.execution.setNextRequest(pm.info.requestName)",
               cookie_refresh="const __ck = pm.cookies.get('XSRF-TOKEN'); if (__ck) { __setVar('xsrfToken', decodeURIComponent(__ck)); }")
BRUNO = Tool("bruno",
             set_var="bru.setVar(k, v)", get_var="(bru.getVar(k) ?? bru.getEnvVar(k))",
             test="test", expect="expect", status="res.getStatus()", header="res.getHeader(n.toLowerCase())",
             text="(typeof res.getBody() === 'string' ? res.getBody() : JSON.stringify(res.getBody()))",
             json_expr="(typeof res.getBody() === 'object' && res.getBody() !== null ? res.getBody() : JSON.parse(res.getBody()))",
             set_cookies="[].concat(res.getHeader('set-cookie') || [])",
             skip="bru.runner.skipRequest()", set_next="bru.runner.setNextRequest(req.getName())", no_redirect="req.setMaxRedirects(0);",
             cookie_refresh=("for (const __c of [].concat(res.getHeader('set-cookie') || [])) { "
                             "const __m = /^XSRF-TOKEN=([^;]+)/.exec(__c); if (__m) { __setVar('xsrfToken', decodeURIComponent(__m[1])); } }"))
INSOMNIA = Tool("insomnia",
                set_var="insomnia.environment.set(k, v)", get_var="insomnia.variables.get(k)",
                test="insomnia.test", expect="insomnia.expect", status="insomnia.response.code",
                header="insomnia.response.headers.get(n)", text="insomnia.response.text()", json_expr="insomnia.response.json()",
                set_cookies="(() => { const a = []; try { insomnia.response.headers.each((h) => { if (String(h.key).toLowerCase() === 'set-cookie') { a.push(h.value); } }); } catch (e) {} return a; })()",
                cookie_refresh=("let __sc = []; try { insomnia.response.headers.each((h) => { if (String(h.key).toLowerCase() === 'set-cookie') { __sc.push(h.value); } }); } catch (e) {} "
                                "for (const __c of __sc) { const __m = /^XSRF-TOKEN=([^;]+)/.exec(__c); if (__m) { __setVar('xsrfToken', decodeURIComponent(__m[1])); } }"))


def jstr(s):
    return json.dumps(s, ensure_ascii=False)


def jsval(v):
    """JS expression for a literal that may hold {{var}} references."""
    if isinstance(v, str) and "{{" in v:
        parts = re.split(r"\{\{(\w+)\}\}", v)
        out = []
        for i, p in enumerate(parts):
            if i % 2:
                out.append(f"__getVar({jstr(p)})")
            elif p:
                out.append(jstr(p))
        return " + ".join(out)
    return json.dumps(v, ensure_ascii=False)


def has_status(c):
    return next((a for a in c["expect"] if a["k"] == "status"), None)


def assertion_js(a, T):
    t, ex = T.test, T.expect
    k = a["k"]
    if k == "status":
        codes = a["codes"]
        label = " or ".join(str(x) for x in codes)
        return f"{t}({jstr('status is ' + label)}, function () {{ {ex}({json.dumps(codes)}).to.include(__status); }});"
    if k == "header":
        if a["pattern"] is None:
            return f"{t}({jstr(a['name'] + ' header is present')}, function () {{ {ex}(__hdr({jstr(a['name'])})).to.exist; }});"
        return (f"{t}({jstr(a['name'] + ' header matches ' + a['pattern'])}, function () {{ "
                f"{ex}(String(__hdr({jstr(a['name'])}) || '')).to.match(new RegExp({jstr(a['pattern'])})); }});")
    if k == "header_opt":
        return (f"{t}({jstr(a['name'] + ' header, when sent, matches ' + a['pattern'])}, function () {{ "
                f"const __h = __hdr({jstr(a['name'])}); if (__h) {{ {ex}(String(__h)).to.match(new RegExp({jstr(a['pattern'])})); }} }});")
    if k == "cookie":
        return (f"{t}({jstr('sets the ' + a['name'] + ' cookie')}, function () {{ "
                f"{ex}(__setCookies().some((c) => String(c).startsWith({jstr(a['name'] + '=')}))).to.equal(true); }});")
    if k == "no_header":
        return f"{t}({jstr(a['name'] + ' header is absent')}, function () {{ {ex}(__hdr({jstr(a['name'])}) || null).to.equal(null); }});"
    if k == "location":
        return (f"{t}({jstr('Location matches ' + a['pattern'])}, function () {{ "
                f"{ex}(String(__hdr('Location') || '')).to.match(new RegExp({jstr(a['pattern'])})); }});")
    if k == "text":
        return f"{t}({jstr('body contains ' + a['value'])}, function () {{ {ex}(__text.includes({jstr(a['value'])})).to.equal(true); }});"
    if k == "no_text":
        return f"{t}({jstr('body does not contain ' + a['value'])}, function () {{ {ex}(__text.includes({jstr(a['value'])})).to.equal(false); }});"
    if k == "json":
        path, op, val = a["path"], a["op"], a["value"]
        name = f"json {path} {op}" + ("" if op in ("exists", "missing") else f" {json.dumps(val, ensure_ascii=False)}")
        v = f"__get(__j, {jstr(path)})"
        body = {
            "exists": f"{ex}({v}).to.not.equal(undefined); {ex}({v}).to.not.equal(null);",
            "missing": f"{ex}({v}).to.equal(undefined);",
            "eq": f"{ex}({v}).to.deep.equal({jsval(val)});",
            "type": f"{ex}(Array.isArray({v}) ? 'array' : typeof {v}).to.equal({jstr(val)});",
            "match": f"{ex}(String({v})).to.match(new RegExp({jstr(val)}));",
            "gte": f"{ex}({v}).to.be.at.least({json.dumps(val)});",
            "len_gte": f"{ex}({v}).to.be.an('array'); {ex}({v}.length).to.be.at.least({json.dumps(val)});",
            "len": f"{ex}({v}).to.be.an('array'); {ex}({v}.length).to.equal({json.dumps(val)});",
            "includes": f"{ex}({v}).to.include({jsval(val)});",
        }[op]
        return f"{t}({jstr(name)}, function () {{ {body} }});"
    raise ValueError(k)


def capture_js(cap):
    var, src, arg = cap["var"], cap["from"], cap["arg"]
    if src == "json":
        return f"{{ const __v = __get(__j, {jstr(arg)}); if (__v !== undefined && __v !== null) {{ __setVar({jstr(var)}, String(__v)); }} }}"
    if src == "location":
        return f"{{ const __m = new RegExp({jstr(arg)}).exec(String(__hdr('Location') || '')); if (__m) {{ __setVar({jstr(var)}, __m[1]); }} }}"
    if src == "body":
        return f"{{ const __m = new RegExp({jstr(arg)}).exec(__text); if (__m) {{ __setVar({jstr(var)}, __m[1]); }} }}"
    raise ValueError(src)


def pre_request_js(c, T):
    lines = [
        "// Generated by docs/api/build.py. Do not edit by hand.",
        "__setVar('requestId', 'kudos-api-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8));",
        "if (!__getVar('runId')) { const __id = Date.now().toString(36); __setVar('runId', __id); __setVar('spaceName', 'API Probe ' + __id); }",
    ]
    guards = []
    for n in c["needs"]:
        guards.append(f"!__getVar({jstr(n)}) || __getVar({jstr(n)}) === 'false'")
    if c["optional"]:
        guards.append("__getVar('runOptional') !== 'true'")
    if guards and T.skip:
        lines.append(f"if ({' || '.join(guards)}) {{ {T.skip}; }}")
    if T.no_redirect:
        lines.append(T.no_redirect)
    pre = T.prelude()
    # the pre-request script only needs the variable helpers
    head = [pre[0], pre[1]]
    return head + lines


def post_response_js(c, T, index):
    """Captures and cookie refresh (always run), then assertions (not while a loop is still repeating)."""
    code = T.prelude()
    code.append(T.cookie_refresh)
    for cap in c["capture"]:
        code.append(capture_js(cap))
    again = "false"
    if c["loop_until"] is not None and T.set_next:
        counter = jstr(f"loop{index}")
        lu = c["loop_until"]
        code.append(f"const __n = Number(__getVar({counter}) || 0) + 1; __setVar({counter}, String(__n));")
        if isinstance(lu, tuple):
            again = f"__n < {lu[1]}"
        else:
            again = f"(__status !== {lu} && __n < 70)"
        code.append(f"const __again = {again}; if (__again) {{ {T.set_next}; }} else {{ __setVar({counter}, '0'); }}")
    else:
        code.append("const __again = false;")
    tests = [
        f"{T.test}('echoes X-Request-ID', function () {{ {T.expect}(__hdr('X-Request-ID')).to.equal(__getVar('requestId')); }});",
        *[assertion_js(a, T) for a in c["expect"]],
    ]
    code.append("if (!__again) {")
    code.extend("  " + t for t in tests)
    code.append("}")
    return code


def split_script(code_lines, tests_start_marker="if (!__again) {"):
    return code_lines


# ----------------------------------------------------------------------------------------------------------------
# example responses
# ----------------------------------------------------------------------------------------------------------------
def example_for(c):
    ex = c["example"]
    if not ex:
        return None
    code, key, extra = ex
    body = E.EXAMPLES[key] if key else None
    hdrs = {"X-Request-ID": E.REQUEST_ID}
    if body is not None:
        hdrs["Content-Type"] = "application/json"
    hdrs.update(extra)
    return {"code": code, "status": STATUS_TEXT.get(code, ""), "headers": hdrs, "body": json.dumps(body, indent=2, ensure_ascii=False) if body is not None else ""}


# ----------------------------------------------------------------------------------------------------------------
# Postman
# ----------------------------------------------------------------------------------------------------------------
def postman_url(c):
    raw = full_url(c)
    path = [p for p in c["path"].split("/") if p]
    u = {"raw": raw, "host": ["{{baseUrl}}"], "path": path}
    if c["query"]:
        u["query"] = [{"key": k, "value": v} for k, v in c["query"]]
    return u


def postman_request(c):
    r = {"method": c["method"], "header": [{"key": k, "value": v, "type": "text"} for k, v in headers_for(c)], "url": postman_url(c),
         "description": description(c)}
    if c["body"] is not None:
        r["body"] = {"mode": "raw", "raw": body_text(c), "options": {"raw": {"language": "json"}}}
    return r


def postman_item(c, index):
    pre = pre_request_js(c, POSTMAN)
    post = post_response_js(c, POSTMAN, index)
    item = {
        "name": c["name"],
        "event": [
            {"listen": "prerequest", "script": {"type": "text/javascript", "exec": pre}},
            {"listen": "test", "script": {"type": "text/javascript", "exec": post}},
        ],
        "request": postman_request(c),
        "protocolProfileBehavior": {"followRedirects": False},
        "response": [],
    }
    ex = example_for(c)
    if ex:
        item["response"].append({
            "name": f"{ex['code']} {ex['status']}", "originalRequest": postman_request(c), "status": ex["status"], "code": ex["code"],
            "_postman_previewlanguage": "json" if ex["body"] else "text",
            "header": [{"key": k, "value": v} for k, v in ex["headers"].items()], "cookie": [], "body": ex["body"],
        })
    return item


def postman_env(key, spec):
    values = []
    for name in C.ENV_VARIABLES:
        default, desc, secret = C.VARIABLES[name]
        value = spec["baseUrl"] if name == "baseUrl" else default
        values.append({"key": name, "value": value, "type": "secret" if secret else "default", "enabled": True})
    return {"id": f"kudos-{key}", "name": spec["label"], "values": values, "_postman_variable_scope": "environment",
            "_postman_exported_at": "2026-11-19T00:00:00.000Z", "_postman_exported_using": "docs/api/build.py"}


def postman_collection():
    folders = []
    idx = 0
    for f in C.FOLDERS:
        items = []
        for c in f["cases"]:
            items.append(postman_item(c, idx))
            idx += 1
        folders.append({"name": f["name"], "description": f["desc"], "item": items})
    return {
        "info": {"_postman_id": "6b7a1c5e-0f1d-4f43-9d0f-4b6f1d6a2c11", "name": COLLECTION_NAME, "description": DESCRIPTION,
                 "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
        "item": folders,
        "variable": [{"key": n, "value": C.VARIABLES[n][0]} for n in ("baseUrl", "email", "password", "missingId", "runOptional")],
    }


# ----------------------------------------------------------------------------------------------------------------
# Insomnia (v4 export)
# ----------------------------------------------------------------------------------------------------------------
def ins(s):
    return re.sub(r"\{\{(\w+)\}\}", r"{{ _.\1 }}", s) if isinstance(s, str) else s


def insomnia_export():
    res = []
    wrk = "wrk_kudos_api"
    res.append({"_id": wrk, "_type": "workspace", "parentId": None, "name": COLLECTION_NAME, "description": DESCRIPTION, "scope": "collection"})
    base_data = {n: C.VARIABLES[n][0] for n in C.ENV_VARIABLES}
    res.append({"_id": "env_kudos_base", "_type": "environment", "parentId": wrk, "name": "Base Environment", "data": base_data,
                "dataPropertyOrder": {"&": C.ENV_VARIABLES}, "color": None, "isPrivate": False, "metaSortKey": 1})
    for i, (key, spec) in enumerate(C.ENVIRONMENTS.items()):
        res.append({"_id": f"env_kudos_{key.replace('-', '_')}", "_type": "environment", "parentId": "env_kudos_base", "name": spec["label"],
                    "data": {"baseUrl": spec["baseUrl"]}, "dataPropertyOrder": {"&": ["baseUrl"]}, "color": None, "isPrivate": False, "metaSortKey": 2 + i})
    res.append({"_id": "jar_kudos_api", "_type": "cookie_jar", "parentId": wrk, "name": "Default Jar", "cookies": []})
    idx = 0
    for fi, f in enumerate(C.FOLDERS):
        fid = f"fld_kudos_{fi:02d}"
        res.append({"_id": fid, "_type": "request_group", "parentId": wrk, "name": f["name"], "description": f["desc"], "environment": {},
                    "environmentPropertyOrder": None, "metaSortKey": -1000 + fi})
        for ci, c in enumerate(f["cases"]):
            if c["optional"]:
                continue  # Insomnia has no way to skip a request from a script; the optional folder is left out of this export
            pre = pre_request_js(c, INSOMNIA)
            post = post_response_js(c, INSOMNIA, idx)
            idx += 1
            r = {"_id": f"req_kudos_{fi:02d}_{ci:02d}", "_type": "request", "parentId": fid, "name": c["name"], "description": description(c),
                 "method": c["method"], "url": ins(full_url(c)), "parameters": [],
                 "headers": [{"name": k, "value": ins(v)} for k, v in headers_for(c)], "authentication": {},
                 "preRequestScript": "\n".join(pre), "afterResponseScript": "\n".join(post),
                 "metaSortKey": -1000 + ci, "settingStoreCookies": True, "settingSendCookies": True, "settingDisableRenderRequestBody": False,
                 "settingEncodeUrl": True, "settingRebuildPath": True, "settingFollowRedirects": "off"}
            if c["body"] is not None:
                r["body"] = {"mimeType": "application/json", "text": ins(body_text(c))}
            else:
                r["body"] = {}
            res.append(r)
    return {"_type": "export", "__export_format": 4, "__export_date": "2026-11-19T00:00:00.000Z", "__export_source": "docs/api/build.py", "resources": res}


# ----------------------------------------------------------------------------------------------------------------
# Bruno
# ----------------------------------------------------------------------------------------------------------------
def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def indent(lines, n=2):
    pad = " " * n
    return "\n".join(pad + ln if ln else "" for ln in lines)


def bruno_request(c, seq, index):
    method = c["method"].lower()
    out = [f"meta {{\n  name: {c['name']}\n  type: http\n  seq: {seq}\n}}\n"]
    body_kind = "json" if c["body"] is not None else "none"
    out.append(f"{method} {{\n  url: {full_url(c)}\n  body: {body_kind}\n  auth: none\n}}\n")
    out.append("headers {\n" + "\n".join(f"  {k}: {v}" for k, v in headers_for(c)) + "\n}\n")
    if c["body"] is not None:
        out.append("body:json {\n" + indent(body_text(c).split("\n")) + "\n}\n")
    pre = pre_request_js(c, BRUNO)
    out.append("script:pre-request {\n" + indent(pre) + "\n}\n")
    post = post_response_js(c, BRUNO, index)
    # Bruno runs captures in script:post-response and assertions in tests; both need the helpers, so split at the test block
    cut = post.index("if (!__again) {")
    script_part, test_part = post[:cut], post[cut:]
    out.append("script:post-response {\n" + indent(script_part) + "\n}\n")
    out.append("tests {\n" + indent(T_PRELUDE_BRUNO + ["const __again = " + ("(bru.getVar(%s) || '0') !== '0'" % jstr(f"loop{index}") if c["loop_until"] is not None else "false") + ";"] + test_part) + "\n}\n")
    out.append("docs {\n" + indent(description(c).split("\n")) + "\n}\n")
    return "\n".join(out)


T_PRELUDE_BRUNO = BRUNO.prelude()


def bruno_env(key, spec):
    lines = ["vars {"]
    for n in C.ENV_VARIABLES:
        value = spec["baseUrl"] if n == "baseUrl" else C.VARIABLES[n][0]
        lines.append(f"  {n}: {value}")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def bruno_files():
    """Returns {relative path: text}."""
    files = {}
    files["bruno.json"] = json.dumps({"version": "1", "name": COLLECTION_NAME, "type": "collection", "ignore": ["node_modules", ".git"]}, indent=2) + "\n"
    files["collection.bru"] = ("docs {\n" + indent(DESCRIPTION.split("\n")) + "\n}\n")
    for key, spec in C.ENVIRONMENTS.items():
        files[f"environments/{key}.bru"] = bruno_env(key, spec)
    idx = 0
    for fi, f in enumerate(C.FOLDERS, 1):
        d = f"{fi:02d}-{slug(f['name'][3:])}"
        files[f"{d}/folder.bru"] = f"meta {{\n  name: {f['name']}\n  seq: {fi}\n}}\n\ndocs {{\n{indent(f['desc'].split(chr(10)))}\n}}\n"
        for ci, c in enumerate(f["cases"], 1):
            files[f"{d}/{ci:02d}-{slug(c['name'])}.bru"] = bruno_request(c, ci, idx)
            idx += 1
    return files


def write_all(outdir):
    pm = outdir / "postman"
    (pm).mkdir(parents=True, exist_ok=True)
    (pm / "kudos.postman_collection.json").write_text(json.dumps(postman_collection(), indent=2, ensure_ascii=False) + "\n")
    (pm / "kudos.local.postman_environment.json").write_text(json.dumps(postman_env("local", C.ENVIRONMENTS["local"]), indent=2) + "\n")
    (pm / "kudos.prod-style.postman_environment.json").write_text(json.dumps(postman_env("prod-style", C.ENVIRONMENTS["prod-style"]), indent=2) + "\n")
    ins_dir = outdir / "insomnia"
    ins_dir.mkdir(exist_ok=True)
    (ins_dir / "kudos.insomnia.json").write_text(json.dumps(insomnia_export(), indent=2, ensure_ascii=False) + "\n")
    bru_dir = outdir / "bruno"
    import shutil
    if bru_dir.exists():
        shutil.rmtree(bru_dir)
    for rel, text in bruno_files().items():
        p = bru_dir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
