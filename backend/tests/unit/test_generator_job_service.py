from backend.app.api.schemas.generator import GeneratorJobCreate
from backend.app.services.generator_service import GeneratorService


def test_generator_job_service_state_transitions():
    service = GeneratorService()

    job = service.create(
        GeneratorJobCreate(
            profile_name='demo',
            batch_size=5,
            interval_ms=1000,
            duration_seconds=5,
        )
    )
    assert job.status == 'running'

    stopped = service.stop(job.id)
    assert stopped is not None
    assert stopped.status == 'stopped'
