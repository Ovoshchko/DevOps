from backend.app.services.detector_service import DetectorService
from backend.app.api.schemas.detector import DetectorConfigCreate, DetectorConfigUpdate


class FakeRepo:
    def __init__(self):
        self.items = {}

    def create(self, payload):
        item = {"id": "det-1", **payload.model_dump()}
        self.items[item["id"]] = item
        return item

    def list(self):
        return list(self.items.values())

    def get(self, detector_id):
        return self.items.get(detector_id)

    def update(self, detector_id, payload):
        item = self.items.get(detector_id)
        if not item:
            return None
        item.update(payload.model_dump(exclude_none=True))
        return item

    def delete(self, detector_id):
        return self.items.pop(detector_id, None) is not None


def test_detector_service_create_list_update_get_delete():
    service = DetectorService(repo=FakeRepo())
    created = service.create(DetectorConfigCreate(
        name='svc1',
        description='x',
        sensitivity=0.5,
        window_size_seconds=60,
        window_step_seconds=30,
        features=['f1']
    ))
    assert created["id"] == "det-1"
    assert any(d["id"] == "det-1" for d in service.list())

    updated = service.update("det-1", DetectorConfigUpdate(name="svc1-updated"))
    assert updated is not None
    assert updated["name"] == "svc1-updated"

    fetched = service.get("det-1")
    assert fetched is not None
    assert fetched["name"] == "svc1-updated"

    assert service.delete("det-1") is True
    assert service.get("det-1") is None
