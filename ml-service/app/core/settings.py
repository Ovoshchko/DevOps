from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel


DEFAULT_MODEL_DIR = Path(__file__).resolve().parents[2] / "models" / "v0"


class Settings(BaseModel):
    service_name: str = "ml-service"
    threshold: float = float(os.getenv("ML_THRESHOLD", "0.7"))
    model_dir: str = os.getenv("ML_MODEL_DIR", str(DEFAULT_MODEL_DIR))
    model_version: str = os.getenv("ML_MODEL_VERSION", "v0")


settings = Settings()
