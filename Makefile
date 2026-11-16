COMPOSE ?= docker compose
EXEC := $(COMPOSE) exec web uv run

.PHONY: up down logs migrate test lint import shell psql

up:
	$(COMPOSE) up -d --build
down:
	$(COMPOSE) down
logs:
	$(COMPOSE) logs -f web worker beat
migrate:
	$(EXEC) alembic upgrade head
test:
	$(EXEC) pytest
lint:
	$(EXEC) ruff check .
import:
	$(EXEC) jobskillgap import-all
import-%:
	$(EXEC) jobskillgap import $*
shell:
	$(COMPOSE) exec web bash
psql:
	$(COMPOSE) exec db psql -U postgres -d jobskillgap
