from fastapi.testclient import TestClient
from backend.app.main import app


client = TestClient(app)


def test_detectors_crud_contract():
    payload = {
        "name": "detector-1",
        "description": "demo",
        "sensitivity": 0.8,
        "window_size_seconds": 60,
        "window_step_seconds": 30,
        "features": ["bytes_per_sec"],
    }
    created = client.post('/detectors', json=payload)
    assert created.status_code == 201
    detector_id = created.json()['id']

    listed = client.get('/detectors')
    assert listed.status_code == 200

    fetched = client.get(f'/detectors/{detector_id}')
    assert fetched.status_code == 200

    updated = client.put(f'/detectors/{detector_id}', json={**payload, "name": "detector-2", "status": "active"})
    assert updated.status_code == 200
    assert updated.json()['name'] == 'detector-2'

    deleted = client.delete(f'/detectors/{detector_id}')
    assert deleted.status_code == 204
