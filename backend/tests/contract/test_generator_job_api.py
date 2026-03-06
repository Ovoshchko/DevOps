from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.routes import generator as generator_route


client = TestClient(app)


def test_generator_job_lifecycle_contract_with_mock_service(monkeypatch):
    job = {
        "id": "job-1",
        "profile_name": "demo",
        "status": "running",
        "batch_size": 10,
        "interval_ms": 1000,
        "duration_seconds": 5,
        "sent_batches": 0,
        "total_batches": 5,
        "last_error": None,
        "started_at": "2026-01-01T00:00:00Z",
        "finished_at": None,
    }

    class MockService:
        def create(self, payload):
            return job

        def get(self, job_id):
            return job if job_id == "job-1" else None

        def stop(self, job_id):
            if job_id != "job-1":
                return None
            return {**job, "status": "stopped", "finished_at": "2026-01-01T00:00:01Z"}

    monkeypatch.setattr(generator_route, "service", MockService())

    created = client.post(
        "/generator/jobs",
        json={
            "profile_name": "demo",
            "batch_size": 10,
            "interval_ms": 1000,
            "duration_seconds": 5,
        },
    )
    assert created.status_code == 201, created.text
    job_id = created.json()["id"]

    fetched = client.get(f"/generator/jobs/{job_id}")
    assert fetched.status_code == 200

    stopped = client.post(f"/generator/jobs/{job_id}/stop")
    assert stopped.status_code == 200
    assert stopped.json()["status"] == "stopped"
