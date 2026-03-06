from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from ..api.schemas.detection import DetectionResult, DetectionRunOut, DetectionRunRequest
from ..repositories.detection_repository import DetectionRepository
from ..repositories.detector_repository import DetectorRepository
from ..repositories.traffic_repository import TrafficRepository
from ..services.ml_client import MLClient


class DetectionService:
    def __init__(
        self,
        detection_repo: DetectionRepository | None = None,
        detector_repo: DetectorRepository | None = None,
        traffic_repo: TrafficRepository | None = None,
        ml_client: MLClient | None = None,
    ) -> None:
        self.detection_repo = detection_repo or DetectionRepository()
        self.detector_repo = detector_repo or DetectorRepository()
        self.traffic_repo = traffic_repo or TrafficRepository()
        self.ml_client = ml_client or MLClient()

    async def run(self, req: DetectionRunRequest) -> DetectionRunOut:
        detector = self.detector_repo.get(req.detector_config_id)
        if detector is None:
            raise LookupError(f'Detector {req.detector_config_id} not found')
        detector_status = getattr(detector.status, 'value', detector.status)
        if detector_status == 'archived':
            raise ValueError(f'Detector {req.detector_config_id} is archived and cannot be used')

        effective_window_end = req.window_end
        effective_window_start = effective_window_end - timedelta(seconds=detector.window_size_seconds)

        now = datetime.now(timezone.utc)
        run = DetectionRunOut(
            id=str(uuid4()),
            detector_config_id=req.detector_config_id,
            window_start=effective_window_start,
            window_end=effective_window_end,
            initiated_by=req.initiated_by,
            status='running',
            summary=None,
            created_at=now,
            completed_at=None,
        )
        self.detection_repo.save_run(run)

        points = self.traffic_repo.latest(limit=max(20, detector.window_size_seconds))
        metrics = []
        for point in points:
            filtered = {key: value for key, value in point.metrics.items() if key in detector.features}
            metrics.append(filtered if filtered else point.metrics)

        ml = await self.ml_client.score(metrics)
        score = float(ml.get('anomaly_score', 0.0))
        threshold = float(detector.sensitivity)
        is_anomaly = score >= threshold

        result = DetectionResult(
            id=str(uuid4()),
            detection_run_id=run.id,
            timestamp=now,
            anomaly_score=score,
            is_anomaly=is_anomaly,
            metrics_snapshot=(metrics[-1] if metrics else {}),
            explanation=f"detector={detector.name}; threshold={threshold}; features={','.join(detector.features)}",
        )
        self.detection_repo.save_result(result)

        completed = self.detection_repo.update_run(
            run.id,
            {
                'status': 'completed',
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'summary': {
                    'anomaly_score': score,
                    'is_anomaly': is_anomaly,
                    'threshold': threshold,
                    'window_size_seconds': detector.window_size_seconds,
                    'window_step_seconds': detector.window_step_seconds,
                    'features': detector.features,
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
