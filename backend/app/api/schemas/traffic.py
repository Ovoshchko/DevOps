from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TrafficPoint(BaseModel):
    timestamp: datetime
    source_id: str
    metrics: dict[str, float] = Field(min_length=1)
    tags: Optional[dict[str, str]] = None

    @staticmethod
    def coerce_metric_value(value: object) -> float | None:
        if isinstance(value, bool):
            return float(value)
        if isinstance(value, (int, float)):
            return float(value)
        return None

    def numeric_metrics(self) -> dict[str, float]:
        return {
            key: coerced
            for key, value in self.metrics.items()
            if (coerced := self.coerce_metric_value(value)) is not None
        }


class TrafficIngestRequest(BaseModel):
    points: list[TrafficPoint] = Field(min_length=1)


class TrafficLatestResponse(BaseModel):
    points: list[TrafficPoint]
