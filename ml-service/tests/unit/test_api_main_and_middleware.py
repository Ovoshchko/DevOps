from __future__ import annotations

import asyncio
import logging
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.api.middleware.logging import logging_middleware
from app.api.routes import inference as inference_route
from app.main import app
from app.model.anomaly_model import FeaturePreparationError, ModelLoadError


def test_main_health_and_inference_success(monkeypatch):
    monkeypatch.setattr(
        inference_route,
        'run_inference',
        lambda samples: {'anomaly_score': 0.8, 'is_anomaly': True, 'model_version': 'test-v1'},
    )

    client = TestClient(app)

    health = client.get('/health')
    inference = client.post('/inference', json={'samples': [{'packet_size': 1.0}]})

    assert health.status_code == 200
    assert health.json()['status'] == 'ok'
    assert inference.status_code == 200
    assert inference.json()['model_version'] == 'test-v1'


def test_inference_route_translates_model_errors(monkeypatch):
    client = TestClient(app)

    monkeypatch.setattr(
        inference_route,
        'run_inference',
        lambda samples: (_ for _ in ()).throw(FeaturePreparationError('bad feature payload')),
    )
    response = client.post('/inference', json={'samples': [{'packet_size': 1.0}]})
    assert response.status_code == 422
    assert response.json() == {'detail': 'bad feature payload'}

    monkeypatch.setattr(
        inference_route,
        'run_inference',
        lambda samples: (_ for _ in ()).throw(ModelLoadError('missing model bundle')),
    )
    response = client.post('/inference', json={'samples': [{'packet_size': 1.0}]})
    assert response.status_code == 500
    assert response.json() == {'detail': 'missing model bundle'}


def test_logging_middleware_logs_successful_requests(caplog):
    request = SimpleNamespace(method='POST', url=SimpleNamespace(path='/inference'))

    async def call_next(req):
        return SimpleNamespace(status_code=202)

    with caplog.at_level(logging.INFO, logger='ml-service.request'):
        response = asyncio.run(logging_middleware(request, call_next))

    assert response.status_code == 202
    assert 'request_completed' in caplog.text


def test_logging_middleware_logs_failed_requests(caplog):
    request = SimpleNamespace(method='GET', url=SimpleNamespace(path='/broken'))

    async def call_next(req):
        raise RuntimeError('boom')

    with caplog.at_level(logging.ERROR, logger='ml-service.request'):
        with pytest.raises(RuntimeError, match='boom'):
            asyncio.run(logging_middleware(request, call_next))

    assert 'request_failed' in caplog.text
