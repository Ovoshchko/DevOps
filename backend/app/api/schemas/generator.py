from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GeneratorJobCreate(BaseModel):
    profile_name: str = Field(min_length=1, max_length=120)
    batch_size: int = Field(gt=0)
    interval_ms: int = Field(ge=250)
    duration_seconds: int = Field(gt=0)


class GeneratorJobOut(BaseModel):
    id: str
    profile_name: str
    status: str
    batch_size: int
    interval_ms: int
    duration_seconds: int
    sent_batches: int
    total_batches: int
    last_error: Optional[str] = None
    started_at: datetime
    finished_at: Optional[datetime] = None
