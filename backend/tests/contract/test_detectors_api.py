from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import detectors as detectors_route


client = TestClient(app)


def test_detectors_crud_contract_with_mock_service(monkeypatch):
    storage = {}

    class MockService:
        def create(self, payload):
            item = {
                "id": "det-1",
                "name": payload.name,
                "description": payload.description,
                "sensitivity": payload.sensitivity,
                "window_size_seconds": payload.window_size_seconds,
                "window_step_seconds": payload.window_step_seconds,
                "features": payload.features,
                "status": getattr(payload.status, "value", payload.status),
            }
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
            patch = payload.model_dump(exclude_none=True)
            for key, value in patch.items():
                item[key] = getattr(value, "value", value)
            return item

        def delete(self, detector_id):
            return storage.pop(detector_id, None) is not None

    monkeypatch.setattr(detectors_route, "service", MockService())

    payload = {
        "name": "detector-1",
        "description": "demo",
        "sensitivity": 0.8,
        "window_size_seconds": 60,
        "window_step_seconds": 30,
        "features": ["bytes_per_sec"],
    }

    created = client.post("/detectors", json=payload)
    assert created.status_code == 201, created.text
    detector_id = created.json()["id"]

    listed = client.get("/detectors")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    fetched = client.get(f"/detectors/{detector_id}")
    assert fetched.status_code == 200

    updated = client.put(f"/detectors/{detector_id}", json={"name": "detector-2", "status": "active"})
    assert updated.status_code == 200
    assert updated.json()["name"] == "detector-2"

    deleted = client.delete(f"/detectors/{detector_id}")
    assert deleted.status_code == 204
