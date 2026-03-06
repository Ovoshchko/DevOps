from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator


@contextmanager
def transactional_scope() -> Iterator[None]:
    """Unified transaction boundary for repository operations.

    Current implementation is no-op because repositories can run in file-backed
    mode for local/test environments.
    """

    yield
