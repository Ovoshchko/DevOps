from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DetectionRunRequest(BaseModel):
    detector_config_id: str
    window_start: datetime
    window_end: datetime
    initiated_by: Optional[str] = None


class DetectionRunOut(BaseModel):
    id: str
    detector_config_id: str
    window_start: datetime
    window_end: datetime
    initiated_by: Optional[str] = None
    status: str
    summary: Optional[dict] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class DetectionResult(BaseModel):
    id: str
    detection_run_id: str
    timestamp: datetime
    anomaly_score: float
    is_anomaly: bool
    metrics_snapshot: dict[str, float] = Field(default_factory=dict)
    explanation: Optional[str] = None


class DetectionLatestResponse(BaseModel):
    results: list[DetectionResult]
