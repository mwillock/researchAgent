from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.llm import generate_code

router = APIRouter(prefix="/assist", tags=["assist"])

SYSTEM_CODE = (
    # This is subject to change as we experiment
    "You are a senior code assistant. Output minimal, correct code with a brief rationale "
    "and a tiny usage example. State assumptions explicitly when paths/APIs are unknown."
)

SYSTEM_REVIEW_DIFF = (
    "You are a senior code reviewer. Given a code snippet and its modified version, "
    "1) Summariaze the change made. \n"
    "2) List issues, risk ad bugs as bullet points. \n"
    "3) Provide a fix different that preseves intent but improves safety, reliability and security. \n"
    "Output is Markdown"
)

SYSTEM_DOCSTRINGS = (
    "You are a Python documentation assistant. Given code snippets, you will:\n"
    "1) Add or improve docstrings in the requested style (e.g. Google, NumPy).\n"
    "2) Do no change behavior unless you see a clear bug.\n"
    "3) Return the final annotated code block in Markdown."
)

SYSTEM_TEST = (
    "You are a senior test engineer. Given code a short spec, you will:\n"
    "1) Identify key behaviors and edge cases.\n"
    "2) Write runnable test in the requested framework (default:pytest).\n"
    "3) Keep tests focused and deterministic.\n"
    "Output test case in a single code block, and brief notes"
)


# -------------- Request Models --------------
class ExplainRequest(BaseModel):
    code: str


class ReviewDiffRequest(BaseModel):
    diff: str
    context: Optional[str] = None  # e.g., repo, file, or intent


class DocstringsRequest(BaseModel):
    snippets: list[str]  # list of python code snippets
    style: Optional[str] = "numpy"  # or "google", "pep257", etc.


class TestRequest(BaseModel):
    code: str
    spec: Optional[str] = None
    framework: str = "pytest"  # you can extend later (unittest, etc.)


# ---------- Helper: shared LLM caller ----------
def _call_llm(task: str, prompt: str, mock: bool) -> dict:
    """
    Shared helper: either return a mock result or calls generate_code(prompt)
    and wraps it in the standard envelope.
    """
    if mock:
        # Simple, deterministic mock payload on test/health check are stable
        return {
            "ok": True,
            "task": task,
            "result": {
                "summary": f"[mock] {task} completed successfully.",
                "details": "[mock] No real LLM call was made",
            },
        }
    try:
        # generate_code should return a string (e.g. Markdown or plain text)
        lllm_output = generate_code(prompt)
    except Exception as exc:
        # Keep errors structured
        raise HTTPException(
            status_code=502, detail=f"LLM backend error: {exc}"
        ) from exc

    return {
        "ok": True,
        "task": task,
        "result": {
            "raw": lllm_output  # raw model output; you can parse/structure later if needed
        },
    }


# ---------------- Endpoints -----------------
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
