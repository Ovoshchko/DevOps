from __future__ import annotations

from pydantic import BaseModel
import os


class Settings(BaseModel):
    service_name: str = "ml-service"
    threshold: float = float(os.getenv("ML_THRESHOLD", "0.7"))


settings = Settings()
