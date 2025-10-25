#variables
MANAGE = docker compose run --rm web python manage.py wait_for_db --cmd

install: build migrate createsuperuser

build:
	docker compose --progress=plain build

run:
	docker compose up --remove-orphans

down:
	docker compose down

destroy:
	docker compose down -v

logs:
	docker compose logs -f web

# Production targets
build-prod:
	docker compose -f docker-compose.prod.yml build --no-cache

up-prod:
	docker compose -f docker-compose.prod.yml up -d --remove-orphans

run-prod: up-prod migrate logs-prod

down-prod:
	docker compose -f docker-compose.prod.yml down

logs-prod:
	docker compose -f docker-compose.prod.yml logs -f

# Database backup & restore START
DB_RELOAD_COMMAND_BASE = pg_restore --username postgres --dbname db --schema public --exit-on-error --verbose --clean --if-exists --no-owner --format custom
DB_DUMP_COMMAND_BASE = pg_dump --username postgres --dbname db --format custom

dump-db:
	docker compose exec db bash -c '${DB_DUMP_COMMAND_BASE} -f /dev-doc/db-dumps/live.dump'

restore-db:
	docker compose exec db bash -c '${DB_RELOAD_COMMAND_BASE} /dev-doc/db-dumps/live.dump;'
# Database backup & restore END

shell:
	$(MANAGE) "python manage.py shell"

dbshell:
	$(MANAGE) "python manage.py dbshell"

migrate:
	$(MANAGE) "python manage.py migrate"

makemigrations:
	$(MANAGE) "python manage.py makemigrations"

createsuperuser:
	$(MANAGE) "python manage.py createsuperuser"

collectstatic:
	$(MANAGE) "python manage.py collectstatic --no-input"

tailwind:
	$(MANAGE) "python manage.py tailwind install"

add-plots:
	$(MANAGE) "python manage.py import_plots"