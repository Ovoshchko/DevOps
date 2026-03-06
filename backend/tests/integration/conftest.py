import pytest

from backend.app.core.postgres import is_postgres_available


@pytest.fixture(autouse=True)
def skip_integration_when_postgres_unavailable():
    if not is_postgres_available():
        pytest.skip("PostgreSQL is unavailable for integration tests")
