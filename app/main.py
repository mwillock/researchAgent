from fastapi import FastAPI
from app.core.setting import settings
from app.routers.assist import router as assist_router

app = FastAPI(title="Research Assistant", debug=settings.debug)


@app.get("/health")
def health():
    return {
        "ok": True,
        "ollama_url": str(settings.ollama_url),
        "model_general": settings.model_general,
        "model_code": settings.model_code,
    }


app.include_router(assist_router)
