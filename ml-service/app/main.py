from __future__ import annotations

from fastapi import FastAPI

from .api.routes.inference import router as inference_router
from .api.middleware.logging import logging_middleware
from .core.settings import settings
from .observability import metrics_response

app = FastAPI(title="Traffic Anomaly ML Service")
app.middleware("http")(logging_middleware)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_version": settings.model_version,
        "model_dir": settings.model_dir,
        "threshold": settings.threshold,
    }


app.include_router(inference_router)


@app.get('/metrics')
def metrics():
    return metrics_response()
