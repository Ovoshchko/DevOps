from backend.app.repositories.detector_repository import DetectorRepository
from backend.app.api.schemas.detector import DetectorConfigCreate


def test_detector_repository_persists_to_store_file():
    repo = DetectorRepository()
    created = repo.create(
        DetectorConfigCreate(
            name='persist-profile',
            description='persist test',
            sensitivity=0.5,
            window_size_seconds=60,
            window_step_seconds=30,
            features=['bytes_per_sec'],
            status='active',
        )
    )

    repo_reloaded = DetectorRepository()
    fetched = repo_reloaded.get(created.id)
    assert fetched is not None
    assert fetched.name == 'persist-profile'
