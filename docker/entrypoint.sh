#!/bin/bash
set -e
cd /app
if [ ! -f artisan ]; then
  echo "No Laravel app in /app (codes/). Scaffold it first."; exec "$@"
fi

setup_env() {
  [ -f vendor/autoload.php ] || composer install --no-interaction --prefer-dist
  [ -f .env ] || cp .env.example .env
  # artisan serve ignores container env, so merge docker/.envs/app.env into .env
  if [ -f /run/app.env ]; then
    while IFS= read -r line; do
      case "$line" in ''|\#*) continue ;; esac
      key="${line%%=*}"; val="${line#*=}"
      if grep -q "^${key}=" .env; then
        awk -v k="$key" -v v="$val" 'BEGIN{FS=OFS="="} $1==k{print k"="v; next} {print}' .env > .env.tmp && cat .env.tmp > .env && rm -f .env.tmp
      else
        printf '%s=%s\n' "$key" "$val" >> .env
      fi
    done < /run/app.env
  fi
  grep -q '^APP_KEY=.\+' .env || php artisan key:generate --force
}

# app/queue/vite start together on a shared bind mount: serialize setup
exec 9>/app/.setup.lock
flock 9
setup_env
flock -u 9

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  until php artisan migrate --force 2>/dev/null; do echo "waiting for db..."; sleep 2; done
  php artisan db:seed --force || echo "seed skipped"
fi
[ -L public/storage ] || php artisan storage:link
exec "$@"
