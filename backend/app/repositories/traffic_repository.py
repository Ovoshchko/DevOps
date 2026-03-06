from __future__ import annotations

from collections import OrderedDict

from influxdb_client import Point

from ..api.schemas.traffic import TrafficPoint
from ..core.influx import get_influx_client
from ..core.settings import settings


class TrafficRepository:
    def ingest(self, points: list[TrafficPoint]) -> int:
        with get_influx_client() as client:
            writer = client.write_api()
            records: list[Point] = []
            for point in points:
                influx_point = (
                    Point("traffic")
                    .time(point.timestamp)
                    .tag("source_id", point.source_id)
                )
                if point.tags:
                    for key, value in point.tags.items():
                        influx_point = influx_point.tag(key, value)
                for metric_name, metric_value in point.metrics.items():
                    influx_point = influx_point.field(metric_name, float(metric_value))
                records.append(influx_point)
            writer.write(bucket=settings.influx_bucket, org=settings.influx_org, record=records)
        return len(points)

    def latest(self, limit: int = 20) -> list[TrafficPoint]:
        flux = f"""
from(bucket: "{settings.influx_bucket}")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "traffic")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: {int(limit * 10)})
"""
        with get_influx_client() as client:
            tables = client.query_api().query(query=flux, org=settings.influx_org)

        grouped: "OrderedDict[tuple[str, str], dict]" = OrderedDict()
        system_cols = {
            "result",
            "table",
            "_start",
            "_stop",
            "_measurement",
            "_field",
            "_value",
        }
        for table in tables:
            for record in table.records:
                ts = record.get_time()
                source_id = record.values.get("source_id")
                field_name = record.values.get("_field")
                field_value = record.values.get("_value")
                if ts is None or source_id is None or field_name is None:
                    continue

                key = (ts.isoformat(), str(source_id))
                if key not in grouped:
                    tags: dict[str, str] = {}
                    for col_key, col_value in record.values.items():
                        if col_key in system_cols or col_key.startswith("_") or col_key == "source_id":
                            continue
                        if isinstance(col_value, str):
                            tags[col_key] = col_value
                    grouped[key] = {
                        "timestamp": ts,
                        "source_id": str(source_id),
                        "metrics": {},
                        "tags": tags or None,
                    }
                grouped[key]["metrics"][str(field_name)] = float(field_value)

                if len(grouped) >= limit:
                    break
            if len(grouped) >= limit:
                break

        return [
            TrafficPoint(
                timestamp=item["timestamp"],
                source_id=item["source_id"],
                metrics=item["metrics"],
                tags=item["tags"],
            )
            for item in grouped.values()
            if item["metrics"]
        ]
