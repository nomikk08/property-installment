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

down-prod:
	docker compose -f docker-compose.prod.yml down

logs-prod:
	docker compose -f docker-compose.prod.yml logs -f

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
	$(MANAGE) "python manage.py import_plots plots-data/plots.csv"