from __future__ import annotations

from ..api.schemas.detection import DetectionResult


class DetectionRepository:
    _results: dict[str, DetectionResult] = {}

    def save(self, result: DetectionResult) -> DetectionResult:
        self._results[result.id] = result
        return result

    def list(self) -> list[DetectionResult]:
        return list(self._results.values())

    def get(self, detection_id: str) -> DetectionResult | None:
        return self._results.get(detection_id)

    def latest(self, limit: int = 20) -> list[DetectionResult]:
        return list(self._results.values())[-limit:]
