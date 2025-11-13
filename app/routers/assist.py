from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.llm import generate_code

router = APIRouter(prefix="/assist", tags=["assist"])

SYSTEM_CODE = (
    # This is subject to change as we experiment
    "You are a senior code assistant. Output minimal, correct code with a brief rationale "
    "and a tiny usage example. State assumptions explicitly when paths/APIs are unknown."
)


class ExplainRequest(BaseModel):
    code: str


@router.post("/explain")
async def explain(
    payload: ExplainRequest,
    mock: bool = Query(
        False, description="If true, return a mock response instead of calling LLM"
    ),
):
    """Explain what a peiece of code does, highlighting bugs/edge cases, and suggest for safer solutions.
    Request body:
    {
        "code": "print('Hello, world!')"
    }
    """
    # Basic Guard: Empty code is a Client Error
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")

    # Fast path for health checks/ testing
    if mock:
        return {
            "ok": True,
            "result": {
                "explanation": "This function takes two numbers a & b and return their sums.",
                "notes": "Mock response - no real LLM call made",
            },
        }

    prompt = (
        f"{SYSTEM_CODE}\n\n"
        f"Explain what this code does, list likely bugs/edge cases,"
        "then provide safer solutions:\n\n"
        f"```python\n{payload.code}\n```"
    )
    try:
        # generate code can be sync; FASTAPI is fine calling it here
        result = generate_code(prompt)
    except Exception as exc:
        # Keep the surface clean; log details internally
        raise HTTPException(status_code=502, detail="LLM backend error: {exc}") from exc

    return {"ok": True, "result": result}
