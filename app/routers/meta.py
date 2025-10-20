from fastapi import APIRouter

router = APIRouter(tags=["meta"])


@router.get("/live")
def live():
    return {"ok": True}


@router.get("/ready")
def ready():
    return {"ok": True, "deps": {"ollama": "unchecked"}}
