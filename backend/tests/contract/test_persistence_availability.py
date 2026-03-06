from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_exposes_postgres_configuration_flag():
    response = client.get('/health')
    assert response.status_code == 200
    body = response.json()
    assert 'postgres_configured' in body
