import asyncio
from datetime import datetime, timedelta, timezone

from backend.app.api.schemas.detection import DetectionRunRequest
from backend.app.api.schemas.detector import DetectorConfigCreate
from backend.app.repositories.detector_repository import DetectorRepository
from backend.app.services.detection_service import DetectionService


def test_detection_service_run():
    detector = DetectorRepository().create(
        DetectorConfigCreate(
            name='unit-detector',
            description='unit test detector',
            sensitivity=0.5,
            window_size_seconds=60,
            window_step_seconds=30,
            features=['bytes_per_sec'],
            status='active',
        )
    )
    service = DetectionService()
    now = datetime.now(timezone.utc)
    result = asyncio.run(
        service.run(
            DetectionRunRequest(
                detector_config_id=detector.id,
                window_start=now - timedelta(minutes=1),
                window_end=now,
                initiated_by='tester',
            )
        )
    )
    assert result.id
    assert result.status in {'running', 'completed'}
    assert result.summary is not None
    assert result.summary.get('threshold') == 0.5
