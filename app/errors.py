from fastapi import Request
from fastapi.responses import JSONResponse


class ErrorResponse(JSONResponse):
    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(
            status_code=status_code,
            content={"ok": False, "error": {"code": code, "message": message}},
        )


async def http_error_handler(request: Request, exc: Exception):
    return ErrorResponse(500, "internal_error", "Unexpected server error")
