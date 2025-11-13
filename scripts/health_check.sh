#!/usr/bin/env bash

set -euo pipefail

# Resolve HOST/PORT from env at runtime with safe defaults

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
if curl -fsS -X POST "http://${HOST}:${PORT}/assist/explain?mock=1" \
  -H "Content-Type: application/json" \
  -d '{"code": "def add(a, b): return a + b"}' >/dev/null 2>&1; then
  echo "[HEALTH] /assist/explain reachable (mock=1)"
fi
