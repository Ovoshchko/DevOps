from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from .settings import settings


class PostgresUnavailableError(RuntimeError):
    pass


def is_postgres_configured() -> bool:
    return settings.postgres_dsn.startswith('postgresql://')


@contextmanager
def get_postgres_connection() -> Iterator[object]:
    """Optional runtime connection provider.

    The repository layer can work with file-backed persistence if PostgreSQL
    connectivity is unavailable in local/dev tests.
    """

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
