from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Mapping
from uuid import uuid4

from ..api.schemas.detection import DetectionResult, DetectionRunOut, DetectionRunRequest
from ..api.schemas.traffic import TrafficPoint
from ..services.ml_client import MLClient

if TYPE_CHECKING:
    from ..repositories.detection_repository import DetectionRepository
    from ..repositories.detector_repository import DetectorRepository
    from ..repositories.traffic_repository import TrafficRepository


MODEL_FEATURE_NAMES: tuple[str, ...] = (
    "packet_size",
    "inter_arrival_time",
    "src_port",
    "dst_port",
    "packet_count_5s",
    "mean_packet_size",
    "spectral_entropy",
    "frequency_band_energy",
    "protocol_type_TCP",
    "protocol_type_UDP",
    "src_ip_192.168.1.2",
    "src_ip_192.168.1.3",
    "dst_ip_192.168.1.5",
    "dst_ip_192.168.1.6",
    "tcp_flags_FIN",
    "tcp_flags_SYN",
    "tcp_flags_SYN-ACK",
)

MODEL_FEATURE_DEFAULTS: dict[str, float] = {feature_name: 0.0 for feature_name in MODEL_FEATURE_NAMES}


def _coerce_metric_value(value: object) -> float | None:
    return TrafficPoint.coerce_metric_value(value)


def _normalize_metrics(raw_metrics: Mapping[str, object]) -> dict[str, float]:
    return {
        key: coerced
        for key, value in raw_metrics.items()
        if (coerced := _coerce_metric_value(value)) is not None
    }


def _derive_feature_value(metrics: Mapping[str, float], feature_name: str) -> float:
    direct = metrics.get(feature_name)
    if direct is not None:
        return direct

    bytes_per_sec = metrics.get("bytes_per_sec")
    packets_per_sec = metrics.get("packets_per_sec")

    if feature_name in {"packet_size", "mean_packet_size"}:
        if bytes_per_sec is not None and packets_per_sec not in (None, 0.0):
            return bytes_per_sec / packets_per_sec
        if bytes_per_sec is not None:
            return bytes_per_sec
    if feature_name == "packet_count_5s" and packets_per_sec is not None:
        return packets_per_sec * 5.0
    if feature_name == "inter_arrival_time" and packets_per_sec not in (None, 0.0):
        return 1.0 / packets_per_sec

    return MODEL_FEATURE_DEFAULTS[feature_name]


def prepare_inference_sample(raw_metrics: Mapping[str, object]) -> dict[str, float]:
    normalized_metrics = _normalize_metrics(raw_metrics)
    return {
        feature_name: _derive_feature_value(normalized_metrics, feature_name)
        for feature_name in MODEL_FEATURE_NAMES
    }


class DetectionService:
    def __init__(
        self,
        detection_repo: DetectionRepository | None = None,
        detector_repo: DetectorRepository | None = None,
        traffic_repo: TrafficRepository | None = None,
        ml_client: MLClient | None = None,
    ) -> None:
        if detection_repo is None:
            from ..repositories.detection_repository import DetectionRepository

            detection_repo = DetectionRepository()
        if detector_repo is None:
            from ..repositories.detector_repository import DetectorRepository

            detector_repo = DetectorRepository()
        if traffic_repo is None:
            from ..repositories.traffic_repository import TrafficRepository

            traffic_repo = TrafficRepository()

        self.detection_repo = detection_repo
        self.detector_repo = detector_repo
        self.traffic_repo = traffic_repo
        self.ml_client = ml_client or MLClient()

    async def run(self, req: DetectionRunRequest) -> DetectionRunOut:
        detector = self.detector_repo.get(req.detector_config_id)
        if detector is None:
            raise LookupError(f'Detector {req.detector_config_id} not found')
        detector_status = getattr(detector.status, 'value', detector.status)
        if detector_status == 'archived':
            raise ValueError(f'Detector {req.detector_config_id} is archived and cannot be used')

        effective_window_end = req.window_end
        effective_window_start = effective_window_end - timedelta(seconds=detector.window_size_seconds)

        now = datetime.now(timezone.utc)
        run = DetectionRunOut(
            id=str(uuid4()),
            detector_config_id=req.detector_config_id,
            window_start=effective_window_start,
            window_end=effective_window_end,
            initiated_by=req.initiated_by,
            status='running',
            summary=None,
            created_at=now,
            completed_at=None,
        )
        self.detection_repo.save_run(run)

        points = self.traffic_repo.latest(limit=max(20, detector.window_size_seconds))
        metrics: list[dict[str, float]] = []
        raw_metric_snapshots: list[dict[str, float]] = []
        for point in points:
            raw_metric_snapshots.append(_normalize_metrics(point.metrics))
            metrics.append(prepare_inference_sample(point.metrics))

        ml = await self.ml_client.score(metrics)
        score = float(ml.get('anomaly_score', 0.0))
        threshold = float(detector.sensitivity)
        is_anomaly = score >= threshold

        result = DetectionResult(
            id=str(uuid4()),
            detection_run_id=run.id,
            timestamp=now,
            anomaly_score=score,
            is_anomaly=is_anomaly,
            metrics_snapshot=(raw_metric_snapshots[-1] if raw_metric_snapshots else {}),
            explanation=f"detector={detector.name}; threshold={threshold}; features={','.join(detector.features)}",
        )
        self.detection_repo.save_result(result)

        completed = self.detection_repo.update_run(
            run.id,
            {
                'status': 'completed',
                'completed_at': datetime.now(timezone.utc).isoformat(),
                'summary': {
                    'anomaly_score': score,
                    'is_anomaly': is_anomaly,
                    'threshold': threshold,
                    'window_size_seconds': detector.window_size_seconds,
                    'window_step_seconds': detector.window_step_seconds,
                    'features': detector.features,
                    'result_count': len(self.detection_repo.get_results(run.id)),
                },
            },
        )
        return completed or run

    def list(self, detector_profile_id: str | None = None) -> list[DetectionRunOut]:
        return self.detection_repo.list_runs(detector_profile_id=detector_profile_id)

    def get(self, detection_id: str) -> DetectionRunOut | None:
        return self.detection_repo.get_run(detection_id)

    def get_results(self, detection_id: str) -> list[DetectionResult]:
        return self.detection_repo.get_results(detection_id)
