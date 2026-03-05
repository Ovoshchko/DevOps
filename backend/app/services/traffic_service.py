from __future__ import annotations

from ..api.schemas.traffic import TrafficIngestRequest
from ..repositories.traffic_repository import TrafficRepository


class TrafficService:
    def __init__(self, repo: TrafficRepository | None = None) -> None:
        self.repo = repo or TrafficRepository()

    def ingest(self, req: TrafficIngestRequest) -> int:
        return self.repo.ingest(req.points)

    def latest(self):
        return self.repo.latest()
