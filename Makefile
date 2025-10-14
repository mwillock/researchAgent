PY:= python3
VENV:= .venv
PIP:= $(VENV)/bin/pip
UVICORN:= $(VENV)/bin/uvicorn
PRECOMMIT:= $(VENV)/bin/pre-commit
RUF:= $(VENV)/bin/ruff
BLK:= $(VENV)/bin/black
MYPY:= $(VENV)/bin/mypy
PYTEST:= $(VENV)/bin/pytest

CODEPATHS := app scripts

APP_MODULE := app.main:app
# Resolve at runtime with safe defaults (shell expands values after sourcing .env)
RUNTIME_HOST = $${APP_HOST:-127.0.0.1}
RUNTIME_PORT = $${APP_PORT:-8000}

#Default host and target incase not avaliable in env
#HOST ?=
#PORT ?=

#Phony targets
.PHONY: help setup venv install hooks fmt lint type test run dev stop check env-validate health ports kill freeze clean


help:
	@echo "Top commands:"
	@echo " make setup						# venv+ deps+pre-commit"
	@echo " make dev 						# run uvicorn with reload"
	@echo " make check						# fmt+ lint+ type+ env-validate+ health"
	@echo " make health						# curl/health and basic route checks"
	@echo " make stop						# terminates process"

setup: venv install hooks

venv:
	@test -d $(VENV) || $(PY) -m venv $(VENV)
	@echo "[(venv) ready]"

install:
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	$(PIP) install black ruff mypy pytest pre-commit python-dotenv

hooks:
	$(PRECOMMIT) install
fmt:
	$(BLK) $(CODEPATHS)
lint:
	$(RUF) $(CODEPATHS)
type:
	$(MYPY) $(CODEPATHS) || true
test:
	$(PYTEST) $(CODEPATHS) || true
run:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	$(UVICORN) $(APP_MODULE) --host $(RUNTIME_HOST) --port $(RUNTIME_PORT)
dev:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	$(UVICORN) $(APP_MODULE) --reload --host $(RUNTIME_HOST) --port $(RUNTIME_PORT)
stop:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	PORT=$(RUNTIME_PORT); \
	lsof -ti tcp:$$PORT | xargs -r kill

check: fmt lint type test env-validate health

env-validate:
	# Load .env if present, then run validator
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	$(PY) scripts/validate_config.py

health:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	bash scripts/health_check.sh

ports:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	PORT=$(RUNTIME_PORT); \
	echo "Listening processes on :$$PORT"; lsof -i :$$PORT || true

kill:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	PORT=$(RUNTIME_PORT); \
	echo "Killing processes on :$$PORT"; lsof -ti :$$PORT | xargs -r kill

freeze:
	$(PIP) freeze > requirements.lock.txt

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache .ruff_cache
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +
