from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from ..core.postgres import PostgresUnavailableError

try:
    from psycopg import OperationalError as PsycopgOperationalError
except Exception:
    PsycopgOperationalError = RuntimeError

try:
    from influxdb_client.client.exceptions import InfluxDBError
except Exception:
    InfluxDBError = RuntimeError


class APIError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(APIError)
    async def handle_api_error(_: Request, exc: APIError):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    @app.exception_handler(PostgresUnavailableError)
    async def handle_postgres_unavailable(_: Request, exc: PostgresUnavailableError):
        return JSONResponse(status_code=503, content={"error": str(exc)})

    @app.exception_handler(PsycopgOperationalError)
    async def handle_postgres_operational_error(_: Request, exc: Exception):
        return JSONResponse(status_code=503, content={"error": str(exc)})

    @app.exception_handler(InfluxDBError)
    async def handle_influx_error(_: Request, exc: Exception):
        return JSONResponse(status_code=503, content={"error": str(exc)})
