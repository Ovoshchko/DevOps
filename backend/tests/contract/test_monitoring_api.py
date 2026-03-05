from fastapi.testclient import TestClient
from backend.app.main import app
from datetime import datetime, timezone


client = TestClient(app)


def test_ingest_and_monitoring_contract():
    ingest = client.post('/traffic/ingest', json={
        "points": [{
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_id": "sensor-1",
            "metrics": {"bytes_per_sec": 0.6},
            "tags": {"zone": "lab"}
        }]
    })
    assert ingest.status_code == 202

    latest = client.get('/traffic/latest')
    assert latest.status_code == 200
    assert 'points' in latest.json()

    anomalies = client.get('/anomalies/latest')
    assert anomalies.status_code == 200
    assert 'results' in anomalies.json()
