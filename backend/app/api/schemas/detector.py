from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DetectorStatus(str, Enum):
    draft = 'draft'
    active = 'active'
    archived = 'archived'


class DetectorConfigCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    description: Optional[str] = None
    sensitivity: float = Field(ge=0.0, le=1.0)
    window_size_seconds: int = Field(gt=0)
    window_step_seconds: int = Field(gt=0)
    features: list[str] = Field(min_length=1)
    status: DetectorStatus = DetectorStatus.active


class DetectorConfigUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=120)
    description: Optional[str] = None
    sensitivity: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    window_size_seconds: Optional[int] = Field(default=None, gt=0)
    window_step_seconds: Optional[int] = Field(default=None, gt=0)
    features: Optional[list[str]] = None
    status: Optional[DetectorStatus] = None


class DetectorConfigOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    sensitivity: float
    window_size_seconds: int
    window_step_seconds: int
    features: list[str]
    status: DetectorStatus
    created_at: datetime
    updated_at: datetime
