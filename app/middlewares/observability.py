import time
import uuid
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HDR = "X-Request-ID"


async def request_id_and_timing_mw(request: Request, call_next):
    rid = request.headers.get(REQUEST_ID_HDR, str(uuid.uuid4()))
    start = time.perf_counter()
    response: Response | None = None

    try:
        # Normal request flow
        response: Response = await call_next(request)
    except Exception:
        # Something in the downstream stack raised
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        request.app.logger.exception(
            f"{request.method} {request.url.path} -> ERROR in {elapsed_ms}ms [rid={rid}]"
        )
        # Re-raise so FastAPI's exception handlers can do their job
        raise
    else:
        # Only runs if no exception
        elapsed_ms = int((time.perf_counter() - start) * 1000)

        # Try to attach observability headers
        try:
            response.headers[REQUEST_ID_HDR] = rid
            response.headers["X-Elapsed-ms"] = str(elapsed_ms)
        except Exception:
            # Don't let header failures kill the request
            pass

        request.app.logger.info(
            f"{request.method} {request.url.path} -> "
            f"{getattr(response, 'status_code', '?')} in {elapsed_ms}ms [rid={rid}]"
        )

        # ✅ IMPORTANT: always return a Response on the happy path
        return response
