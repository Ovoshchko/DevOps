from __future__ import annotations

from fastapi import APIRouter, HTTPException
from ..schemas.detector import DetectorConfigCreate, DetectorConfigUpdate
from ...services.detector_service import DetectorService

router = APIRouter()
service = DetectorService()


@router.post("/detectors", status_code=201)
def create_detector(payload: DetectorConfigCreate):
    return service.create(payload)


@router.get("/detectors")
def list_detectors():
    return service.list()


@router.get("/detectors/{detector_id}")
def get_detector(detector_id: str):
    detector = service.get(detector_id)
    if not detector:
        raise HTTPException(status_code=404, detail="Detector not found")
    return detector


@router.put("/detectors/{detector_id}")
def update_detector(detector_id: str, payload: DetectorConfigUpdate):
    detector = service.update(detector_id, payload)
    if not detector:
        raise HTTPException(status_code=404, detail="Detector not found")
    return detector


@router.delete("/detectors/{detector_id}", status_code=204)
def delete_detector(detector_id: str):
    ok = service.delete(detector_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Detector not found")
