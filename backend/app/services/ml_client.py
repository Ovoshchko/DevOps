from __future__ import annotations

import httpx
from ..core.settings import settings


class MLClient:
    async def score(self, metrics: list[dict[str, float]]) -> dict:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(f"{settings.ml_service_url}/inference", json={"samples": metrics})
                resp.raise_for_status()
                return resp.json()
        except Exception:
            values = [v for sample in metrics for v in sample.values()]
            score = sum(values) / len(values) if values else 0.0
            return {"anomaly_score": min(score, 1.0), "model_version": "fallback-v1"}
