from __future__ import annotations

from time import time
from fastapi import Request


async def logging_middleware(request: Request, call_next):
    start = time()
    response = await call_next(request)
    _ = time() - start
    return response
