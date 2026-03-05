from __future__ import annotations

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DetectionRunRequest(BaseModel):
    detector_config_id: str
    window_start: datetime
    window_end: datetime
    initiated_by: Optional[str] = None


class DetectionResult(BaseModel):
    id: str
    detector_config_id: str
    window_start: datetime
    window_end: datetime
    anomaly_score: float
    is_anomaly: bool
    model_version: str
    summary: Optional[str] = None
    created_at: datetime


class DetectionLatestResponse(BaseModel):
    results: list[DetectionResult]
