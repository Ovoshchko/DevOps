from __future__ import annotations

try:  # pragma: no cover - exercised in integration/runtime environments
    from psycopg.rows import dict_row
    from psycopg.types.json import Json
except Exception:  # pragma: no cover - allows unit tests without psycopg installed
    dict_row = None

    class Json:  # type: ignore[no-redef]
        def __init__(self, obj):
            self.obj = obj

from ..api.schemas.detection import DetectionResult, DetectionRunOut
from ..core.postgres import ensure_postgres_schema, get_postgres_connection


class DetectionRepository:
    def __init__(self) -> None:
        pass

    def save_run(self, run: DetectionRunOut) -> DetectionRunOut:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO detection_runs (
                        id, detector_config_id, window_start, window_end, initiated_by,
                        status, summary, created_at, completed_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        run.id,
                        run.detector_config_id,
                        run.window_start,
                        run.window_end,
                        run.initiated_by,
                        run.status,
                        Json(run.summary) if run.summary is not None else None,
                        run.created_at,
                        run.completed_at,
                    ),
                )
            conn.commit()
        return run

    def update_run(self, run_id: str, patch: dict) -> DetectionRunOut | None:
        ensure_postgres_schema()
        if not patch:
            return self.get_run(run_id)

        allowed = {
            'window_start',
            'window_end',
            'initiated_by',
            'status',
            'summary',
            'created_at',
            'completed_at',
        }
        assignments: list[str] = []
        values: list[object] = []
        for key, value in patch.items():
            if key not in allowed:
                continue
            if key == 'summary':
                value = Json(value) if value is not None else None
            assignments.append(f"{key} = %s")
            values.append(value)

        if not assignments:
            return self.get_run(run_id)

        values.append(run_id)
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    f"UPDATE detection_runs SET {', '.join(assignments)} WHERE id = %s RETURNING *",
                    tuple(values),
                )
                row = cur.fetchone()
            conn.commit()
        if row:
            return DetectionRunOut.model_validate(row)
        return None

    def save_result(self, result: DetectionResult) -> DetectionResult:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO detection_results (
                        id, detection_run_id, timestamp, anomaly_score, is_anomaly,
                        metrics_snapshot, explanation
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        result.id,
                        result.detection_run_id,
                        result.timestamp,
                        result.anomaly_score,
                        result.is_anomaly,
                        Json(result.metrics_snapshot),
                        result.explanation,
                    ),
                )
            conn.commit()
        return result

    def list_runs(self, detector_profile_id: str | None = None) -> list[DetectionRunOut]:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if detector_profile_id:
                    cur.execute(
                        """
                        SELECT * FROM detection_runs
                        WHERE detector_config_id = %s
                        ORDER BY created_at DESC
                        """,
                        (detector_profile_id,),
                    )
                else:
                    cur.execute("SELECT * FROM detection_runs ORDER BY created_at DESC")
                rows = cur.fetchall()
        return [DetectionRunOut.model_validate(row) for row in rows]

    def get_run(self, detection_id: str) -> DetectionRunOut | None:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("SELECT * FROM detection_runs WHERE id = %s", (detection_id,))
                row = cur.fetchone()
        if row:
            return DetectionRunOut.model_validate(row)
        return None

    def get_results(self, detection_id: str) -> list[DetectionResult]:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    """
                    SELECT * FROM detection_results
                    WHERE detection_run_id = %s
                    ORDER BY timestamp DESC
                    """,
                    (detection_id,),
                )
                rows = cur.fetchall()
        return [DetectionResult.model_validate(row) for row in rows]

    def latest_results(self, detector_profile_id: str | None = None, limit: int = 20) -> list[DetectionResult]:
        ensure_postgres_schema()
        with get_postgres_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                if detector_profile_id:
                    cur.execute(
                        """
                        SELECT drs.*
                        FROM detection_results drs
                        JOIN detection_runs drn ON drs.detection_run_id = drn.id
                        WHERE drn.detector_config_id = %s
                        ORDER BY drs.timestamp DESC
                        LIMIT %s
                        """,
                        (detector_profile_id, limit),
                    )
                else:
                    cur.execute(
                        "SELECT * FROM detection_results ORDER BY timestamp DESC LIMIT %s",
                        (limit,),
                    )
                rows = cur.fetchall()
        return [DetectionResult.model_validate(row) for row in rows]
