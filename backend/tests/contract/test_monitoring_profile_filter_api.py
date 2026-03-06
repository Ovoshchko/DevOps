from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_anomalies_latest_accepts_detector_filter():
    detector = client.post(
        '/detectors',
        json={
            'name': 'monitor-filter-profile',
            'description': 'profile',
            'sensitivity': 0.5,
            'window_size_seconds': 60,
            'window_step_seconds': 30,
            'features': ['bytes_per_sec'],
            'status': 'active',
        },
    ).json()

    now = datetime.now(timezone.utc)
    run = client.post(
        '/detections/run',
        json={
            'detector_config_id': detector['id'],
            'window_start': (now - timedelta(minutes=1)).isoformat(),
            'window_end': now.isoformat(),
        },
    )
    assert run.status_code == 201

    filtered = client.get(f"/anomalies/latest?detector_profile_id={detector['id']}")
    assert filtered.status_code == 200
    assert 'results' in filtered.json()
