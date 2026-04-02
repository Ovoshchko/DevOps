from __future__ import annotations

from datetime import datetime, timedelta, timezone
from time import sleep
from uuid import uuid4

from backend.app.api.schemas.detection import DetectionResult, DetectionRunOut
from backend.app.api.schemas.detector import DetectorConfigCreate, DetectorStatus
from backend.app.api.schemas.generator import GeneratorJobCreate
from backend.app.api.schemas.traffic import TrafficPoint
from backend.app.core.influx import is_influx_available
from backend.app.core.postgres import is_postgres_available
from backend.app.repositories.detection_repository import DetectionRepository
from backend.app.repositories.detector_repository import DetectorRepository
from backend.app.repositories.generator_repository import GeneratorRepository
from backend.app.repositories.traffic_repository import TrafficRepository


def test_runtime_datastores_are_available():
    assert is_postgres_available() is True
    assert is_influx_available() is True


def test_detector_and_generator_repositories_roundtrip_against_postgres():
    suffix = uuid4().hex[:8]
    detector_repo = DetectorRepository()
    generator_repo = GeneratorRepository()

    detector = detector_repo.create(
        DetectorConfigCreate(
            name=f'roundtrip-detector-{suffix}',
            description='repository roundtrip',
            sensitivity=0.65,
            window_size_seconds=90,
            window_step_seconds=30,
            features=['bytes_per_sec', 'packets_per_sec'],
            status=DetectorStatus.active,
        )
    )
    fetched_detector = detector_repo.get(detector.id)

    assert fetched_detector is not None
    assert fetched_detector.name == detector.name
    assert fetched_detector.features == ['bytes_per_sec', 'packets_per_sec']

    job = generator_repo.create(
        GeneratorJobCreate(
            profile_name=f'profile-{suffix}',
            batch_size=5,
            interval_ms=500,
            duration_seconds=10,
        )
    )
    fetched_job = generator_repo.get(job.id)
    updated_job = generator_repo.update(job.id, {'status': 'stopped', 'sent_batches': 2})

    assert fetched_job is not None
    assert fetched_job.profile_name == f'profile-{suffix}'
    assert updated_job is not None
    assert updated_job.status == 'stopped'
    assert updated_job.sent_batches == 2


def test_detection_repository_roundtrip_against_postgres():
    detector_suffix = uuid4().hex[:8]
    detector = DetectorRepository().create(
        DetectorConfigCreate(
            name=f'detection-detector-{detector_suffix}',
            description='detection repo test',
            sensitivity=0.7,
            window_size_seconds=60,
            window_step_seconds=30,
            features=['bytes_per_sec'],
            status=DetectorStatus.active,
        )
    )
    repo = DetectionRepository()
    now = datetime.now(timezone.utc)
    run = DetectionRunOut(
        id=str(uuid4()),
        detector_config_id=detector.id,
        window_start=now - timedelta(minutes=1),
        window_end=now,
        initiated_by='integration-test',
        status='running',
        summary=None,
        created_at=now,
        completed_at=None,
    )
    repo.save_run(run)
    result = DetectionResult(
        id=str(uuid4()),
        detection_run_id=run.id,
        timestamp=now,
        anomaly_score=0.91,
        is_anomaly=True,
        metrics_snapshot={'bytes_per_sec': 120.0},
        explanation='integration roundtrip',
    )
    repo.save_result(result)
    updated = repo.update_run(
        run.id,
        {
            'status': 'completed',
            'summary': {'anomaly_score': 0.91, 'is_anomaly': True},
            'completed_at': now.isoformat(),
        },
    )

    assert updated is not None
    assert updated.status == 'completed'
    assert repo.get_run(run.id) is not None
    assert repo.get_results(run.id)
    assert any(item.id == run.id for item in repo.list_runs(detector_profile_id=detector.id))
    assert any(item.id == result.id for item in repo.latest_results(detector_profile_id=detector.id))


def test_traffic_repository_roundtrip_against_influx():
    repo = TrafficRepository()
    source_id = f'integration-source-{uuid4().hex[:8]}'
    timestamp = datetime.now(timezone.utc)
    ingested = repo.ingest(
        [
            TrafficPoint(
                timestamp=timestamp,
                source_id=source_id,
                metrics={'bytes_per_sec': 321.0, 'packets_per_sec': 27.0},
                tags={'profile': 'integration', 'mode': 'test'},
            )
        ]
    )

    assert ingested == 1

    for _ in range(5):
        latest = repo.latest(limit=50)
        matched = [point for point in latest if point.source_id == source_id]
        if matched:
            break
        sleep(0.3)
    else:
        matched = []

    assert matched
    assert matched[0].metrics['bytes_per_sec'] == 321.0
    assert matched[0].tags == {'profile': 'integration', 'mode': 'test'}
