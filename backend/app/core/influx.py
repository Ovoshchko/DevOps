from __future__ import annotations

from influxdb_client import InfluxDBClient
from .settings import settings


def get_influx_client() -> InfluxDBClient:
    return InfluxDBClient(
        url=settings.influx_url,
        token=settings.influx_token,
        org=settings.influx_org,
    )


def is_influx_available() -> bool:
    try:
        with get_influx_client() as client:
            return bool(client.ping())
    except Exception:
        return False
