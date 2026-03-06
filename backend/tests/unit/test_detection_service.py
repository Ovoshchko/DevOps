from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from backend.app.api.schemas.detection import DetectionRunRequest
from backend.app.api.schemas.detection import DetectionResult, DetectionRunOut
from backend.app.api.schemas.traffic import TrafficPoint
from backend.app.api.schemas.detector import DetectorStatus
from backend.app.services.detection_service import DetectionService


class FakeDetectionRepo:
    def __init__(self) -> None:
        self.runs: dict[str, DetectionRunOut] = {}
        self.results: dict[str, list[DetectionResult]] = {}

    def save_run(self, run: DetectionRunOut) -> DetectionRunOut:
        self.runs[run.id] = run
        self.results.setdefault(run.id, [])
        return run

    def update_run(self, run_id: str, patch: dict) -> DetectionRunOut | None:
        run = self.runs.get(run_id)
        if not run:
            return None
        merged = {**run.model_dump(), **patch}
        updated = DetectionRunOut.model_validate(merged)
        self.runs[run_id] = updated
        return updated

    def save_result(self, result: DetectionResult) -> DetectionResult:
        self.results.setdefault(result.detection_run_id, []).append(result)
        return result

    def get_results(self, detection_id: str) -> list[DetectionResult]:
        return self.results.get(detection_id, [])

    def list_runs(self, detector_profile_id: str | None = None) -> list[DetectionRunOut]:
        runs = list(self.runs.values())
        if detector_profile_id:
            runs = [item for item in runs if item.detector_config_id == detector_profile_id]
        return runs

    def get_run(self, detection_id: str) -> DetectionRunOut | None:
        return self.runs.get(detection_id)

    def latest_results(self, detector_profile_id: str | None = None, limit: int = 20) -> list[DetectionResult]:
        runs = self.list_runs(detector_profile_id=detector_profile_id)
        run_ids = {item.id for item in runs}
        all_results = [res for run_id in run_ids for res in self.results.get(run_id, [])]
        return all_results[-limit:]


class FakeDetectorRepo:
    def __init__(self, detector: object | None = None) -> None:
        self.detector = detector

    def get(self, detector_id: str):
        if self.detector and getattr(self.detector, "id", None) == detector_id:
            return self.detector
        return None


class FakeTrafficRepo:
    def __init__(self, points: list[TrafficPoint]) -> None:
        self.points = points
        self.last_limit: int | None = None

    def latest(self, limit: int = 20) -> list[TrafficPoint]:
        self.last_limit = limit
        return self.points


class FakeMLClient:
    def __init__(self, score: float) -> None:
        self.score_value = score
        self.received_metrics: list[dict[str, float]] | None = None

    async def score(self, metrics: list[dict[str, float]]) -> dict:
        self.received_metrics = metrics
        return {"anomaly_score": self.score_value}


def _build_detector(status: DetectorStatus = DetectorStatus.active):
    return SimpleNamespace(
        id='det-1',
        name='unit-detector',
        sensitivity=0.5,
        window_size_seconds=60,
        window_step_seconds=30,
        features=['bytes_per_sec'],
        status=status,
    )


def _build_points() -> list[TrafficPoint]:
    now = datetime.now(timezone.utc)
    return [
        TrafficPoint(
            timestamp=now - timedelta(seconds=15),
            source_id='sensor-a',
            metrics={'bytes_per_sec': 0.4, 'packets_per_sec': 10.0},
        ),
        TrafficPoint(
            timestamp=now,
            source_id='sensor-a',
            metrics={'bytes_per_sec': 0.8, 'packets_per_sec': 20.0},
        ),
    ]


def test_detection_service_run_applies_detector_configuration():
    detector = _build_detector()
    detection_repo = FakeDetectionRepo()
    traffic_repo = FakeTrafficRepo(_build_points())
    ml_client = FakeMLClient(score=0.75)
    service = DetectionService(
        detection_repo=detection_repo,
        detector_repo=FakeDetectorRepo(detector),
        traffic_repo=traffic_repo,
        ml_client=ml_client,
    )

    now = datetime.now(timezone.utc)
    result = asyncio.run(
        service.run(
            DetectionRunRequest(
                detector_config_id='det-1',
                window_start=now - timedelta(minutes=1),
                window_end=now,
                initiated_by='tester',
            )
        )
    )

    assert result.id
    assert result.status == 'completed'
    assert result.summary is not None
    assert result.summary.get('threshold') == 0.5
    assert result.summary.get('is_anomaly') is True
    assert result.summary.get('features') == ['bytes_per_sec']
    assert traffic_repo.last_limit == 60
    assert ml_client.received_metrics is not None
    assert all('bytes_per_sec' in item for item in ml_client.received_metrics)
    assert all('packets_per_sec' not in item for item in ml_client.received_metrics)


def test_detection_service_raises_if_detector_not_found():
    service = DetectionService(
        detection_repo=FakeDetectionRepo(),
        detector_repo=FakeDetectorRepo(None),
        traffic_repo=FakeTrafficRepo(_build_points()),
        ml_client=FakeMLClient(score=0.3),
    )
    now = datetime.now(timezone.utc)

    try:
        asyncio.run(
            service.run(
                DetectionRunRequest(
                    detector_config_id='missing',
                    window_start=now - timedelta(minutes=1),
                    window_end=now,
                )
            )
        )
        assert False, "LookupError was expected"
    except LookupError as exc:
        assert "missing" in str(exc)


def test_detection_service_raises_if_detector_archived():
    service = DetectionService(
        detection_repo=FakeDetectionRepo(),
        detector_repo=FakeDetectorRepo(_build_detector(status=DetectorStatus.archived)),
        traffic_repo=FakeTrafficRepo(_build_points()),
        ml_client=FakeMLClient(score=0.3),
    )
    now = datetime.now(timezone.utc)

    try:
        asyncio.run(
            service.run(
                DetectionRunRequest(
                    detector_config_id='det-1',
                    window_start=now - timedelta(minutes=1),
                    window_end=now,
                )
            )
        )
        assert False, "ValueError was expected"
    except ValueError as exc:
        assert "archived" in str(exc)
