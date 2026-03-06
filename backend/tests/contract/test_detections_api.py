from fastapi.testclient import TestClient
from backend.app.main import app
from datetime import datetime, timezone, timedelta


client = TestClient(app)


def test_detections_run_and_query_contract():
    created = client.post('/detectors', json={
        "name": "det-x",
        "description": "demo",
        "sensitivity": 0.7,
        "window_size_seconds": 60,
        "window_step_seconds": 30,
        "features": ["bytes_per_sec"]
    })
    assert created.status_code == 201, created.text
    detector = created.json()
    assert "id" in detector, created.text

    now = datetime.now(timezone.utc)
    run = client.post('/detections/run', json={
        "detector_config_id": detector['id'],
        "window_start": (now - timedelta(minutes=1)).isoformat(),
        "window_end": now.isoformat(),
        "initiated_by": "tester"
    })
    assert run.status_code == 201
    detection_id = run.json()['id']

    listed = client.get('/detections')
    assert listed.status_code == 200

    one = client.get(f'/detections/{detection_id}')
    assert one.status_code == 200
