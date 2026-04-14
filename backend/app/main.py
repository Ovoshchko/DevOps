from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.errors import register_error_handlers
from .api.middleware.logging import logging_middleware
from .api.router import router
from .core.influx import is_influx_available
from .core.postgres import is_postgres_available, is_postgres_configured
from .observability import metrics_response

app = FastAPI(title='Traffic Anomaly Backend')
register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://127.0.0.1:3000'
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.middleware('http')(logging_middleware)
app.include_router(router)


@app.get('/health')
def health():
    postgres_ok = is_postgres_available()
    influx_ok = is_influx_available()
    return {
        'status': 'ok' if postgres_ok and influx_ok else 'degraded',
        'postgres_configured': is_postgres_configured(),
        'postgres_available': postgres_ok,
        'influx_available': influx_ok,
    }


@app.get('/metrics')
def metrics():
    return metrics_response()
