from __future__ import annotations

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.api import errors
from backend.app.api.errors import APIError, register_error_handlers
from backend.app.api.routes import detections, detectors, generator, traffic
from backend.app.api.schemas.detection import DetectionRunOut
from backend.app.api.schemas.detector import DetectorConfigOut, DetectorStatus
from backend.app.core.postgres import PostgresUnavailableError


class FakeInfluxResponse:
    def __init__(self) -> None:
        self.data = 'influx unavailable'
        self.status = 503
        self.reason = 'service unavailable'

    def getheaders(self):
        return {}

    def getheader(self, name: str):
        return None


def _detector() -> DetectorConfigOut:
    now = datetime.now(timezone.utc)
    return DetectorConfigOut(
        id='det-1',
        name='detector',
        description='desc',
        sensitivity=0.5,
        window_size_seconds=60,
        window_step_seconds=30,
        features=['bytes_per_sec'],
        status=DetectorStatus.active,
        created_at=now,
        updated_at=now,
    )


def _run() -> DetectionRunOut:
    now = datetime.now(timezone.utc)
    return DetectionRunOut(
        id='run-1',
        detector_config_id='det-1',
        window_start=now,
        window_end=now,
        initiated_by='tester',
        status='completed',
        summary={},
        created_at=now,
        completed_at=now,
    )


def test_register_error_handlers_maps_known_exceptions_to_json_responses():
    app = FastAPI()
    register_error_handlers(app)

    @app.get('/api-error')
    def raise_api_error():
        raise APIError(status_code=418, message='short and stout')

    @app.get('/postgres-unavailable')
    def raise_postgres_unavailable():
        raise PostgresUnavailableError('postgres offline')

    @app.get('/postgres-operational')
    def raise_postgres_operational():
        raise errors.PsycopgOperationalError('db connection failed')

    @app.get('/influx-error')
    def raise_influx_error():
        raise errors.InfluxDBError(FakeInfluxResponse())

    client = TestClient(app)

    assert client.get('/api-error').json() == {'error': 'short and stout'}
    assert client.get('/api-error').status_code == 418
    assert client.get('/postgres-unavailable').json() == {'error': 'postgres offline'}
    assert client.get('/postgres-unavailable').status_code == 503
    assert client.get('/postgres-operational').json() == {'error': 'db connection failed'}
    assert client.get('/postgres-operational').status_code == 503
    assert client.get('/influx-error').json() == {'error': 'influx unavailable'}
    assert client.get('/influx-error').status_code == 503


def test_detector_routes_return_not_found_for_missing_resources(monkeypatch):
    class StubService:
        def get(self, detector_id: str):
            return None

        def update(self, detector_id: str, payload):
            return None

        def delete(self, detector_id: str):
            return False

    monkeypatch.setattr(detectors, 'service', StubService())

    app = FastAPI()
    app.include_router(detectors.router)
    client = TestClient(app)

    assert client.get('/detectors/missing').status_code == 404
    assert client.put('/detectors/missing', json={'name': 'abc'}).status_code == 404
    assert client.delete('/detectors/missing').status_code == 404


def test_detection_routes_translate_lookup_and_validation_errors(monkeypatch):
    class StubService:
        async def run(self, payload):
            raise LookupError('detector missing')

        def get(self, detection_id: str):
            return None

    monkeypatch.setattr(detections, 'service', StubService())

    app = FastAPI()
    app.include_router(detections.router)
    client = TestClient(app)

    payload = {
        'detector_config_id': 'det-1',
        'window_start': '2026-04-02T10:00:00Z',
        'window_end': '2026-04-02T10:01:00Z',
    }
    response = client.post('/detections/run', json=payload)
    assert response.status_code == 404
    assert response.json() == {'detail': 'detector missing'}

    assert client.get('/detections/missing').status_code == 404
    assert client.get('/detections/missing/results').status_code == 404

    class StubValueErrorService:
        async def run(self, payload):
            raise ValueError('bad window')

    monkeypatch.setattr(detections, 'service', StubValueErrorService())
    response = client.post('/detections/run', json=payload)
    assert response.status_code == 400
    assert response.json() == {'detail': 'bad window'}


def test_detection_results_route_returns_repository_results(monkeypatch):
    class StubService:
        def get(self, detection_id: str):
            return _run()

        def get_results(self, detection_id: str):
            return [{'id': 'res-1'}]

    monkeypatch.setattr(detections, 'service', StubService())

    app = FastAPI()
    app.include_router(detections.router)
    client = TestClient(app)

    assert client.get('/detections/run-1/results').json() == {'results': [{'id': 'res-1'}]}


def test_generator_and_traffic_routes_cover_error_and_not_found_paths(monkeypatch):
    class GeneratorStub:
        def get(self, job_id: str):
            return None

        def stop(self, job_id: str):
            return None

    class TrafficStub:
        def ingest(self, payload):
            raise RuntimeError('influx write failed')

    monkeypatch.setattr(generator, 'service', GeneratorStub())
    monkeypatch.setattr(traffic, 'service', TrafficStub())

    app = FastAPI()
    app.include_router(generator.router)
    app.include_router(traffic.router)
    client = TestClient(app)

    assert client.get('/generator/jobs/missing').status_code == 404
    assert client.post('/generator/jobs/missing/stop').status_code == 404

    response = client.post(
        '/traffic/ingest',
        json={
            'points': [
                {
                    'timestamp': '2026-04-02T10:00:00Z',
                    'source_id': 'sensor-1',
                    'metrics': {'bytes_per_sec': 10},
                }
            ]
        },
    )
    assert response.status_code == 503
    assert response.json() == {'detail': 'influx write failed'}
