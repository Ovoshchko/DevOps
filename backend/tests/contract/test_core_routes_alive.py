from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_core_routes_are_alive():
    assert client.get('/health').status_code == 200
    assert client.get('/detectors').status_code in {200, 503}
    assert client.get('/traffic/latest').status_code in {200, 503}
    assert client.get('/anomalies/latest').status_code in {200, 503}
    assert client.get('/detections').status_code in {200, 503}
