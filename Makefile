# Everything Docker lives in docker/. `make dev` (bind-mounted, hot reload) or `make prod` (immutable images).
DC      = docker compose -f docker/docker-compose.yml
DC_PROD = docker compose -f docker/docker-compose.yml -f docker/docker-compose.prod.yml

.PHONY: dev prod down migrate test lint types logs
dev:
	$(DC) up -d --build
prod:
	@test -f docker/.envs/app.prod.env || { echo "create docker/.envs/app.prod.env from app.prod.env.example"; exit 1; }
	DOCKER_BUILD_MODE=prod $(DC_PROD) up -d --build
down:
	$(DC) down
migrate:
	$(DC_PROD) exec app php artisan migrate --force
test:
	$(DC) exec -T app php artisan test --compact
lint:
	$(DC) exec -T app vendor/bin/pint --test && $(DC) exec -T app vendor/bin/phpstan analyse --memory-limit=1G
types:
	$(DC) exec -T vite npm run types
logs:
	$(DC) logs -f --tail 100
