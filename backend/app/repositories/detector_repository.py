from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

try:  # pragma: no cover - exercised in integration/runtime environments
    from psycopg.rows import dict_row
    from psycopg.types.json import Json
except Exception:  # pragma: no cover - allows unit tests without psycopg installed
    dict_row = None

    class Json:  # type: ignore[no-redef]
        def __init__(self, obj):
            self.obj = obj

from ..api.schemas.detector import DetectorConfigCreate, DetectorConfigOut, DetectorConfigUpdate, DetectorStatus
from ..core.postgres import ensure_postgres_schema, get_postgres_connection


class DetectorRepository:
    def __init__(self) -> None:
        pass

    def create(self, payload: DetectorConfigCreate) -> DetectorConfigOut:
        ensure_postgres_schema()
        now = datetime.now(timezone.utc)
        detector = DetectorConfigOut(
            id=str(uuid4()),
            created_at=now,
            updated_at=now,
            **payload.model_dump(),
        )

        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    INSERT INTO detector_profiles (
                        id, name, description, status, sensitivity,
                        window_size_seconds, window_step_seconds, features,
                        created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        description = EXCLUDED.description,
                        status = EXCLUDED.status,
                        sensitivity = EXCLUDED.sensitivity,
                        window_size_seconds = EXCLUDED.window_size_seconds,
                        window_step_seconds = EXCLUDED.window_step_seconds,
                        features = EXCLUDED.features,
                        updated_at = EXCLUDED.updated_at
                    RETURNING *
                    """,
                    (
                        detector.id,
                        detector.name,
                        detector.description,
                        detector.status.value,
                        detector.sensitivity,
                        detector.window_size_seconds,
                        detector.window_step_seconds,
                        Json(detector.features),
                        detector.created_at,
                        detector.updated_at,
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        return DetectorConfigOut.model_validate(row)

    def list(self) -> list[DetectorConfigOut]:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM detector_profiles ORDER BY created_at DESC")
                rows = cur.fetchall()
        return [DetectorConfigOut.model_validate(row) for row in rows]

    def get(self, detector_id: str) -> DetectorConfigOut | None:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM detector_profiles WHERE id = %s", (detector_id,))
                row = cur.fetchone()
        if row:
            return DetectorConfigOut.model_validate(row)
        return None

    def update(self, detector_id: str, payload: DetectorConfigUpdate) -> DetectorConfigOut | None:
        ensure_postgres_schema()
        patch = payload.model_dump(exclude_none=True)
        if not patch:
            return self.get(detector_id)

        assignments: list[str] = []
        values: list[object] = []
        for key, value in patch.items():
            if key == 'features':
                value = Json(value)
            if key == 'status' and isinstance(value, DetectorStatus):
                value = value.value
            assignments.append(f"{key} = %s")
            values.append(value)
        assignments.append("updated_at = %s")
        values.append(datetime.now(timezone.utc))
        values.append(detector_id)

        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    f"UPDATE detector_profiles SET {', '.join(assignments)} WHERE id = %s RETURNING *",
                    tuple(values),
                )
                row = cur.fetchone()
            conn.commit()
        if row:
            return DetectorConfigOut.model_validate(row)
        return None

    def delete(self, detector_id: str) -> bool:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE detector_profiles
                    SET status = %s, updated_at = %s
                    WHERE id = %s
                    """,
                    (DetectorStatus.archived.value, datetime.now(timezone.utc), detector_id),
                )
                updated = cur.rowcount > 0
            conn.commit()
        return updated
