from datetime import datetime, timedelta, timezone
import asyncio

from backend.app.api.schemas.detection import DetectionRunRequest
from backend.app.services.detection_service import DetectionService


def test_detection_service_returns_run_history_entries():
    service = DetectionService()
    now = datetime.now(timezone.utc)

    run = asyncio.run(
        service.run(
            DetectionRunRequest(
                detector_config_id='demo-detector',
                window_start=now - timedelta(minutes=1),
                window_end=now,
            )
        )
    )

    listed = service.list()
    assert any(item.id == run.id for item in listed)
