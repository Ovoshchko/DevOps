from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import detectors as detectors_route


client = TestClient(app)


def test_detector_profile_lifecycle_contract_with_mock_service(monkeypatch):
    storage = {}

    class MockService:
        def create(self, payload):
            item = {**payload.model_dump(), "id": "profile-a"}
            storage[item["id"]] = item
            return item

        def list(self):
            return list(storage.values())

        def get(self, detector_id):
            return storage.get(detector_id)

        def update(self, detector_id, payload):
            item = storage.get(detector_id)
            if not item:
                return None
            item.update(payload.model_dump(exclude_none=True))
            return item

        def delete(self, detector_id):
            item = storage.get(detector_id)
            if not item:
                return False
            item["status"] = "archived"
            return True

    monkeypatch.setattr(detectors_route, "service", MockService())

    payload = {
        "name": "profile-a",
        "description": "test profile",
        "sensitivity": 0.5,
        "window_size_seconds": 60,
        "window_step_seconds": 30,
        "features": ["bytes_per_sec"],
        "status": "active",
    }

    created = client.post("/detectors", json=payload)
    assert created.status_code == 201
    detector_id = created.json()["id"]

    updated = client.put(f"/detectors/{detector_id}", json={"status": "draft"})
    assert updated.status_code == 200
    assert updated.json()["status"] == "draft"

    archived = client.delete(f"/detectors/{detector_id}")
    assert archived.status_code == 204

    fetched = client.get(f"/detectors/{detector_id}")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "archived"
