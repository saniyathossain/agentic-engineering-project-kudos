# syntax=docker/dockerfile:1.7
# Targets: dev (bind-mounted code, artisan serve) | prod (immutable php-fpm image) | edge (unprivileged nginx).
# `make dev` / `make prod` pick one. The prod image carries no composer, git, node or build toolchain.
ARG PHP_IMAGE=php:8.5-fpm-alpine
ARG NODE_IMAGE=node:26-alpine
ARG NGINX_IMAGE=nginxinc/nginx-unprivileged:1.31-alpine
ARG POSTGRES_IMAGE=postgres:18-alpine

# ---- runtime: php-fpm plus the extensions the app needs, nothing else ---------------------------------------
FROM ${PHP_IMAGE} AS runtime
RUN apk upgrade --no-cache \
    && apk add --no-cache icu-libs libpng libjpeg-turbo freetype libzip libpq \
    && apk add --no-cache --virtual .build icu-dev libpng-dev libjpeg-turbo-dev freetype-dev libzip-dev postgresql-dev oniguruma-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" pdo_pgsql intl gd zip bcmath pcntl \
    && apk del .build \
    && rm -rf /tmp/* /var/cache/apk/*
WORKDIR /app

# ---- tools: runtime + composer and git, used to build vendor and by the dev image only ---------------------
FROM runtime AS tools
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
RUN apk add --no-cache git unzip

# ---- dev ---------------------------------------------------------------------------------------------------
FROM tools AS dev
RUN apk add --no-cache bash curl
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["entrypoint.sh"]
CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]

# ---- prod build stages -------------------------------------------------------------------------------------
FROM tools AS vendor
COPY codes/composer.json codes/composer.lock ./
RUN --mount=type=cache,target=/root/.composer/cache \
    composer install --no-dev --no-scripts --no-autoloader --prefer-dist --no-interaction
COPY codes/ .
RUN composer dump-autoload --optimize --classmap-authoritative --no-dev --no-scripts \
    && php artisan package:discover --ansi \
    && php artisan lang:export-status \
    && rm -rf tests database/factories

FROM ${NODE_IMAGE} AS assets
WORKDIR /app
COPY codes/package.json codes/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --no-audit --no-fund
COPY codes/ .
COPY --from=vendor /app/vendor ./vendor
RUN npm run build

# ---- prod --------------------------------------------------------------------------------------------------
FROM runtime AS prod
LABEL org.opencontainers.image.title="kudos-app" org.opencontainers.image.description="Kudos php-fpm application image"
ARG GIT_SHA=
ARG APP_VERSION=dev
ENV APP_ENV=production APP_DEBUG=false APP_COMMIT=${GIT_SHA} APP_VERSION=${APP_VERSION}
COPY docker/php/php-prod.ini /usr/local/etc/php/conf.d/zz-prod.ini
COPY docker/php/www.conf /usr/local/etc/php-fpm.d/zz-www.conf
COPY --chmod=0755 docker/entrypoint.prod.sh /usr/local/bin/entrypoint.sh
# application code is owned by root and read-only to the app user; only storage and the cache directory are writable
COPY --from=vendor --chown=0:0 /app /app
COPY --from=assets --chown=0:0 /app/public/build /app/public/build
RUN mkdir -p storage/framework/cache storage/framework/sessions storage/framework/views storage/logs bootstrap/cache \
    && chown -R 82:82 storage bootstrap/cache \
    && chmod -R go-w,a+rX /app   # normalise modes: host files may be 0600, the app user must still read them
USER 82:82
STOPSIGNAL SIGQUIT
EXPOSE 9000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD php-fpm -t >/dev/null 2>&1 || exit 1
ENTRYPOINT ["entrypoint.sh"]
CMD ["php-fpm", "-F"]

# ---- edge (nginx, runs as an unprivileged user, public dir baked in) ---------------------------------------
FROM ${NGINX_IMAGE} AS edge
# the base image lags behind Alpine's security fixes: patch it, then return to the unprivileged user
USER root
RUN apk upgrade --no-cache
USER 101
# only OUTAGE_* variables are substituted into the template; nginx's own $variables stay untouched
ENV NGINX_ENVSUBST_FILTER=^OUTAGE_ OUTAGE_FIRST_MS=4000 OUTAGE_LONGEST_MS=15000
COPY --chmod=0755 docker/nginx/default.conf.template /etc/nginx/templates/default.conf.template
COPY --chmod=0755 docker/nginx/snippets/fastcgi-app.conf /etc/nginx/snippets/fastcgi-app.conf
COPY --chmod=0755 docker/nginx/10-outage-defaults.envsh /docker-entrypoint.d/10-outage-defaults.envsh
COPY --from=prod /app/public /var/www/public
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD wget -qO- http://127.0.0.1:8080/healthz >/dev/null || exit 1

# ---- db (PostgreSQL without gosu, run directly as the postgres user: no root, no capabilities) ----------------
# The stock image starts as root and drops privileges with a gosu binary built with an old Go toolchain (many CVEs).
# Started as `postgres` the entrypoint never calls gosu, so the binary is removed. Patch OS packages as well.
FROM ${POSTGRES_IMAGE} AS db
USER root
RUN apk upgrade --no-cache && rm -f /usr/local/bin/gosu
USER postgres
HEALTHCHECK --interval=10s --timeout=5s --retries=10 CMD pg_isready -q -U "${POSTGRES_USER:-postgres}" || exit 1
