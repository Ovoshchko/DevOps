from __future__ import annotations

from fastapi import APIRouter

from .routes import detections, detectors, generator, monitoring, traffic

router = APIRouter()
router.include_router(detectors.router, tags=['detectors'])
router.include_router(traffic.router, tags=['traffic'])
router.include_router(monitoring.router, tags=['monitoring'])
router.include_router(detections.router, tags=['detections'])
router.include_router(generator.router, tags=['generator'])
