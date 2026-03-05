from pathlib import Path


def test_openapi_contains_required_paths():
    spec = Path('specs/001-traffic-anomaly-platform/contracts/openapi.yaml').read_text()
    for required in [
        '/detectors',
        '/traffic/ingest',
        '/detections/run',
        '/traffic/latest',
        '/anomalies/latest',
    ]:
        assert required in spec
