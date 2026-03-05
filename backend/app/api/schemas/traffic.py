from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TrafficPoint(BaseModel):
    timestamp: datetime
    source_id: str
    metrics: dict[str, float] = Field(min_length=1)
    tags: Optional[dict[str, str]] = None


class TrafficIngestRequest(BaseModel):
    points: list[TrafficPoint] = Field(min_length=1)


class TrafficLatestResponse(BaseModel):
    points: list[TrafficPoint]
