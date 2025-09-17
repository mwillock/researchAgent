# Uses `docker compose` if available; otherwise falls back to `docker-compose`.
DOCKER_COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

# Env file used by docker compose for interpolation and runtime
ENV_FILE ?= .env
COMPOSE_ENV := --env-file $(ENV_FILE)

# -------- Compose files --------
COMPOSE_DEV := -f compose/compose.base.yml \
               -f compose/compose.db.yml \
               -f compose/compose.ollama.yml \
               -f compose/compose.dev.yml

COMPOSE_PROD := -f compose/compose.base.yml \
                -f compose/compose.db.yml \
                -f compose/compose.ollama.yml \
                -f compose/compose.prod.yml

# Default goal (runs if you just type `make`)
.DEFAULT_GOAL := up-dev

# -------- Targets --------
.PHONY: up-dev down-dev logs-dev ps-dev rebuild-dev restart \
        up-prod down-prod logs-prod ps-prod \
        api-shell db-shell prune status help

up-dev:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) up -d

down-dev:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) down

logs-dev:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) logs -f

ps-dev:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) ps

status-dev:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) ps
	curl -s localhost:8000/health || true

rebuild-dev:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) build --no-cache
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) up -d

# Generic restart for dev
restart: down-dev up-dev

# ---- prod variants (adjust files/services as you like) ----
up-prod:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_PROD) up -d

down-prod:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_PROD) down

logs-prod:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_PROD) logs -f

ps-prod:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_PROD) ps

# ---- shells (adapt service names if different) ----
api-shell:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) exec api sh -lc "bash || sh"

db-shell:
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) exec db psql -U $$POSTGRES_USER -d $$POSTGRES_DB

# ---- housekeeping ----
prune:
	docker system prune -af --volumes

status:
	@echo "Compose binary: $(DOCKER_COMPOSE)"
	@echo "Env file: $(ENV_FILE)"
	$(DOCKER_COMPOSE) $(COMPOSE_ENV) $(COMPOSE_DEV) ps

help:
	@echo "Targets:"
	@echo "  up-dev, down-dev, logs-dev, ps-dev, rebuild-dev, restart"
	@echo "  up-prod, down-prod, logs-prod, ps-prod"
	@echo "  api-shell, db-shell, prune, status"
	@echo "  Tip: override ENV_FILE, e.g., make up-dev ENV_FILE=.env.dev"