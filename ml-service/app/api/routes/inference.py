from __future__ import annotations

from fastapi import APIRouter
from fastapi import HTTPException
from pydantic import BaseModel, Field

from ...inference.service import run_inference
from ...model.anomaly_model import FeaturePreparationError
from ...model.anomaly_model import ModelLoadError

router = APIRouter()


class InferenceRequest(BaseModel):
    samples: list[dict[str, float]] = Field(min_length=1)


@router.post('/inference')
def inference(req: InferenceRequest):
    try:
        return run_inference(req.samples)
    except FeaturePreparationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ModelLoadError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
