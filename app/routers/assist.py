from typing import Optional, Literal
from urllib import request
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.services.llm import generate_code
from app.prompt.loader import prompts

router = APIRouter(prefix="/assist", tags=["assist"])

SYSTEM_CODE = (
    # This is subject to change as we experiment
    "You are a senior code assistant. Output minimal, correct code with a brief rationale "
    "and a tiny usage example. State assumptions explicitly when paths/APIs are unknown."
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


# ___________ Request Models _________________


class ExplainRequest(BaseModel):
    code: str


class ReviewDiffRequest(BaseModel):
    diff: str
    context: Optional[str] = None


class DocstringsRequest(BaseModel):
    snippets: list[str]
    style: Optional[str]


class TestRequest(BaseModel):
    code: str
    spec: Optional[str] = None
    framework: str = "pytest"


# __________ Response Models _________________
class ExplainResult(BaseModel):
    summary: str
    explanation: str
    issues: str
    suggestions: str
    example: Optional[str] = None


class ExplainResponse(BaseModel):
    ok: bool = True
    task: Literal["explain"]
    result: ExplainResult


class ReviewDiffResult(BaseModel):
    summary: str
    issues: str
    suggested_diff: str
    notes: Optional[str] = None  # e.g., repo, file, or intent


class ReviewDiffResponse(BaseModel):
    ok: bool = True
    task: Literal["review-diff"]
    result: ReviewDiffResult


class DocstringsResult(BaseModel):
    summary: str  #
    annotated_code: str


class DocstringsResponse(BaseModel):
    ok: bool = True
    task: Literal["docstrings"]
    result: DocstringsResult


class TestResult(BaseModel):
    summary: str
    test_code: str
    notes: Optional[str] = None
    framework: str = "pytest"  # you can extend later (unittest, etc.)


class TestResponse(BaseModel):

    ok: bool = True
    task: Literal["tests"]
    result: TestResult


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
        llm_output = generate_code(prompt)
    except Exception as exc:
        # Keep errors structured
        raise HTTPException(
            status_code=502, detail=f"LLM backend error: {exc}"
        ) from exc

    return {
        "ok": True,
        "task": task,
        "result": {
            "raw": llm_output  # raw model output; you can parse/structure later if needed
        },
    }


# ---------------- Endpoints -----------------
@router.post("/explain", response_model=ExplainResponse)
async def explain(
    payload: ExplainRequest,
    mock: bool = Query(
        False, description="If true, return a mock response instead of calling LLM"
    ),
):
    # Basic Guard: Empty code is a Client Error
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="Code snippet cannot be empty.")
    if mock:
        return ExplainResponse(
            task="explain",
            result=ExplainResult(
                summary="[mock] This is function adds tow numbers",
                explanation="[mock] The function takes two parameters and returns their sum.",
                issues="[mock] No issues found.",
                suggestions="[mock] The code is safe and efficient.",
                example="[mock] Example usage: add(2, 3) returns 5.",
            ),
        )

    bundle = prompts.bundle("assist.review_diff")
    prompt = (
        f"{bundle.system}\n\n"
        f"{bundle.output_contract}\n\n"
        f"{bundle.safety}\n\n"
        "Here is the diff: \n"
        "dif:\n"
        f"{payload.diff}\n"
        "```"
    )
    llm_text = generate_code(prompt)

    return ExplainResponse(
        task="explain",
        result=ExplainResult(
            summary="[LLM] This is function adds tow numbers",
            explanation=llm_text,
            issues=llm_text,
            suggestions="[LLM] The code is safe and efficient.",
            example=None,
        ),
    )


@router.post("/review-diff", response_model=ReviewDiffResponse)
async def review_diff(
    payload: ReviewDiffRequest,
    mock: bool = Query(
        False, description="If true, return a mock response instead of calling LLM"
    ),
):
    if not payload.diff.strip():
        raise HTTPException(status_code=400, detail="Field 'diff' cannot be empty.")
    if mock:
        return ReviewDiffResponse(
            task="review-diff",
            result=ReviewDiffResult(
                summary="[mock] This change adds basic input validation.",
                issues="[mock] No tests added.\n[mock] Error message is generic.",
                suggested_diff="```diff\n[mock diff goes here]\n```",  # ✅ same name
                notes="[mock] Consider adding tests for invalid inputs.",
            ),
        )

    bundle = prompts.bundle("assist.review_diff")
    request.app.logger.info(f"assist.review_diff prompt_version={bundle.version}")
    prompt = (
        f"{bundle.system}\n\n"
        f"{bundle.output_contract}\n\n"
        f"{bundle.safety}\n\n"
        "Here is the diff: \n"
        "dif:\n"
        f"{payload.diff}\n"
        "```"
    )

    llm_text = generate_code(prompt)
    return ReviewDiffResponse(
        task="review-diff",
        result=ReviewDiffResult(
            summary="Model-generated review of this diff.",
            issues=llm_text,
            suggested_diff="```diff\n# (Structured suggested diff TODO)\n```",
            notes=None,
        ),
    )


@router.post("/docstrings")
async def docstrings(
    payload: DocstringsRequest,
    mock: bool = Query(
        False, description="If true, return a mock response instead of calling the LLM"
    ),
):
    if not payload.snippets:
        raise HTTPException(
            status_code=400, detail="Field 'snippets' must contain at least one item."
        )
    if mock:
        return DocstringsResponse(
            task="docstrings",
            result=DocstringsResult(
                summary="[mock] Added Google-style docstrings to provided snippets.",
                annotated_code="```python\n# (mock annotated code with docstrings)\n```",
            ),
        )

    joined_snippets = "\n\n".join(
        f"# snippet {i + 1}\n```python\n{snippet}\n```"
        for i, snippet in enumerate(payload.snippets)
    )

    prompt = (
        f"{SYSTEM_DOCSTRINGS}\n\n"
        f"Docstring style to use: {payload.style}\n\n"
        f"Here are the snippets:\n\n{joined_snippets}"
    )
    llm_text = generate_code(prompt)
    return DocstringsResponse(
        task="docstrings",
        result=DocstringsResult(
            summary="Model-generated summary of docstring additions.",
            annotated_code=llm_text,
        ),
    )


@router.post("/test")
async def test(
    payload: TestRequest,
    mock: bool = Query(
        False, description="If true, return a mock response instead of calling the LLM"
    ),
):
    """
    Generate runnable test for code + spec using the requested framework.
    """
    if not payload.code.strip():
        raise HTTPException(status_code=400, detail="Field 'code' must not be empty")

    if mock:
        return TestResponse(
            task="tests",
            result=TestResult(
                summary="[mock] Generated basic pytest tests for add().",
                test_code=(
                    "```python\n"
                    "def test_add_basic():\n"
                    "    assert add(1, 2) == 3\n"
                    "```"
                ),
                notes="[mock] Consider adding edge-case tests.",
            ),
        )

    spec_text = (
        payload.spec or "no explicit spec was provided; infer behavior from the code "
    )
    prompt = (
        f"{SYSTEM_TEST}\n\n"
        f"Testing framework: {payload.framework}\n\n"
        "Here is the code under test:\n"
        f"```python\n{payload.code}\n```\n\n"
        f"Spec / requirements:\n{spec_text}\n"
    )

    llm_text = generate_code(prompt)
    return TestResponse(
        task="tests",
        result=TestResult(
            summary="Model-generated test cases.",
            test_code=llm_text,
            notes=None,
        ),
    )
