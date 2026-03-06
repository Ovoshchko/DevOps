from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_detector_profile_lifecycle_contract():
    payload = {
        'name': 'profile-a',
        'description': 'test profile',
        'sensitivity': 0.5,
        'window_size_seconds': 60,
        'window_step_seconds': 30,
        'features': ['bytes_per_sec'],
        'status': 'active',
    }

    created = client.post('/detectors', json=payload)
    assert created.status_code == 201, created.text
    detector_id = created.json()['id']

    updated = client.put(f'/detectors/{detector_id}', json={'status': 'draft'})
    assert updated.status_code == 200
    assert updated.json()['status'] == 'draft'

    archived = client.delete(f'/detectors/{detector_id}')
    assert archived.status_code == 204

    fetched = client.get(f'/detectors/{detector_id}')
    assert fetched.status_code == 200
    assert fetched.json()['status'] == 'archived'
