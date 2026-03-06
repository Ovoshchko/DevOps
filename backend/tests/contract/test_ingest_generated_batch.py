import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import traffic as traffic_route


client = TestClient(app)


def test_ingest_generated_batch_compatibility_with_mock_service(monkeypatch):
    class MockTrafficService:
        def ingest(self, payload):
            return len(payload.points)

    monkeypatch.setattr(traffic_route, "service", MockTrafficService())

    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "traffic_points.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))

    response = client.post("/traffic/ingest", json=payload)
    assert response.status_code == 202
    assert response.json()["accepted"] == len(payload["points"])
