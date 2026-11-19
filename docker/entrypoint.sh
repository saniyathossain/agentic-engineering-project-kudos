#!/bin/bash
# Dev entrypoint. The bind-mounted codes/.env is shared by app, queue and vite, so exactly one container
# (the one with SETUP_ENV=1, the app) writes it, atomically; the others wait for it. flock is not reliable
# across containers on bind mounts, so no lock is used.
set -e
cd /app
if [ ! -f artisan ]; then
  echo "No Laravel app in /app (codes/). Scaffold it first."; exec "$@"
fi

# each service has its own vendor volume: reinstall whenever composer.lock changed since that volume was filled
lock_hash="$(md5sum composer.lock | cut -d' ' -f1)"
if [ ! -f vendor/autoload.php ] || [ "$(cat vendor/.lock-hash 2>/dev/null)" != "$lock_hash" ]; then
  composer install --no-interaction --prefer-dist
  echo "$lock_hash" > vendor/.lock-hash
fi

setup_env() {
  local current=".env"
  [ -f "$current" ] || current=".env.example"
  cp "$current" .env.new
  # defaults first (app.env.example), then the user's app.env on top
  for envfile in /run/app.defaults.env /run/app.env; do
    [ -f "$envfile" ] || continue
    while IFS= read -r line; do
      case "$line" in ''|\#*) continue ;; esac
      key="${line%%=*}"; val="${line#*=}"
      if grep -q "^${key}=" .env.new; then
        awk -v k="$key" -v v="$val" 'BEGIN{FS=OFS="="} $1==k{print k"="v; next} {print}' .env.new > .env.tmp && mv .env.tmp .env.new
      else
        printf '%s=%s\n' "$key" "$val" >> .env.new
      fi
    done < "$envfile"
  done
  if ! grep -q '^APP_KEY=.\+' .env.new; then
    key="base64:$(php -r 'echo base64_encode(random_bytes(32));')"
    if grep -q '^APP_KEY=' .env.new; then
      awk -v v="$key" 'BEGIN{FS=OFS="="} $1=="APP_KEY"{print "APP_KEY="v; next} {print}' .env.new > .env.tmp && mv .env.tmp .env.new
    else
      printf 'APP_KEY=%s\n' "$key" >> .env.new
    fi
  fi
  mv .env.new .env   # atomic: readers never see a half-written file
}

if [ "${SETUP_ENV:-0}" = "1" ]; then
  setup_env
else
  for _ in $(seq 1 60); do
    grep -q '^APP_KEY=.\+' .env 2>/dev/null && break
    sleep 1
  done
fi

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  until php artisan migrate --force 2>/dev/null; do echo "waiting for db..."; sleep 2; done
  php artisan db:seed --force || echo "seed skipped"
fi
# compiled views embed the Blade directives of the installed packages: drop them so an upgrade cannot leave stale ones
php artisan view:clear >/dev/null
php artisan lang:export-status >/dev/null
[ -L public/storage ] || php artisan storage:link
exec "$@"
