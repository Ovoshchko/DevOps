from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import detections as detections_route


client = TestClient(app)


def test_detections_run_and_query_contract_with_mock_service(monkeypatch):
    now = datetime.now(timezone.utc)
    run_item = {
        "id": "run-1",
        "detector_config_id": "det-1",
        "window_start": (now - timedelta(minutes=1)).isoformat(),
        "window_end": now.isoformat(),
        "initiated_by": "tester",
        "status": "completed",
        "summary": {"anomaly_score": 0.9, "is_anomaly": True},
        "created_at": now.isoformat(),
        "completed_at": now.isoformat(),
    }
    results = [{"id": "res-1", "detection_run_id": "run-1", "is_anomaly": True}]

    class MockService:
        async def run(self, payload):
            return run_item

        def list(self, detector_profile_id=None):
            return [run_item]

        def get(self, detection_id):
            return run_item if detection_id == "run-1" else None

        def get_results(self, detection_id):
            return results if detection_id == "run-1" else []

    monkeypatch.setattr(detections_route, "service", MockService())

    run = client.post(
        "/detections/run",
        json={
            "detector_config_id": "det-1",
            "window_start": (now - timedelta(minutes=1)).isoformat(),
            "window_end": now.isoformat(),
            "initiated_by": "tester",
        },
    )
    assert run.status_code == 201, run.text
    detection_id = run.json()["id"]

    listed = client.get("/detections")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    one = client.get(f"/detections/{detection_id}")
    assert one.status_code == 200

    result_set = client.get(f"/detections/{detection_id}/results")
    assert result_set.status_code == 200
    assert len(result_set.json()["results"]) == 1
