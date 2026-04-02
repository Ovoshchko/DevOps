from __future__ import annotations

import asyncio
import sys
from types import SimpleNamespace

from backend.app.services.ml_client import MLClient


class StubResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self.payload


class StubAsyncClient:
    def __init__(self, response: StubResponse) -> None:
        self.response = response
        self.calls: list[tuple[str, dict]] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url: str, json: dict):
        self.calls.append((url, json))
        return self.response


def test_ml_client_posts_metrics_to_ml_service(monkeypatch):
    client_impl = StubAsyncClient(StubResponse({'anomaly_score': 0.91, 'model_version': 'v1'}))
    httpx_stub = SimpleNamespace(AsyncClient=lambda timeout: client_impl)
    monkeypatch.setitem(sys.modules, 'httpx', httpx_stub)

    client = MLClient()
    payload = [{'packet_size': 1.0}]

    result = asyncio.run(client.score(payload))

    assert result == {'anomaly_score': 0.91, 'model_version': 'v1'}
    assert client_impl.calls
    called_url, called_json = client_impl.calls[0]
    assert called_url.endswith('/inference')
    assert called_json == {'samples': payload}


def test_ml_client_falls_back_to_average_score_when_http_call_fails(monkeypatch):
    class BrokenAsyncClient:
        async def __aenter__(self):
            raise RuntimeError('network unavailable')

        async def __aexit__(self, exc_type, exc, tb):
            return False

    httpx_stub = SimpleNamespace(AsyncClient=lambda timeout: BrokenAsyncClient())
    monkeypatch.setitem(sys.modules, 'httpx', httpx_stub)

    client = MLClient()
    result = asyncio.run(client.score([{'a': 0.2, 'b': 0.6}, {'c': 2.0}]))

    assert result == {'anomaly_score': 0.9333333333333332, 'model_version': 'fallback-v1'}
