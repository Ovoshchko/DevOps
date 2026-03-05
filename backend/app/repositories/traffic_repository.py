from __future__ import annotations

from ..api.schemas.traffic import TrafficPoint


class TrafficRepository:
    _points: list[TrafficPoint] = []

    def ingest(self, points: list[TrafficPoint]) -> int:
        self._points.extend(points)
        return len(points)

    def latest(self, limit: int = 20) -> list[TrafficPoint]:
        return self._points[-limit:]
