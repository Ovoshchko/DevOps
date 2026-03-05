from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field
from ...inference.service import run_inference

router = APIRouter()


class InferenceRequest(BaseModel):
    samples: list[dict[str, float]] = Field(min_length=1)


@router.post('/inference')
def inference(req: InferenceRequest):
    return run_inference(req.samples)
