from backend.app.api.schemas.generator import GeneratorJobCreate
from backend.app.services.generator_service import GeneratorService


class FakeGeneratorRepo:
    def __init__(self):
        self.items = {}
        self.last_update = None

    def create(self, payload):
        item = {"id": "job-1", "status": "running", **payload.model_dump()}
        self.items[item["id"]] = item
        return item

    def get(self, job_id):
        return self.items.get(job_id)

    def update(self, job_id, patch):
        self.last_update = patch
        if job_id not in self.items:
            return None
        self.items[job_id].update(patch)
        return self.items[job_id]


def test_generator_job_service_state_transitions():
    repo = FakeGeneratorRepo()
    service = GeneratorService(repo=repo)

    job = service.create(
        GeneratorJobCreate(
            profile_name='demo',
            batch_size=5,
            interval_ms=1000,
            duration_seconds=5,
        )
    )
    assert job["status"] == 'running'

    stopped = service.stop(job["id"])
    assert stopped is not None
    assert stopped["status"] == 'stopped'
    assert repo.last_update is not None
    assert repo.last_update.get('status') == 'stopped'
    assert isinstance(repo.last_update.get('finished_at'), str)
