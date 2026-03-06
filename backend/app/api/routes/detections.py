from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ...services.detection_service import DetectionService
from ..schemas.detection import DetectionRunRequest

router = APIRouter()
service = DetectionService()


@router.post('/detections/run', status_code=201)
async def run_detection(payload: DetectionRunRequest):
    return await service.run(payload)


@router.get('/detections')
def list_detections(detector_profile_id: Optional[str] = Query(default=None)):
    return service.list(detector_profile_id=detector_profile_id)


@router.get('/detections/{detection_id}')
def get_detection(detection_id: str):
    result = service.get(detection_id)
    if not result:
        raise HTTPException(status_code=404, detail='Detection not found')
    return result


@router.get('/detections/{detection_id}/results')
def get_detection_results(detection_id: str):
    run = service.get(detection_id)
    if not run:
        raise HTTPException(status_code=404, detail='Detection not found')
    return {'results': service.get_results(detection_id)}
