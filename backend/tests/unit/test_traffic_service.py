from datetime import datetime, timezone
from backend.app.services.traffic_service import TrafficService
from backend.app.api.schemas.traffic import TrafficIngestRequest, TrafficPoint


def test_traffic_service_ingest_and_latest():
    service = TrafficService()
    count = service.ingest(TrafficIngestRequest(points=[TrafficPoint(
        timestamp=datetime.now(timezone.utc),
        source_id='s1',
        metrics={'bytes_per_sec': 0.4}
    )]))
    assert count == 1
    assert len(service.latest()) >= 1
