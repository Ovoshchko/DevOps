from datetime import datetime, timezone

from backend.app.api.schemas.detection import DetectionResult
from backend.app.api.schemas.traffic import TrafficPoint
from backend.app.services.monitoring_service import MonitoringService


class TrafficRepoStub:
    def __init__(self, points):
        self.points = points

    def latest(self):
        return self.points


class DetectionRepoStub:
    def __init__(self, results):
        self.results = results
        self.last_filter = None

    def latest_results(self, detector_profile_id=None, limit=20):
        self.last_filter = detector_profile_id
        return self.results[:limit]


def test_monitoring_service_latest_anomalies_filters_non_anomaly_results():
    results = [
        DetectionResult(
            id='r1',
            detection_run_id='d1',
            timestamp=datetime.now(timezone.utc),
            anomaly_score=0.9,
            is_anomaly=True,
            metrics_snapshot={'bytes_per_sec': 0.9},
        ),
        DetectionResult(
            id='r2',
            detection_run_id='d1',
            timestamp=datetime.now(timezone.utc),
            anomaly_score=0.2,
            is_anomaly=False,
            metrics_snapshot={'bytes_per_sec': 0.2},
        ),
    ]
    service = MonitoringService(
        traffic_repo=TrafficRepoStub([]),
        detection_repo=DetectionRepoStub(results),
    )

    anomalies = service.latest_anomalies(detector_profile_id='det-1')
    assert len(anomalies) == 1
    assert anomalies[0].id == 'r1'
    assert service.detection_repo.last_filter == 'det-1'


def test_monitoring_service_latest_traffic_returns_repo_data():
    points = [
        TrafficPoint(
            timestamp=datetime.now(timezone.utc),
            source_id='sensor-1',
            metrics={'bytes_per_sec': 0.5},
        )
    ]
    service = MonitoringService(
        traffic_repo=TrafficRepoStub(points),
        detection_repo=DetectionRepoStub([]),
    )

    latest = service.latest_traffic()
    assert len(latest) == 1
    assert latest[0].source_id == 'sensor-1'
