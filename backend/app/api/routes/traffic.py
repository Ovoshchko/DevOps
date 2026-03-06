from __future__ import annotations

from fastapi import APIRouter, HTTPException
from ..schemas.traffic import TrafficIngestRequest
from ...services.traffic_service import TrafficService

router = APIRouter()
service = TrafficService()


@router.post("/traffic/ingest", status_code=202)
def ingest_traffic(payload: TrafficIngestRequest):
    try:
        count = service.ingest(payload)
        return {"accepted": count}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
