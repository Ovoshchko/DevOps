from __future__ import annotations

from time import time
from fastapi import Request

from ...observability.metrics import EXCEPTION_COUNTER
from ...observability.metrics import IN_PROGRESS
from ...observability.metrics import observe_request


async def logging_middleware(request: Request, call_next):
    start = time()
    method = request.method
    path = request.url.path
    tracker = IN_PROGRESS.labels(method=method, path=path)
    tracker.inc()
    try:
        response = await call_next(request)
    except Exception as exc:
        EXCEPTION_COUNTER.labels(
            method=method,
            path=path,
            exception_type=exc.__class__.__name__,
        ).inc()
        observe_request(method=method, path=path, status_code=500, duration_seconds=time() - start)
        raise
    finally:
        tracker.dec()

    observe_request(
        method=method,
        path=path,
        status_code=response.status_code,
        duration_seconds=time() - start,
    )
    return response
