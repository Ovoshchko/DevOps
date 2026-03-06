from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import monitoring as monitoring_route
from backend.app.api.routes import traffic as traffic_route


client = TestClient(app)


def test_ingest_and_monitoring_contract_with_mock_services(monkeypatch):
    points = [
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_id": "sensor-1",
            "metrics": {"bytes_per_sec": 0.6},
            "tags": {"zone": "lab"},
        }
    ]
    anomalies = [{"id": "r1", "is_anomaly": True}]

    class MockTrafficService:
        def ingest(self, payload):
            return len(payload.points)

    class MockMonitoringService:
        def latest_traffic(self):
            return points

        def latest_anomalies(self, detector_profile_id=None):
            return anomalies

    monkeypatch.setattr(traffic_route, "service", MockTrafficService())
    monkeypatch.setattr(monitoring_route, "service", MockMonitoringService())

    ingest = client.post("/traffic/ingest", json={"points": points})
    assert ingest.status_code == 202
    assert ingest.json()["accepted"] == 1

    latest = client.get("/traffic/latest")
    assert latest.status_code == 200
    assert "points" in latest.json()
    assert len(latest.json()["points"]) == 1

    latest_anomalies = client.get("/anomalies/latest")
    assert latest_anomalies.status_code == 200
    assert "results" in latest_anomalies.json()
    assert len(latest_anomalies.json()["results"]) == 1
