import asyncio
from datetime import datetime, timezone, timedelta
from backend.app.services.detection_service import DetectionService
from backend.app.api.schemas.detection import DetectionRunRequest


def test_detection_service_run():
    service = DetectionService()
    now = datetime.now(timezone.utc)
    result = asyncio.run(service.run(DetectionRunRequest(
        detector_config_id='det-1',
        window_start=now - timedelta(minutes=1),
        window_end=now,
        initiated_by='tester'
    )))
    assert result.id
    assert result.model_version
