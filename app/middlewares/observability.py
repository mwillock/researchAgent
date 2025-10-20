import time
import uuid
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HDR = "X-Request-ID"


async def request_id_and_timing_mw(request: Request, call_next):
    rid = request.headers.get(REQUEST_ID_HDR, str(uuid.uuid4()))
    start = time.perf_counter()
    try:
        response: Response = await call_next(request)
    finally:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        headers = {REQUEST_ID_HDR: rid, "X-Elapsed-ms": str(elapsed_ms)}
        for k, v in headers.items():
            try:
                response.headers[k] = v
            except Exception:
                pass
        request.app.logger.info(
            f"{request.method} {request.url.path} -> {getattr(response,'status_code','?')} in {elapsed_ms}ms [rid={rid}]"
        )
        return response
