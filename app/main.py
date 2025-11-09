"""
FastAPI entrypoint with:
- Env-driven config (title, debug, CORS) via app.core.setting.Settings
- JSON logging (inline) so logs are machine-parsable
- Request observability middleware (X-Request-ID, X-Elapsed-ms)
- Health probes: /live, /health, /ready (Ollama dependency check)
- Safe optional router include for assist module

This file is intentionally self-contained (no hard dependency on app.core.logging
or routers.meta). You can swap inline pieces for your dedicated modules later.
"""

from __future__ import annotations

import json
import logging
import time
import httpx
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from app.middlewares.observability import request_id_and_timing_mw
from fastapi.middleware.cors import CORSMiddleware
from app.core.setting import settings
from app.core.logging import setup_logging
from app.routers import meta
from app.errors import http_error_handler
from starlette.responses import Response


# ----------------------------- JSON Logging  ----------------------------
class _JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "time": int(time.time() * 1000),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

    def _setup_logging(level: str = "INFO") -> None:
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel((level or "INFO").upper())
        handler = logging.StreamHandler()
        handler.setFormatter(_JSONFormatter())
        root.addHandler(handler)


# ------------- Request observability: ID + latency headers ----------------
"""
REQUEST_ID_HDR = "X-Request-ID"


 async def request_id_and_timing_mw(request: Request, call_next):
    rid = request.headers.get(REQUEST_ID_HDR, str(uuid.uuid4()))
    start = time.perf_counter()
    response: Response | None = None
    try:
        response = await call_next(request)
        return response
    finally:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        if response is not None:
            response = Response(status_code=500)
        response.headers[REQUEST_ID_HDR] = rid
        response.headers["X-Elapsed-ms"] = str(elapsed_ms)
        request.app.logger.info(
            f"{request.method} {request.url.path} -> "
            f"{getattr(response, 'status_code', '?')} in {elapsed_ms}"
        )
 """

# -------------------  Ollama readiness Probe -----------------------
ollama_ok: Optional[bool] = None


async def _check_ollama(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            r = await client.get(url.rstrip("/") + "/api/tags")
            return r.status_code // 100 == 2
    except Exception:
        return False


# app = FastAPI(title="Research Assistant", debug=settings.debug)


# --------------------- FastAPI App Factory ------------------------
def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.logger = logging.getLogger("app")
    origin = getattr(settings, "frontend_url", None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin] if origin else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Observability Middlewares
    app.middleware("http")(request_id_and_timing_mw)
    app.include_router(meta.router)

    # -------------------- Core Probes ------------------------
    @app.get("/live")
    def live():
        # Simple liveness probe
        return {"ok": True}

    @app.get("/health")
    def health():
        # Simple health probe
        return {
            "ok": True,
            "ollama_url": str(settings.ollama_url),
            "model_general": settings.model_general,
            "model_code": settings.model_code,
        }

    @app.get("/ready")
    async def ready():
        # patch /ready to use at current state
        global ollama_ok
        if ollama_ok is None:
            # probe once if not checked yet
            ollama_ok = await _check_ollama(str(settings.ollama_url))

    return {"ok": bool(ollama_ok), "deps": {"ollama": bool(ollama_ok)}}

    # ---------------------  Exception Handlers ------------------------
    class ErrorResponse(Response):
        media_type = "application/json"

        def __init__(self, status_code: int, code: str, message: str):
            super().__init__(
                content=json.dumps(
                    {"ok": False, "error": {"code": code, "message": message}}
                ),
                status_code=status_code,
            )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request, exc):
        return ErrorResponse(422, "validation_error", str(exc))

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        return ErrorResponse(exc.status_code, "http_error", exc.detail)

    @app.exception_handler(Exception)
    async def fallback_handler(request, exc):
        return http_error_handler(request, exc)

    # Startup hoo to warm ollama status
    @app.on_event("startup")
    async def on_startup():
        global ollama_ok
        ollama_ok = await _check_ollama(str(settings.ollama_url))

    return app


app = create_app()
