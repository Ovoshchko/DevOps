from __future__ import annotations

from fastapi import APIRouter
from .routes import detectors, traffic, monitoring, detections

router = APIRouter()
router.include_router(detectors.router, tags=["detectors"])
router.include_router(traffic.router, tags=["traffic"])
router.include_router(monitoring.router, tags=["monitoring"])
router.include_router(detections.router, tags=["detections"])
