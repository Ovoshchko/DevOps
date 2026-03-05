from __future__ import annotations

from ..repositories.detector_repository import DetectorRepository
from ..api.schemas.detector import DetectorConfigCreate, DetectorConfigUpdate


class DetectorService:
    def __init__(self, repo: DetectorRepository | None = None) -> None:
        self.repo = repo or DetectorRepository()

    def create(self, payload: DetectorConfigCreate):
        return self.repo.create(payload)

    def list(self):
        return self.repo.list()

    def get(self, detector_id: str):
        return self.repo.get(detector_id)

    def update(self, detector_id: str, payload: DetectorConfigUpdate):
        return self.repo.update(detector_id, payload)

    def delete(self, detector_id: str):
        return self.repo.delete(detector_id)
