from __future__ import annotations

from fastapi import APIRouter
from ..schemas.traffic import TrafficIngestRequest
from ...services.traffic_service import TrafficService

router = APIRouter()
service = TrafficService()


@router.post("/traffic/ingest", status_code=202)
def ingest_traffic(payload: TrafficIngestRequest):
    count = service.ingest(payload)
    return {"accepted": count}
