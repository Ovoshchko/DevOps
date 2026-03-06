from __future__ import annotations

from contextlib import contextmanager
from threading import Lock
from typing import Iterator

from .settings import settings


class PostgresUnavailableError(RuntimeError):
    pass


def is_postgres_configured() -> bool:
    return settings.postgres_dsn.startswith('postgresql://')


def is_postgres_available() -> bool:
    if not is_postgres_configured():
        return False
    try:
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except Exception:
        return False


_schema_lock = Lock()
_schema_initialized = False


def ensure_postgres_schema() -> None:
    global _schema_initialized
    if _schema_initialized:
        return

    with _schema_lock:
        if _schema_initialized:
            return

        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS detector_profiles (
                      id TEXT PRIMARY KEY,
                      name TEXT NOT NULL UNIQUE,
                      description TEXT,
                      status TEXT NOT NULL,
                      sensitivity DOUBLE PRECISION NOT NULL,
                      window_size_seconds INTEGER NOT NULL,
                      window_step_seconds INTEGER NOT NULL,
                      features JSONB NOT NULL,
                      created_at TIMESTAMPTZ NOT NULL,
                      updated_at TIMESTAMPTZ NOT NULL
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS detection_runs (
                      id TEXT PRIMARY KEY,
                      detector_config_id TEXT NOT NULL REFERENCES detector_profiles(id),
                      window_start TIMESTAMPTZ NOT NULL,
                      window_end TIMESTAMPTZ NOT NULL,
                      initiated_by TEXT,
                      status TEXT NOT NULL,
                      summary JSONB,
                      created_at TIMESTAMPTZ NOT NULL,
                      completed_at TIMESTAMPTZ
                    );
                    """
                )
                cur.execute(
                    "ALTER TABLE detection_runs ADD COLUMN IF NOT EXISTS detector_config_id TEXT;"
                )
                cur.execute(
                    """
                    DO $$
                    BEGIN
                        IF EXISTS (
                            SELECT 1
                            FROM information_schema.columns
                            WHERE table_name = 'detection_runs' AND column_name = 'detector_profile_id'
                        ) THEN
                            UPDATE detection_runs
                            SET detector_config_id = detector_profile_id
                            WHERE detector_config_id IS NULL;
                        END IF;
                    END
                    $$;
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS detection_results (
                      id TEXT PRIMARY KEY,
                      detection_run_id TEXT NOT NULL REFERENCES detection_runs(id),
                      timestamp TIMESTAMPTZ NOT NULL,
                      anomaly_score DOUBLE PRECISION NOT NULL,
                      is_anomaly BOOLEAN NOT NULL,
                      metrics_snapshot JSONB NOT NULL,
                      explanation TEXT
                    );
                    """
                )
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS generator_jobs (
                      id TEXT PRIMARY KEY,
                      profile_name TEXT NOT NULL,
                      status TEXT NOT NULL,
                      batch_size INTEGER NOT NULL,
                      interval_ms INTEGER NOT NULL,
                      duration_seconds INTEGER NOT NULL,
                      sent_batches INTEGER NOT NULL,
                      total_batches INTEGER NOT NULL,
                      last_error TEXT,
                      started_at TIMESTAMPTZ NOT NULL,
                      finished_at TIMESTAMPTZ
                    );
                    """
                )
            conn.commit()

        _schema_initialized = True


@contextmanager
def get_postgres_connection() -> Iterator[object]:
    if not is_postgres_configured():
        raise PostgresUnavailableError('PostgreSQL DSN is not configured')

    try:
        import psycopg
    except Exception as exc:  # pragma: no cover - optional dependency path
        raise PostgresUnavailableError('psycopg is not installed') from exc

    conn = psycopg.connect(settings.postgres_dsn)
    try:
        yield conn
    finally:
        conn.close()
