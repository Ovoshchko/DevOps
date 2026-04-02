from __future__ import annotations

from uuid import uuid4

from backend.app.api.schemas.detector import DetectorConfigCreate, DetectorConfigUpdate, DetectorStatus
from backend.app.repositories.detector_repository import DetectorRepository


def test_detector_repository_update_delete_and_missing_paths():
    repo = DetectorRepository()
    suffix = uuid4().hex[:8]

    created = repo.create(
        DetectorConfigCreate(
            name=f'mutation-detector-{suffix}',
            description='before update',
            sensitivity=0.4,
            window_size_seconds=60,
            window_step_seconds=30,
            features=['bytes_per_sec'],
            status=DetectorStatus.active,
        )
    )

    updated = repo.update(
        created.id,
        DetectorConfigUpdate(
            description='after update',
            features=['bytes_per_sec', 'packets_per_sec'],
            status=DetectorStatus.draft,
        ),
    )
    untouched = repo.update(created.id, DetectorConfigUpdate())
    deleted = repo.delete(created.id)
    archived = repo.get(created.id)

    assert updated is not None
    assert updated.description == 'after update'
    assert updated.features == ['bytes_per_sec', 'packets_per_sec']
    assert updated.status == DetectorStatus.draft
    assert untouched is not None
    assert deleted is True
    assert archived is not None
    assert archived.status == DetectorStatus.archived

    missing_update = repo.update('missing-detector', DetectorConfigUpdate(description='x'))
    missing_delete = repo.delete('missing-detector')

    assert missing_update is None
    assert missing_delete is False
