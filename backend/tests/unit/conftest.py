import pytest


@pytest.fixture(autouse=True)
def forbid_real_databases(monkeypatch):
    def _raise_postgres(*args, **kwargs):
        raise AssertionError('Unit tests must not use real PostgreSQL connection')

    def _raise_influx(*args, **kwargs):
        raise AssertionError('Unit tests must not use real InfluxDB connection')

    monkeypatch.setattr('backend.app.core.postgres.get_postgres_connection', _raise_postgres)
    monkeypatch.setattr('backend.app.core.influx.get_influx_client', _raise_influx)
