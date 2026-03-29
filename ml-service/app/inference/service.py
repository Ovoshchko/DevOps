from __future__ import annotations

from ..core.settings import settings
from ..model.anomaly_model import ModelBundle
from ..model.anomaly_model import load_model_bundle
from ..model.anomaly_model import score_samples


def run_inference(
    samples: list[dict[str, float]],
    *,
    threshold: float | None = None,
    model_dir: str | None = None,
    bundle_loader=load_model_bundle,
    bundle: ModelBundle | None = None,
) -> dict:
    active_threshold = settings.threshold if threshold is None else threshold
    score, model_version = score_samples(
        samples,
        bundle=bundle,
        bundle_loader=bundle_loader,
        model_dir=model_dir or settings.model_dir,
        version=settings.model_version,
    )
    return {
        "anomaly_score": score,
        "is_anomaly": score >= active_threshold,
        "model_version": model_version,
    }
