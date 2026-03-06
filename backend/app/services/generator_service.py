from __future__ import annotations

from datetime import datetime, timezone

from ..api.schemas.generator import GeneratorJobCreate
from ..repositories.generator_repository import GeneratorRepository


class GeneratorService:
    def __init__(self, repo: GeneratorRepository | None = None) -> None:
        self.repo = repo or GeneratorRepository()

    def create(self, payload: GeneratorJobCreate):
        return self.repo.create(payload)

    def get(self, job_id: str):
        return self.repo.get(job_id)

    def stop(self, job_id: str):
        return self.repo.update(
            job_id,
            {
                'status': 'stopped',
                'finished_at': datetime.now(timezone.utc).isoformat(),
            },
        )
