from __future__ import annotations

import logging
from time import time

from fastapi import Request

logger = logging.getLogger("ml-service.request")


async def logging_middleware(request: Request, call_next):
    start = time()
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time() - start) * 1000, 2)
        logger.exception(
            "request_failed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "duration_ms": duration_ms,
            },
        )
        raise

    duration_ms = round((time() - start) * 1000, 2)
    logger.info(
        "request_completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )
    return response
