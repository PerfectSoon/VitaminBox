SERVICE ?= backend
MIGRATION_MSG ?= "auto migration"

help:
	@echo "Usage:"
	@echo "  make up                   # start containers"
	@echo "  make build                   # Build & start containers"
	@echo "  make down                 # Stop & remove containers"
	@echo "  make migrate-create MSG=\"Your message\""
	@echo "                           # Create a new Alembic migration"
	@echo "  make migrate-upgrade      # Apply migrations (upgrade to head)"
	@echo "  make migrate-history      # Show migration history"
	@echo "  make test                 # Run pytest in the backend container"

up:
	docker-compose up

build:
	docker-compose up -d --build

down:
	docker-compose down

migrate-create:
ifndef MSG
	$(error MSG is undefined. Usage: make migrate-create MSG=MIGRATION_MSG)
endif
	docker-compose exec $(SERVICE) \
		alembic revision --autogenerate -m "$(MSG)"

migrate-upgrade:
	docker-compose exec $(SERVICE) \
		alembic upgrade head

migrate-history:
	docker-compose exec $(SERVICE) \
		alembic history --verbose

test:
	docker-compose exec $(SERVICE) \
		pytest --maxfail=1 --disable-warnings -q
