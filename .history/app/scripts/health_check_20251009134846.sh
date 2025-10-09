#!/usr/bin/env bash
set -euo pipefail


HOST="${APP_HOST:-127.0.0.1}"
PORT="${APP_PORT:-8000}"

echo "[HEALTH] Checking FastAPI  on http://${HOST}:${PORT}""

# /Heath returns 200 with {"ok": "true"}
if ! curl -fsS "http://${HOST}:${PORT}/health" | grep -qi '"ok":\s*true'; then
  echo "[HEALTH:FAIL] FastAPI is not healthy"
  exit 2
fi

echo "[HEALTH:OK] FastAPI is healthy"

# Check if AI route is presentent
if curl -fsS "http://${HOST}:${PORT}/assist/explain?mock=1" >/dev/null 2>&1; then
    echo "[HEALTH] /assist/explain reachable (mock=1)"