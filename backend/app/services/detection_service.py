from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from ..api.schemas.detection import DetectionRunRequest, DetectionResult
from ..repositories.detection_repository import DetectionRepository
from ..repositories.traffic_repository import TrafficRepository
from .ml_client import MLClient


class DetectionService:
    def __init__(
        self,
        detection_repo: DetectionRepository | None = None,
        traffic_repo: TrafficRepository | None = None,
        ml_client: MLClient | None = None,
    ) -> None:
        self.detection_repo = detection_repo or DetectionRepository()
        self.traffic_repo = traffic_repo or TrafficRepository()
        self.ml_client = ml_client or MLClient()

    async def run(self, req: DetectionRunRequest) -> DetectionResult:
        points = self.traffic_repo.latest()
        metrics = [p.metrics for p in points]
        ml = await self.ml_client.score(metrics)
        score = float(ml.get("anomaly_score", 0.0))
        result = DetectionResult(
            id=str(uuid4()),
            detector_config_id=req.detector_config_id,
            window_start=req.window_start,
            window_end=req.window_end,
            anomaly_score=score,
            is_anomaly=score >= 0.7,
            model_version=ml.get("model_version", "simple-v1"),
            summary="window detection",
            created_at=datetime.now(timezone.utc),
        )
        return self.detection_repo.save(result)

    def list(self) -> list[DetectionResult]:
        return self.detection_repo.list()

    def get(self, detection_id: str) -> DetectionResult | None:
        return self.detection_repo.get(detection_id)
