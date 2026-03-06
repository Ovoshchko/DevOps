from __future__ import annotations

from ..api.schemas.detection import DetectionResult, DetectionRunOut
from .json_store import JsonStore


class DetectionRepository:
    def __init__(self) -> None:
        self.runs_store = JsonStore('detection_runs')
        self.results_store = JsonStore('detection_results')

    def save_run(self, run: DetectionRunOut) -> DetectionRunOut:
        rows = self.runs_store.read()
        rows.append(run.model_dump(mode='json'))
        self.runs_store.write(rows)
        return run

    def update_run(self, run_id: str, patch: dict) -> DetectionRunOut | None:
        rows = self.runs_store.read()
        for idx, row in enumerate(rows):
            if row.get('id') != run_id:
                continue
            row.update(patch)
            rows[idx] = row
            self.runs_store.write(rows)
            return DetectionRunOut.model_validate(row)
        return None

    def save_result(self, result: DetectionResult) -> DetectionResult:
        rows = self.results_store.read()
        rows.append(result.model_dump(mode='json'))
        self.results_store.write(rows)
        return result

    def list_runs(self, detector_profile_id: str | None = None) -> list[DetectionRunOut]:
        rows = [DetectionRunOut.model_validate(row) for row in self.runs_store.read()]
        if detector_profile_id:
            rows = [item for item in rows if item.detector_config_id == detector_profile_id]
        return rows

    def get_run(self, detection_id: str) -> DetectionRunOut | None:
        for row in self.runs_store.read():
            if row.get('id') == detection_id:
                return DetectionRunOut.model_validate(row)
        return None

    def get_results(self, detection_id: str) -> list[DetectionResult]:
        rows = [DetectionResult.model_validate(row) for row in self.results_store.read()]
        return [row for row in rows if row.detection_run_id == detection_id]

    def latest_results(self, detector_profile_id: str | None = None, limit: int = 20) -> list[DetectionResult]:
        runs = {run.id: run for run in self.list_runs(detector_profile_id=detector_profile_id)}
        rows = [DetectionResult.model_validate(row) for row in self.results_store.read()]
        filtered = [row for row in rows if row.detection_run_id in runs]
        return filtered[-limit:]
