from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_generator_job_lifecycle_contract():
    created = client.post(
        '/generator/jobs',
        json={
            'profile_name': 'demo',
            'batch_size': 10,
            'interval_ms': 1000,
            'duration_seconds': 5,
        },
    )
    assert created.status_code == 201, created.text
    job_id = created.json()['id']

    fetched = client.get(f'/generator/jobs/{job_id}')
    assert fetched.status_code == 200

    stopped = client.post(f'/generator/jobs/{job_id}/stop')
    assert stopped.status_code == 200
    assert stopped.json()['status'] == 'stopped'
