# Resolve HOST/PORT from env at runtime with safe defaults
RUNTIME_HOST = ${APP_HOST:-127.0.0.1}
RUNTIME_PORT = ${APP_PORT:-8000}

...

run:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	$(UVICORN) $(APP_MODULE) --host $(RUNTIME_HOST) --port $(RUNTIME_PORT)

...

dev:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	$(UVICORN) $(APP_MODULE) --reload --host $(RUNTIME_HOST) --port $(RUNTIME_PORT)

...

stop:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	PORT=$(RUNTIME_PORT); \
	lsof -ti tcp:$$PORT | xargs -r kill

...

ports:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	PORT=$(RUNTIME_PORT); \
	echo "Listening processes on :$$PORT"; lsof -i :$$PORT || true

...

kill:
	@set -a; [ -f .env ] && . ./.env || true; set +a; \
	PORT=$(RUNTIME_PORT); \
	echo "Killing processes on :$PORT"; lsof -ti :$PORT | xargs -r kill


#!/usr/bin/env bash
set -euo pipefail


HOST="${APP_HOST:-127.0.0.1}"
PORT="${APP_PORT:-8000}"

echo "[HEALTH] Checking FastAPI on http://${HOST}:${PORT}"

# /health should return 200 with {"ok": true}
if ! curl -fsS "http://${HOST}:${PORT}/health" | grep -qi '"ok":[[:space:]]*true'; then
  echo "[HEALTH:FAIL] /health did not report ok:true"
  exit 2
fi

echo "[HEALTH:OK] FastAPI is healthy"

# Optional: check AI route if present
if curl -fsS "http://${HOST}:${PORT}/assist/explain?mock=1" >/dev/null 2>&1; then
  echo "[HEALTH] /assist/explain reachable (mock=1)"
fi
