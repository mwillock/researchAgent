from typing import Optional
from fastapi import FastAPI
from app.core.setting import settings
from app.core.logging import setup_logging
from app.routers import meta
from app.middlewares.observability import request_id_and_timing_mw
from fastapi.middleware.cors import CORSMiddleware


ollama_ok: Optional[bool] = None
# Update Project name
app = FastAPI(title="Research Assistant", debug=settings.debug)


def create_app() -> FastAPI:
    setup_logging(settings.log_level)
    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url] if settings.frontend_url else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(request_id_and_timing_mw)
    app.include_router(meta.router)

    @app.get("/health")
    def health():
        return {
            "ok": True,
            "ollama_url": str(settings.ollama_url),
            "model_general": settings.model_general,
            "model_code": settings.model_code,
        }

    return app


app = create_app()

"""  async def _check_ollama(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=1.5) as client:
            r = await client.get(url.rstrip('/') + "/api/tags")
            return r.status_code // 100 == 2
    except Exception:
        return False

@app.on_event("startup")
async def _startup():
    global ollama_ok
    ollama_ok = await _check_ollama(settings.ollama_url)

#patch /ready to use at current state
@meta.router.get("/ready")
async def ready():
    global ollama_ok
    if ollama_ok is None:
        # probe once if not checked yet
        ollama_ok = await _check_ollama(settings.ollama_url)
    return {"ok": bool(ollama_ok), "deps": {"ollama": bool(ollama_ok)}}   """
