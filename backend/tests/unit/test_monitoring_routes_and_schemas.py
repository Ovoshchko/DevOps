from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api.routes import monitoring
from backend.app.api.schemas.common import ErrorResponse, HealthResponse
from backend.app.domain.detector import DetectorConfig


def test_monitoring_routes_return_service_data_and_translate_failures(monkeypatch):
    class HappyService:
        def latest_traffic(self):
            return [{'source_id': 'sensor-1'}]

        def latest_anomalies(self, detector_profile_id: str | None = None):
            return [{'id': 'res-1', 'detector_profile_id': detector_profile_id}]

    monkeypatch.setattr(monitoring, 'service', HappyService())
    app = FastAPI()
    app.include_router(monitoring.router)
    client = TestClient(app)

    assert client.get('/traffic/latest').json() == {'points': [{'source_id': 'sensor-1'}]}
    assert client.get('/anomalies/latest?detector_profile_id=det-1').json() == {
        'results': [{'id': 'res-1', 'detector_profile_id': 'det-1'}]
    }

    class BrokenTrafficService:
        def latest_traffic(self):
            raise RuntimeError('traffic unavailable')

        def latest_anomalies(self, detector_profile_id: str | None = None):
            raise RuntimeError('anomalies unavailable')

    monkeypatch.setattr(monitoring, 'service', BrokenTrafficService())

    traffic_response = client.get('/traffic/latest')
    anomalies_response = client.get('/anomalies/latest')

    assert traffic_response.status_code == 503
    assert traffic_response.json() == {'detail': 'traffic unavailable'}
    assert anomalies_response.status_code == 503
    assert anomalies_response.json() == {'detail': 'anomalies unavailable'}


def test_common_schemas_and_detector_domain_model_validate_data():
    assert ErrorResponse(error='boom').model_dump() == {'error': 'boom'}
    assert HealthResponse().status == 'ok'

    now = datetime.now(timezone.utc)
    detector = DetectorConfig(
        id='det-1',
        name='detector-name',
        description='desc',
        sensitivity=0.5,
        window_size_seconds=60,
        window_step_seconds=30,
        features=['bytes_per_sec'],
        status='active',
        created_at=now,
        updated_at=now,
    )

    assert detector.name == 'detector-name'
    assert detector.features == ['bytes_per_sec']
