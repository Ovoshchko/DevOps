from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from ..api.schemas.detector import DetectorConfigCreate, DetectorConfigUpdate, DetectorConfigOut


class DetectorRepository:
    _store: dict[str, DetectorConfigOut] = {}

    def create(self, payload: DetectorConfigCreate) -> DetectorConfigOut:
        now = datetime.now(timezone.utc)
        detector = DetectorConfigOut(id=str(uuid4()), created_at=now, updated_at=now, **payload.model_dump())
        self._store[detector.id] = detector
        return detector

    def list(self) -> list[DetectorConfigOut]:
        return list(self._store.values())

    def get(self, detector_id: str) -> DetectorConfigOut | None:
        return self._store.get(detector_id)

    def update(self, detector_id: str, payload: DetectorConfigUpdate) -> DetectorConfigOut | None:
        current = self._store.get(detector_id)
        if current is None:
            return None
        updated = current.model_copy(update={**payload.model_dump(), "updated_at": datetime.now(timezone.utc)})
        self._store[detector_id] = updated
        return updated

    def delete(self, detector_id: str) -> bool:
        return self._store.pop(detector_id, None) is not None
