from fastapi import APIRouter
from app.services.llm import generate_code

router = APIRouter(prefix="/assist", tags=["assist"])

SYSTEM_CODE = (
    # This is subject to change as we experiment
    "You are a senior code assistant. Output minimal, correct code with a brief rationale "
    "and a tiny usage example. State assumptions explicitly when paths/APIs are unknown."
)


@router.post("/explain")
def explain(playload: dict):
    """
    Body:
        {
            "code": "print('hello')"
        }
    """

    code = playload.get("code", "")
    prompt = (
        f"{SYSTEM_CODE}\n\n"
        f"Explain what this code does, list likely bugs/edge cases then provide safer solutions:\n\n"
        f"```python\n{code}\n```"
    )
    result = generate_code(prompt)
    return {"result": result}
