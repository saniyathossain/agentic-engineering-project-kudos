# syntax=docker/dockerfile:1
# Targets: dev (bind-mounted code, artisan serve) | prod (immutable php-fpm image).
# `make dev` / `make prod` pick one; DOCKER_BUILD_MODE mirrors the other projects' convention.
ARG PHP_IMAGE=php:8.4-fpm-alpine
ARG NODE_IMAGE=node:22-alpine

FROM ${PHP_IMAGE} AS base
RUN apk add --no-cache bash icu-libs libpng libjpeg-turbo freetype libzip libpq \
    && apk add --no-cache --virtual .build icu-dev libpng-dev libjpeg-turbo-dev freetype-dev libzip-dev postgresql-dev oniguruma-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j"$(nproc)" pdo_pgsql intl gd zip bcmath pcntl opcache \
    && apk del .build
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer
WORKDIR /app

# ---- dev -------------------------------------------------------------------
FROM base AS dev
RUN apk add --no-cache git unzip curl nodejs npm
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
EXPOSE 8000
ENTRYPOINT ["entrypoint.sh"]
CMD ["php", "artisan", "serve", "--host=0.0.0.0", "--port=8000"]

# ---- prod build stages ------------------------------------------------------
FROM base AS vendor
COPY codes/composer.json codes/composer.lock ./
RUN composer install --no-dev --no-scripts --no-autoloader --prefer-dist --no-interaction
COPY codes/ .
RUN composer dump-autoload --optimize --classmap-authoritative --no-dev --no-scripts \
    && php artisan package:discover --ansi

FROM ${NODE_IMAGE} AS assets
WORKDIR /app
COPY codes/package.json codes/package-lock.json ./
RUN npm ci
COPY codes/ .
COPY --from=vendor /app/vendor ./vendor
RUN npm run build

# ---- prod --------------------------------------------------------------------
FROM base AS prod
ENV APP_ENV=production APP_DEBUG=false
COPY docker/php/php-prod.ini /usr/local/etc/php/conf.d/zz-prod.ini
COPY docker/php/www.conf /usr/local/etc/php-fpm.d/zz-www.conf
COPY docker/entrypoint.prod.sh /usr/local/bin/entrypoint.sh
COPY --from=vendor --chown=82:82 /app /app
COPY --from=assets --chown=82:82 /app/public/build /app/public/build
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && mkdir -p storage/framework/{cache,sessions,views} storage/logs bootstrap/cache \
    && chown -R 82:82 storage bootstrap/cache
USER 82:82
EXPOSE 9000
ENTRYPOINT ["entrypoint.sh"]
CMD ["php-fpm", "-F"]

# ---- edge (nginx with the public dir baked in) -------------------------------
FROM nginx:1.27-alpine AS edge
COPY docker/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=prod /app/public /var/www/public
