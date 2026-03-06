from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query

from ...services.monitoring_service import MonitoringService

router = APIRouter()
service = MonitoringService()


@router.get('/traffic/latest')
def traffic_latest():
    return {'points': service.latest_traffic()}


@router.get('/anomalies/latest')
def anomalies_latest(detector_profile_id: Optional[str] = Query(default=None)):
    return {'results': service.latest_anomalies(detector_profile_id=detector_profile_id)}
