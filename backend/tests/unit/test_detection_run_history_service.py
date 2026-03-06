from datetime import datetime, timedelta, timezone
import asyncio
from types import SimpleNamespace

from backend.app.api.schemas.detection import DetectionRunRequest
from backend.app.api.schemas.traffic import TrafficPoint
from backend.app.services.detection_service import DetectionService


def test_detection_service_returns_run_history_entries():
    class DetectionRepoStub:
        def __init__(self):
            self.runs = {}
            self.results = {}

        def save_run(self, run):
            self.runs[run.id] = run
            self.results.setdefault(run.id, [])
            return run

        def update_run(self, run_id, patch):
            run = self.runs[run_id]
            merged = {**run.model_dump(), **patch}
            updated = type(run).model_validate(merged)
            self.runs[run_id] = updated
            return updated

        def save_result(self, result):
            self.results.setdefault(result.detection_run_id, []).append(result)
            return result

        def get_results(self, detection_id):
            return self.results.get(detection_id, [])

        def list_runs(self, detector_profile_id=None):
            runs = list(self.runs.values())
            if detector_profile_id:
                runs = [item for item in runs if item.detector_config_id == detector_profile_id]
            return runs

        def get_run(self, detection_id):
            return self.runs.get(detection_id)

    class DetectorRepoStub:
        def get(self, detector_id):
            return SimpleNamespace(
                id=detector_id,
                name='history-detector',
                sensitivity=0.55,
                window_size_seconds=120,
                window_step_seconds=30,
                features=['bytes_per_sec'],
                status='active',
            )

    class TrafficRepoStub:
        def latest(self, limit=20):
            return [
                TrafficPoint(
                    timestamp=datetime.now(timezone.utc),
                    source_id='sensor-h',
                    metrics={'bytes_per_sec': 0.33, 'packets_per_sec': 12.0},
                )
            ]

    class MLStub:
        async def score(self, metrics):
            return {'anomaly_score': 0.9}

    service = DetectionService(
        detection_repo=DetectionRepoStub(),
        detector_repo=DetectorRepoStub(),
        traffic_repo=TrafficRepoStub(),
        ml_client=MLStub(),
    )
    now = datetime.now(timezone.utc)

    run = asyncio.run(
        service.run(
            DetectionRunRequest(
                detector_config_id='demo-detector',
                window_start=now - timedelta(minutes=1),
                window_end=now,
            )
        )
    )

    listed = service.list()
    assert any(item.id == run.id for item in listed)
