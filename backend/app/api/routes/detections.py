from __future__ import annotations

from fastapi import APIRouter, HTTPException
from ..schemas.detection import DetectionRunRequest
from ...services.detection_service import DetectionService

router = APIRouter()
service = DetectionService()


@router.post("/detections/run", status_code=201)
async def run_detection(payload: DetectionRunRequest):
    return await service.run(payload)


@router.get("/detections")
def list_detections():
    return service.list()


@router.get("/detections/{detection_id}")
def get_detection(detection_id: str):
    result = service.get(detection_id)
    if not result:
        raise HTTPException(status_code=404, detail="Detection not found")
    return result
