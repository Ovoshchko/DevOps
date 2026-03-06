from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from psycopg.rows import dict_row

from ..api.schemas.generator import GeneratorJobCreate, GeneratorJobOut
from ..core.postgres import ensure_postgres_schema, get_postgres_connection


class GeneratorRepository:
    def __init__(self) -> None:
        pass

    def create(self, payload: GeneratorJobCreate) -> GeneratorJobOut:
        ensure_postgres_schema()
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
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO generator_jobs (
                        id, profile_name, status, batch_size, interval_ms,
                        duration_seconds, sent_batches, total_batches, last_error,
                        started_at, finished_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        job.id,
                        job.profile_name,
                        job.status,
                        job.batch_size,
                        job.interval_ms,
                        job.duration_seconds,
                        job.sent_batches,
                        job.total_batches,
                        job.last_error,
                        job.started_at,
                        job.finished_at,
                    ),
                )
            conn.commit()
        return job

    def get(self, job_id: str) -> GeneratorJobOut | None:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM generator_jobs WHERE id = %s", (job_id,))
                row = cur.fetchone()
        if row:
            return GeneratorJobOut.model_validate(row)
        return None

    def update(self, job_id: str, patch: dict) -> GeneratorJobOut | None:
        ensure_postgres_schema()
        if not patch:
            return self.get(job_id)

        allowed = {
            'status',
            'batch_size',
            'interval_ms',
            'duration_seconds',
            'sent_batches',
            'total_batches',
            'last_error',
            'finished_at',
        }
        assignments: list[str] = []
        values: list[object] = []
        for key, value in patch.items():
            if key not in allowed:
                continue
            assignments.append(f"{key} = %s")
            values.append(value)

        if not assignments:
            return self.get(job_id)

        values.append(job_id)
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    f"UPDATE generator_jobs SET {', '.join(assignments)} WHERE id = %s RETURNING *",
                    tuple(values),
                )
                row = cur.fetchone()
            conn.commit()
        if row:
            return GeneratorJobOut.model_validate(row)
        return None
