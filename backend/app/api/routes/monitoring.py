from __future__ import annotations

from fastapi import APIRouter
from ...services.monitoring_service import MonitoringService

router = APIRouter()
service = MonitoringService()


@router.get("/traffic/latest")
def traffic_latest():
    return {"points": service.latest_traffic()}


@router.get("/anomalies/latest")
def anomalies_latest():
    return {"results": service.latest_anomalies()}
