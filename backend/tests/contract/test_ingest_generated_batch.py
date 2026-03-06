import json
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_ingest_generated_batch_compatibility():
    fixture_path = Path(__file__).resolve().parents[1] / 'fixtures' / 'traffic_points.json'
    payload = json.loads(fixture_path.read_text(encoding='utf-8'))

    response = client.post('/traffic/ingest', json=payload)
    assert response.status_code == 202
    assert response.json()['accepted'] == len(payload['points'])
