from __future__ import annotations

from ..model.anomaly_model import score_samples


def run_inference(samples: list[dict[str, float]]) -> dict:
    score = score_samples(samples)
    return {
        "anomaly_score": score,
        "is_anomaly": score >= 0.7,
        "model_version": "simple-v1",
    }
