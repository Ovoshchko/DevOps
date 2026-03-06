from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from ..api.schemas.detector import DetectorConfigCreate, DetectorConfigOut, DetectorConfigUpdate, DetectorStatus
from .json_store import JsonStore


class DetectorRepository:
    _lock = Lock()

    def __init__(self) -> None:
        self.store = JsonStore('detector_profiles')

    def create(self, payload: DetectorConfigCreate) -> DetectorConfigOut:
        now = datetime.now(timezone.utc)
        detector = DetectorConfigOut(
            id=str(uuid4()),
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )
        with self._lock:
            rows = self.store.read()
            rows.append(detector.model_dump(mode='json'))
            self.store.write(rows)
        return detector

    def list(self) -> list[DetectorConfigOut]:
        with self._lock:
            rows = self.store.read()
        return [DetectorConfigOut.model_validate(row) for row in rows]

    def get(self, detector_id: str) -> DetectorConfigOut | None:
        with self._lock:
            rows = self.store.read()
        for row in rows:
            if row.get('id') == detector_id:
                return DetectorConfigOut.model_validate(row)
        return None

    def update(self, detector_id: str, payload: DetectorConfigUpdate) -> DetectorConfigOut | None:
        with self._lock:
            rows = self.store.read()
            for idx, row in enumerate(rows):
                if row.get('id') != detector_id:
                    continue
                merged = {
                    **row,
                    **payload.model_dump(exclude_none=True),
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                }
                rows[idx] = merged
                self.store.write(rows)
                return DetectorConfigOut.model_validate(merged)
        return None

    def delete(self, detector_id: str) -> bool:
        with self._lock:
            rows = self.store.read()
            for idx, row in enumerate(rows):
                if row.get('id') != detector_id:
                    continue
                row['status'] = DetectorStatus.archived.value
                row['updated_at'] = datetime.now(timezone.utc).isoformat()
                rows[idx] = row
                self.store.write(rows)
                return True
        return False
