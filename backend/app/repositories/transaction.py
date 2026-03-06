from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def transactional_scope() -> Iterator[None]:
    """Unified transaction boundary for repository operations.

    Repositories own transaction boundaries directly via DB drivers,
    so this scope is reserved for future cross-repository orchestration.
    """

    yield
