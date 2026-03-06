from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from ..api.schemas.detection import DetectionResult, DetectionRunOut, DetectionRunRequest
from ..repositories.detection_repository import DetectionRepository
from ..repositories.traffic_repository import TrafficRepository
from ..services.ml_client import MLClient


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

    async def run(self, req: DetectionRunRequest) -> DetectionRunOut:
        now = datetime.now(timezone.utc)
        run = DetectionRunOut(
            id=str(uuid4()),
            detector_config_id=req.detector_config_id,
            window_start=req.window_start,
            window_end=req.window_end,
            initiated_by=req.initiated_by,
            status='running',
            summary=None,
            created_at=now,
            completed_at=None,
        )
        self.detection_repo.save_run(run)

        points = self.traffic_repo.latest()
        metrics = [p.metrics for p in points]
        ml = await self.ml_client.score(metrics)
        score = float(ml.get('anomaly_score', 0.0))

        result = DetectionResult(
            id=str(uuid4()),
            detection_run_id=run.id,
            timestamp=now,
            anomaly_score=score,
            is_anomaly=score >= 0.7,
            metrics_snapshot=(metrics[-1] if metrics else {}),
            explanation='window detection',
        )
        self.detection_repo.save_result(result)

        completed = self.detection_repo.update_run(
            run.id,
            {
                'status': 'completed',
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'summary': {
                    'anomaly_score': score,
                    'is_anomaly': score >= 0.7,
                    'result_count': len(self.detection_repo.get_results(run.id)),
                },
            },
        )
        return completed or run

    def list(self, detector_profile_id: str | None = None) -> list[DetectionRunOut]:
        return self.detection_repo.list_runs(detector_profile_id=detector_profile_id)

    def get(self, detection_id: str) -> DetectionRunOut | None:
        return self.detection_repo.get_run(detection_id)

    def get_results(self, detection_id: str) -> list[DetectionResult]:
        return self.detection_repo.get_results(detection_id)
