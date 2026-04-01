from __future__ import annotations

from ..core.settings import settings


class MLClient:
    async def score(self, metrics: list[dict[str, float]]) -> dict:
        try:
            import httpx

            async with httpx.AsyncClient(timeout=5) as client:
                # The ml-service contract stays `{"samples": [...]}` with
                # `anomaly_score`, `is_anomaly`, and `model_version` in response.
                # DetectionService now prepares full model-compatible samples here
                # instead of shrinking the payload to detector review features.
                resp = await client.post(f"{settings.ml_service_url}/inference", json={"samples": metrics})
                resp.raise_for_status()
                return resp.json()
        except Exception:
            values = [v for sample in metrics for v in sample.values()]
            score = sum(values) / len(values) if values else 0.0
            return {"anomaly_score": min(score, 1.0), "model_version": "fallback-v1"}
