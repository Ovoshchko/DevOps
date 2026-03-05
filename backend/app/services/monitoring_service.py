from __future__ import annotations

from ..repositories.traffic_repository import TrafficRepository
from ..repositories.detection_repository import DetectionRepository


class MonitoringService:
    def __init__(
        self,
        traffic_repo: TrafficRepository | None = None,
        detection_repo: DetectionRepository | None = None,
    ) -> None:
        self.traffic_repo = traffic_repo or TrafficRepository()
        self.detection_repo = detection_repo or DetectionRepository()

    def latest_traffic(self):
        return self.traffic_repo.latest()

    def latest_anomalies(self):
        return [r for r in self.detection_repo.latest() if r.is_anomaly]
