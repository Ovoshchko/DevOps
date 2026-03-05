from __future__ import annotations

from fastapi import FastAPI
from .api.routes.inference import router as inference_router
from .api.middleware.logging import logging_middleware

app = FastAPI(title="Traffic Anomaly ML Service")
app.middleware("http")(logging_middleware)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(inference_router)
