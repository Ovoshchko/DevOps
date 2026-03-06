from __future__ import annotations

from ..repositories.detection_repository import DetectionRepository
from ..repositories.traffic_repository import TrafficRepository


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

    def latest_anomalies(self, detector_profile_id: str | None = None):
        return [
            result
            for result in self.detection_repo.latest_results(detector_profile_id=detector_profile_id)
            if result.is_anomaly
        ]
