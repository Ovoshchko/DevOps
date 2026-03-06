from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.errors import register_error_handlers
from .api.middleware.logging import logging_middleware
from .api.router import router
from .core.postgres import is_postgres_configured

app = FastAPI(title='Traffic Anomaly Backend')
register_error_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.middleware('http')(logging_middleware)
app.include_router(router)


@app.get('/health')
def health():
    return {'status': 'ok', 'postgres_configured': is_postgres_configured()}
