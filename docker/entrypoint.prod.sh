#!/bin/sh
# Prod entrypoint: configuration comes from the container environment (docker/.envs/*.env), never a baked .env.
set -e
cd /app

# Docker secrets: any NAME_FILE=/path variable becomes NAME=<file contents> (DB_PASSWORD_FILE, STRIPE_SECRET_FILE, ...)
for var in $(env | sed -n 's/^\([A-Z0-9_]*_FILE\)=.*/\1/p'); do
  name="${var%_FILE}"
  file="$(printenv "$var")"
  if [ -r "$file" ]; then
    export "$name=$(cat "$file")"
  fi
done
if [ "${APP_ROLE:-web}" = "web" ]; then
  php artisan config:cache
  php artisan route:cache
  php artisan view:cache
  php artisan event:cache
  # Migrations are explicit in prod: `make migrate`. Set RUN_MIGRATIONS=1 only for first boot.
  if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then php artisan migrate --force; fi
  [ -L public/storage ] || php artisan storage:link || true
fi
exec "$@"
