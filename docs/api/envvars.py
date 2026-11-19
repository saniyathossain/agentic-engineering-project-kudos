"""Configuration reference data: curated variables with meaning, example and secret flag.

docs/configuration.md is generated from this file plus a scan of the PHP config (scan_env.py), so a variable that the code
reads but that is missing here still appears in the "Other settings" table, and build.py warns about it.

Each entry: name -> dict(default, where, meaning, example, secret). `default=None` means "taken from the config scan".
`where` names the service(s) that read it: app (php-fpm / php artisan serve), queue, scheduler, edge (nginx), db, vite, compose (host side), build.
"""

APP_SERVICES = "app, queue, scheduler"


def v(default, where, meaning, example="", secret=False):
    return dict(default=default, where=where, meaning=meaning, example=example, secret=secret)


GROUPS = [
    ("Application", "codes/config/app.php, codes/config/observability.php. Set in `docker/.envs/app.env.example` (dev) and `app.prod.env` (prod).", {
        "APP_NAME": v(None, APP_SERVICES, "Application name. Used in page titles, mail and the default cookie and cache prefixes (`kudos_session`).", "Kudos"),
        "APP_ENV": v(None, APP_SERVICES, "Environment name. `production` turns the Content-Security-Policy on by default and changes error pages; the prod image sets it.", "local | production"),
        "APP_DEBUG": v(None, APP_SERVICES, "Show stack traces for unexpected errors instead of the friendly 500 page. Must be false in production.", "true"),
        "APP_URL": v(None, APP_SERVICES, "Public origin. Used for generated links, mail and storage URLs. Dev: the published app port.", "http://localhost:8010"),
        "APP_KEY": v("(generated)", APP_SERVICES, "Encryption key for cookies and sessions. Dev: the app container generates one into `codes/.env`. Prod: set it yourself (`php artisan key:generate --show`). Changing it signs everyone out.", "base64:...", True),
        "APP_PREVIOUS_KEYS": v(None, APP_SERVICES, "Comma-separated old keys still accepted for decryption during rotation.", "base64:old1,base64:old2", True),
        "APP_LOCALE": v(None, APP_SERVICES, "Application language. Only English exists.", "en"),
        "APP_FALLBACK_LOCALE": v(None, APP_SERVICES, "Fallback language.", "en"),
        "APP_TIMEZONE": v(None, APP_SERVICES, "PHP and database display timezone. Dates in the app are UTC; leave it.", "UTC"),
        "APP_ROLE": v(None, APP_SERVICES, "Which process this container is: `web`, `queue` or `scheduler`. Set by `docker-compose.prod.yml` per service; shows up in every log line (`where.role`) and decides whether the prod entrypoint runs migrations and caches config.", "queue"),
        "APP_VERSION": v(None, APP_SERVICES, "Release label written to every log line (`where.version`). Set it in CI to the image tag or commit.", "2026.11.19-abc1234"),
        "APP_COMMIT": v(None, APP_SERVICES, "Commit id written to every log line. Baked into the prod image from the build arg `GIT_SHA`.", "a1b2c3d"),
        "TRUSTED_PROXIES": v("(unset)", "app", "Read by Laravel itself (not in config/). Proxies whose X-Forwarded-* headers are trusted. Prod: the edge nginx and any TLS proxy; `*` trusts all.", "*"),
        "BCRYPT_ROUNDS": v("12", "app", "Read by Laravel itself. Password hashing cost. phpunit.xml lowers it to 4 for tests.", "12"),
    }),
    ("Database", "codes/config/database.php. Postgres 18 in both stacks.", {
        "DB_CONNECTION": v("sqlite", APP_SERVICES, "Database driver. The stacks set `pgsql`. Tests use `sqlite` in memory through phpunit.xml.", "pgsql"),
        "DB_HOST": v("127.0.0.1", APP_SERVICES, "Database host. Compose service name `db`.", "db"),
        "DB_PORT": v("5432 (pgsql)", APP_SERVICES, "Database port inside the Docker network. (The host-side published port is a different variable, `DB_PORT` in the compose section.)", "5432"),
        "DB_DATABASE": v("laravel (pgsql config)", APP_SERVICES + ", db", "Database name. Also read by compose for `POSTGRES_DB`.", "kudos"),
        "DB_USERNAME": v("root", APP_SERVICES + ", db", "Database user. Also read by compose for `POSTGRES_USER`.", "kudos"),
        "DB_PASSWORD": v(None, APP_SERVICES, "Database password. Dev: the example file uses `kudos`. Prod: not set as a variable; provided as the Docker secret `db_password` through `DB_PASSWORD_FILE`.", "kudos", True),
        "DB_PASSWORD_FILE": v("(unset)", "app, queue, scheduler, db", "Prod only. Path of a Docker secret file (`/run/secrets/db_password`). `entrypoint.prod.sh` turns any `NAME_FILE` variable into `NAME` before PHP starts, so `STRIPE_SECRET_FILE` and others work the same way.", "/run/secrets/db_password", True),
        "DB_URL": v(None, "app", "One connection URL instead of the separate DB_* values.", "pgsql://kudos:secret@db:5432/kudos", True),
    }),
    ("Sessions, cache, queue, mail", "codes/config/session.php, cache.php, queue.php, mail.php.", {
        "SESSION_DRIVER": v(None, "app", "Where sessions live. `database` in both stacks (so any app container can serve any request).", "database"),
        "SESSION_LIFETIME": v(None, "app", "Idle minutes before a session expires.", "120"),
        "SESSION_SECURE_COOKIE": v(None, "app", "Send the session and XSRF cookies over HTTPS only. Prod example sets `true`; leave unset in dev (plain http).", "true"),
        "SESSION_SAME_SITE": v(None, "app", "SameSite attribute of the cookies.", "lax"),
        "SESSION_DOMAIN": v(None, "app", "Cookie domain. Unset means the exact host.", ".example.com"),
        "SESSION_COOKIE": v("kudos_session", "app", "Session cookie name (derived from APP_NAME).", "kudos_session"),
        "CACHE_STORE": v(None, "app", "Cache backend. `database`; also holds the throttle counters.", "database"),
        "QUEUE_CONNECTION": v(None, "app, queue", "Queue backend. `database`; the queue service runs `queue:work`.", "database"),
        "MAIL_MAILER": v(None, "app, queue", "Mail transport. Dev: `smtp` to Mailpit (http://localhost:8030). Config default is `log`.", "smtp"),
        "MAIL_HOST": v(None, "app, queue", "SMTP host. Dev: `mailpit`.", "mailpit"),
        "MAIL_PORT": v(None, "app, queue", "SMTP port. Dev: 1025. Prod example: 587.", "1025"),
        "MAIL_USERNAME": v(None, "app, queue", "SMTP user.", "apikey", True),
        "MAIL_PASSWORD": v(None, "app, queue", "SMTP password.", "", True),
        "MAIL_ENCRYPTION": v(None, "app, queue", "SMTP encryption.", "tls"),
        "MAIL_FROM_ADDRESS": v(None, "app, queue", "Sender address of verification and reset mail.", "hello@kudos.test"),
        "MAIL_FROM_NAME": v(None, "app, queue", "Sender name.", "Kudos"),
    }),
    ("Stripe and billing", "codes/config/services.php and Laravel Cashier. Test mode only in this project. Without the keys, checkout and portal redirect to /billing with a generic message and the missing setting is logged.", {
        "STRIPE_KEY": v("(empty)", "app", "Stripe publishable key. Read by Cashier.", "pk_test_...", False),
        "STRIPE_SECRET": v("(empty)", "app, queue, compose (stripe CLI)", "Stripe secret key. Read by Cashier; the optional `stripe` compose profile also uses it to forward webhooks. Never commit it.", "sk_test_...", True),
        "STRIPE_WEBHOOK_SECRET": v("(empty)", "app", "Signing secret of the webhook endpoint (`whsec_...`). When set, `POST /stripe/webhook` rejects unsigned or badly signed events with 403; when empty the check is skipped (local only).", "whsec_...", True),
        "STRIPE_PRO_PRICE_ID": v(None, "app", "Stripe Price id of the Pro plan used by Checkout.", "price_1Abc...", False),
        "STRIPE_TIMEOUT_S": v(None, "app, queue", "Total timeout of one Stripe API call, in seconds.", "10"),
        "STRIPE_CONNECT_TIMEOUT_S": v(None, "app, queue", "Connect timeout of one Stripe API call, in seconds.", "3"),
        "CASHIER_CURRENCY": v("usd", "app", "Optional Cashier setting read by the package (not in config/): billing currency.", "usd"),
        "STRIPE_WEBHOOK_TOLERANCE": v("300", "app", "Optional Cashier setting: seconds a webhook timestamp may differ from now.", "300"),
    }),
    ("Logging", "codes/config/logging.php and observability.php. One JSON object per line on stderr (`docker compose logs`).", {
        "LOG_CHANNEL": v(None, APP_SERVICES, "Log channel. `stderr_json` writes the five-W JSON format to stderr.", "stderr_json"),
        "LOG_LEVEL": v("debug", APP_SERVICES, "Minimum level. Dev example: debug. Prod example: info.", "info"),
        "LOG_FORMAT": v(None, APP_SERVICES, "`json` (default) or `text` for humans.", "json"),
        "LOG_SERVICE": v(None, APP_SERVICES, "Service name in every log line (`where.service`).", "kudos"),
        "LOG_REQUEST_ID_HEADER": v(None, "app, edge", "Header that carries the request id in and out. The nginx template hard-codes `X-Request-ID`, so change both together.", "X-Request-ID"),
        "LOG_ACCESS": v(None, "app", "Access log mode: `all`, `errors` (4xx, 5xx and slow) or `off`.", "errors"),
        "LOG_ACCESS_SLOW_MS": v(None, "app", "Requests slower than this are logged as slow even in `errors` mode.", "1000"),
        "LOG_TRACE_LIMIT": v(None, "app", "Stack frames kept in an exception log line.", "10"),
        "LOG_MESSAGE_LIMIT": v(None, "app", "Maximum characters of a log message (longer ones are cut).", "2000"),
        "LOG_STACK": v(None, "app", "Channels combined by the `stack` channel (unused by default).", "single"),
        "LOG_DEPRECATIONS_CHANNEL": v(None, "app", "Where PHP deprecation notices go.", "null"),
    }),
    ("Resilience", "codes/config/resilience.php. Retry with exponential backoff for outbound calls (Stripe).", {
        "RETRY_ATTEMPTS": v(None, "app, queue", "Tries per call, first one included.", "3"),
        "RETRY_BASE_DELAY_MS": v(None, "app, queue", "Delay before the first retry.", "200"),
        "RETRY_MAX_DELAY_MS": v(None, "app, queue", "Upper bound of one delay.", "5000"),
        "RETRY_FACTOR": v(None, "app, queue", "Multiplier between delays.", "2"),
        "RETRY_JITTER": v(None, "app, queue", "`full`, `equal` or `none`: how randomness is added to each delay.", "full"),
        "RETRY_BUDGET_MS": v(None, "app, queue", "Stop retrying after this much total time (0 means attempts only).", "15000"),
        "OUTAGE_FIRST_MS": v(None, "app, edge", "Outage page: first re-check after this many ms. Read by the app (in-app banner) and rendered by nginx into `/status/outage-config.json`. Whole numbers only. Defined once in `docker/.envs/outage.env`.", "4000"),
        "OUTAGE_LONGEST_MS": v(None, "app, edge", "Outage page: longest pause between re-checks, in ms.", "15000"),
    }),
    ("Security", "codes/config/security.php (SecurityHeaders middleware).", {
        "CSP_ENABLED": v("true when APP_ENV is production, else false", "app", "Send a nonce-based Content-Security-Policy. Off in dev because the Vite dev server serves scripts from another origin. Embed routes get `frame-ancestors *`, every other route `frame-ancestors 'self'`.", "true"),
        "CSP_REPORT_ONLY": v(None, "app", "Send the policy as `Content-Security-Policy-Report-Only` to trial it without blocking anything.", "false"),
    }),
]

# variables of the Docker stack that PHP never reads
DOCKER_GROUPS = [
    ("Compose, host side (shell or `docker/.env`)", "`docker/docker-compose.yml` and `docker-compose.prod.yml` substitute these when you run `docker compose`. All have defaults; none is a secret except the DB and Stripe values noted.", {
        "APP_PORT": v("8010", "compose", "Host port of the app. Dev: published from `php artisan serve` (container port 8000). Prod: published from the nginx edge (container port 8080). Use `APP_PORT=8011` to run the prod-style stack beside dev.", "8011"),
        "VITE_PORT": v("5180", "compose", "Host port of the Vite dev server (dev only).", "5180"),
        "DB_PORT": v("5440", "compose", "Host port of Postgres in dev (loopback only; prod publishes none). Not the same as the app's `DB_PORT`, which is the port inside the network.", "5440"),
        "MAILPIT_PORT": v("8030", "compose", "Host port of the Mailpit web UI (dev only).", "8030"),
        "DB_DATABASE": v("kudos", "compose", "Becomes `POSTGRES_DB` of the db service (also the app's `DB_DATABASE`).", "kudos"),
        "DB_USERNAME": v("kudos", "compose", "Becomes `POSTGRES_USER` of the db service (also the app's `DB_USERNAME`).", "kudos"),
        "DB_PASSWORD (compose)": v("kudos", "compose", "Dev: becomes `POSTGRES_PASSWORD` of the db service. Prod uses the Docker secret file instead.", "kudos", True),
        "APP_MEM_LIMIT": v("768m dev, 512m prod", "compose", "Memory cap of the app container.", "512m"),
        "APP_CPUS": v("1.0 dev, 1.5 prod", "compose", "CPU cap of the app container.", "1.0"),
        "QUEUE_MEM_LIMIT": v("384m (dev)", "compose", "Memory cap of the dev queue worker.", "384m"),
        "QUEUE_CPUS": v("0.5 (dev)", "compose", "CPU cap of the dev queue worker.", "0.5"),
        "VITE_MEM_LIMIT": v("1g", "compose", "Memory cap of the Vite container.", "1g"),
        "VITE_CPUS": v("1.0", "compose", "CPU cap of the Vite container.", "1.0"),
        "DB_MEM_LIMIT": v("512m", "compose", "Memory cap of Postgres.", "512m"),
        "DB_CPUS": v("1.0", "compose", "CPU cap of Postgres.", "1.0"),
        "KUDOS_IMAGE": v("kudos-app:prod", "compose", "Name and tag of the prod app image (build target `prod`).", "registry.example.com/kudos-app:1.4.0"),
        "KUDOS_EDGE_IMAGE": v("kudos-edge:prod", "compose", "Name and tag of the prod nginx image (build target `edge`).", "registry.example.com/kudos-edge:1.4.0"),
        "KUDOS_DB_IMAGE": v("kudos-db:prod", "compose", "Name and tag of the prod Postgres image.", "registry.example.com/kudos-db:1.4.0"),
        "DOCKER_BUILD_MODE": v("(unset)", "Makefile", "`make prod` sets it to `prod` for the build.", "prod"),
    }),
    ("Container entrypoints and image build", "`docker/entrypoint.sh` (dev), `docker/entrypoint.prod.sh`, `docker/Dockerfile`.", {
        "SETUP_ENV": v("0", "app (dev)", "`1` makes the dev app container the single writer of `codes/.env` (merging `app.env.example` then `app.env`, generating APP_KEY). Set in compose for `app` only; queue and vite wait for the file.", "1"),
        "RUN_MIGRATIONS": v("0", "app", "`1` runs `php artisan migrate --force` (and the dev entrypoint also seeds) at start.", "1"),
        "NAME_FILE (any)": v("(unset)", "app, queue, scheduler, db", "Docker-secret convention of `entrypoint.prod.sh`: for every variable ending in `_FILE`, the file's contents become the variable without the suffix. Used for `DB_PASSWORD_FILE` and `POSTGRES_PASSWORD_FILE`; works for `STRIPE_SECRET_FILE`, `APP_KEY_FILE` and so on.", "STRIPE_SECRET_FILE=/run/secrets/stripe_secret", True),
        "GIT_SHA": v("(empty)", "build, compose", "Build ARG of the prod image: the commit id baked into `APP_COMMIT`. `make prod` sets it from `git rev-parse --short HEAD`.", "a1b2c3d"),
        "NGINX_ENVSUBST_FILTER": v("^OUTAGE_", "edge", "Image setting: only `OUTAGE_*` variables are substituted into the nginx template, so nginx's own `$variables` stay intact.", "^OUTAGE_"),
        "PHP_IMAGE, NODE_IMAGE, NGINX_IMAGE, POSTGRES_IMAGE": v("php:8.5-fpm-alpine, node:26-alpine, nginxinc/nginx-unprivileged:1.31-alpine, postgres:18-alpine", "build", "Docker build ARGs: base images. Defaults are in the Dockerfile; override with `--build-arg`.", "--build-arg NODE_IMAGE=node:26-alpine"),
        "VITE_APP_NAME": v("Kudos", "vite, build", "Frontend app name (import.meta.env), used in the page title fallback.", "Kudos"),
        "VITE_DEV_ORIGIN": v("http://localhost:${VITE_PORT}", "vite (dev)", "Origin the Vite dev server advertises to the browser (set by compose on the vite service).", "http://localhost:5180"),
    }),
]

# one-line meaning for the auto-listed "other settings", by name prefix (first match wins)
OTHER_NOTES = [
    ("REDIS_", "Redis connection. Not used: cache, queue and sessions live in Postgres."),
    ("MEMCACHED_", "Memcached cache store. Not used."),
    ("DYNAMODB_", "DynamoDB cache store. Not used."),
    ("AWS_", "AWS credentials and S3 disk. Not used: uploads go to the local public disk."),
    ("SQS_", "SQS queue. Not used."),
    ("BEANSTALKD_", "Beanstalkd queue. Not used."),
    ("DB_QUEUE", "Database queue driver table and retry settings (stock Laravel)."),
    ("DB_CACHE", "Database cache driver table and lock settings (stock Laravel)."),
    ("DB_", "Stock database driver option."),
    ("MYSQL_", "MySQL SSL option. Not used."),
    ("SESSION_", "Stock session option."),
    ("AUTH_", "Stock authentication option."),
    ("MAIL_", "Stock mail option."),
    ("LOG_", "Stock log channel option (Slack, Papertrail, syslog, daily rotation)."),
    ("PAPERTRAIL_", "Papertrail log channel. Not used."),
    ("SLACK_", "Slack notification credentials. Not used."),
    ("POSTMARK_", "Postmark mail transport. Not used."),
    ("RESEND_", "Resend mail transport. Not used."),
    ("CACHE_", "Stock cache option."),
    ("QUEUE_", "Stock queue option."),
    ("FILESYSTEM_", "Default filesystem disk."),
    ("APP_", "Stock application option."),
]
SECRET_HINTS = ("PASSWORD", "SECRET", "TOKEN", "KEY", "WEBHOOK_URL", "_URL")
SECRET_EXACT_NOT = {"APP_URL", "AWS_URL", "MAIL_URL_X", "REDIS_URL_X"}

# the 3 rate-limit zones etc. documented elsewhere; nothing else to curate here
