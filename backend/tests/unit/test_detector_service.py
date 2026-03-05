from backend.app.services.detector_service import DetectorService
from backend.app.api.schemas.detector import DetectorConfigCreate


def test_detector_service_create_and_list():
    service = DetectorService()
    created = service.create(DetectorConfigCreate(
        name='svc1',
        description='x',
        sensitivity=0.5,
        window_size_seconds=60,
        window_step_seconds=30,
        features=['f1']
    ))
    assert created.id
    assert any(d.id == created.id for d in service.list())
