#!/bin/sh
# Prod entrypoint: configuration comes from the container environment (docker/.envs/*.env), never a baked .env.
set -e
cd /app
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
