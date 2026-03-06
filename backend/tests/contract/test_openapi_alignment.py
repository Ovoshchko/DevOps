from backend.app.main import app


def test_openapi_contains_required_paths():
    openapi = app.openapi()
    paths = set(openapi.get('paths', {}).keys())

    for required in [
        '/detectors',
        '/traffic/ingest',
        '/detections/run',
        '/detections/{detection_id}/results',
        '/traffic/latest',
        '/anomalies/latest',
        '/generator/jobs',
        '/generator/jobs/{job_id}',
        '/generator/jobs/{job_id}/stop',
    ]:
        assert required in paths
