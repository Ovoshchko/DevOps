from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DetectorConfigCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    description: Optional[str] = None
    sensitivity: float = Field(ge=0.0, le=1.0)
    window_size_seconds: int = Field(gt=0)
    window_step_seconds: int = Field(gt=0)
    features: list[str] = Field(min_length=1)


class DetectorConfigUpdate(DetectorConfigCreate):
    status: str = "active"


class DetectorConfigOut(DetectorConfigUpdate):
    id: str
    created_at: datetime
    updated_at: datetime
