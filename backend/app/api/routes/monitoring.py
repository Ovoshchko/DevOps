from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ...services.monitoring_service import MonitoringService

router = APIRouter()
service = MonitoringService()


@router.get('/traffic/latest')
def traffic_latest():
    try:
        return {'points': service.latest_traffic()}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get('/anomalies/latest')
def anomalies_latest(detector_profile_id: Optional[str] = Query(default=None)):
    try:
        return {'results': service.latest_anomalies(detector_profile_id=detector_profile_id)}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
