from __future__ import annotations

from influxdb_client import InfluxDBClient
from .settings import settings


def get_influx_client() -> InfluxDBClient:
    return InfluxDBClient(
        url=settings.influx_url,
        token=settings.influx_token,
        org=settings.influx_org,
    )
