from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class DetectorConfig(BaseModel):
    id: str
    name: str = Field(min_length=3, max_length=120)
    description: Optional[str] = None
    sensitivity: float = Field(ge=0.0, le=1.0)
    window_size_seconds: int = Field(gt=0)
    window_step_seconds: int = Field(gt=0)
    features: List[str] = Field(min_length=1)
    status: str = "active"
    created_at: datetime
    updated_at: datetime
