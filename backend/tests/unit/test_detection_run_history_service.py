from datetime import datetime, timedelta, timezone
import asyncio

from backend.app.api.schemas.detection import DetectionRunRequest
from backend.app.api.schemas.detector import DetectorConfigCreate
from backend.app.repositories.detector_repository import DetectorRepository
from backend.app.services.detection_service import DetectionService


def test_detection_service_returns_run_history_entries():
    detector = DetectorRepository().create(
        DetectorConfigCreate(
            name='history-detector',
            description='history test detector',
            sensitivity=0.55,
            window_size_seconds=120,
            window_step_seconds=30,
            features=['bytes_per_sec'],
            status='active',
        )
    )
    service = DetectionService()
    now = datetime.now(timezone.utc)

    run = asyncio.run(
        service.run(
            DetectionRunRequest(
                detector_config_id=detector.id,
                window_start=now - timedelta(minutes=1),
                window_end=now,
            )
        )
    )

    listed = service.list()
    assert any(item.id == run.id for item in listed)
