from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import detections as detections_route
from backend.app.api.routes import monitoring as monitoring_route


client = TestClient(app)


def test_anomalies_latest_accepts_detector_filter_with_mock_service(monkeypatch):
    now = datetime.now(timezone.utc)

    class MockDetectionService:
        async def run(self, payload):
            return {
                "id": "run-1",
                "detector_config_id": payload.detector_config_id,
                "window_start": payload.window_start.isoformat(),
                "window_end": payload.window_end.isoformat(),
                "status": "completed",
                "created_at": now.isoformat(),
                "completed_at": now.isoformat(),
                "summary": {"is_anomaly": True},
            }

        def list(self, detector_profile_id=None):
            return []

        def get(self, detection_id):
            return None

        def get_results(self, detection_id):
            return []

    class MockMonitoringService:
        def latest_traffic(self):
            return []

        def latest_anomalies(self, detector_profile_id=None):
            return [{"id": "r1", "detector_profile_id": detector_profile_id, "is_anomaly": True}]

    monkeypatch.setattr(detections_route, "service", MockDetectionService())
    monkeypatch.setattr(monitoring_route, "service", MockMonitoringService())

    run = client.post(
        "/detections/run",
        json={
            "detector_config_id": "det-filter-1",
            "window_start": (now - timedelta(minutes=1)).isoformat(),
            "window_end": now.isoformat(),
        },
    )
    assert run.status_code == 201

    filtered = client.get("/anomalies/latest?detector_profile_id=det-filter-1")
    assert filtered.status_code == 200
    body = filtered.json()
    assert "results" in body
    assert body["results"][0]["detector_profile_id"] == "det-filter-1"
