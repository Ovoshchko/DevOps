from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from ..api.schemas.generator import GeneratorJobCreate, GeneratorJobOut
from .json_store import JsonStore


class GeneratorRepository:
    def __init__(self) -> None:
        self.store = JsonStore('generator_jobs')

    def create(self, payload: GeneratorJobCreate) -> GeneratorJobOut:
        now = datetime.now(timezone.utc)
        job = GeneratorJobOut(
            id=str(uuid4()),
            profile_name=payload.profile_name,
            status='running',
            batch_size=payload.batch_size,
            interval_ms=payload.interval_ms,
            duration_seconds=payload.duration_seconds,
            sent_batches=0,
            total_batches=max(1, int((payload.duration_seconds * 1000) / payload.interval_ms)),
            last_error=None,
            started_at=now,
            finished_at=None,
        )
        rows = self.store.read()
        rows.append(job.model_dump(mode='json'))
        self.store.write(rows)
        return job

    def get(self, job_id: str) -> GeneratorJobOut | None:
        for row in self.store.read():
            if row.get('id') == job_id:
                return GeneratorJobOut.model_validate(row)
        return None

    def update(self, job_id: str, patch: dict) -> GeneratorJobOut | None:
        rows = self.store.read()
        for idx, row in enumerate(rows):
            if row.get('id') != job_id:
                continue
            row.update(patch)
            rows[idx] = row
            self.store.write(rows)
            return GeneratorJobOut.model_validate(row)
        return None
