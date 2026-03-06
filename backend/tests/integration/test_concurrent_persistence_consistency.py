from concurrent.futures import ThreadPoolExecutor

from backend.app.api.schemas.detector import DetectorConfigCreate
from backend.app.repositories.detector_repository import DetectorRepository


def test_concurrent_detector_writes_keep_consistent_count():
    repo = DetectorRepository()

    def write_one(idx: int):
        repo.create(
            DetectorConfigCreate(
                name=f'concurrent-{idx}',
                description='c',
                sensitivity=0.5,
                window_size_seconds=60,
                window_step_seconds=30,
                features=['bytes_per_sec'],
                status='active',
            )
        )

    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(write_one, range(4)))

    names = [d.name for d in repo.list()]
    for idx in range(4):
        assert f'concurrent-{idx}' in names
