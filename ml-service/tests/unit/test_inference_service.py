from __future__ import annotations

import numpy as np
import pytest

from app.inference.service import run_inference
from app.model.anomaly_model import FEATURE_NAMES
from app.model.anomaly_model import ModelBundle
from app.model.anomaly_model import ModelLoadError


class StubScaler:
    def __init__(self) -> None:
        self.seen = None

    def transform(self, matrix):
        self.seen = matrix
        return matrix


class StubModel:
    def __init__(self, probabilities: list[list[float]]) -> None:
        self.probabilities = np.asarray(probabilities, dtype=float)
        self.seen = None

    def predict_proba(self, matrix):
        self.seen = matrix
        return self.probabilities


def _sample(value: float = 1.0) -> dict[str, float]:
    return {feature: value for feature in FEATURE_NAMES}


def _bundle(probabilities: list[list[float]] | None = None, version: str = "v0") -> ModelBundle:
    return ModelBundle(
        scaler=StubScaler(),
        model=StubModel(probabilities or [[0.2, 0.8]]),
        feature_names=FEATURE_NAMES,
        version=version,
        scaler_path="ml-service/models/v0/scaler.joblib",
        model_path="ml-service/models/v0/model.joblib",
    )


def test_inference_returns_score_flag_and_model_version_using_bundle_loader():
    bundle = _bundle(probabilities=[[0.2, 0.8], [0.6, 0.4]], version="v0")

    def fake_loader(model_dir: str, *, version: str | None = None):
        assert model_dir == "custom-model-dir"
        assert version == "v0"
        return bundle

    out = run_inference(
        [_sample(1.0), _sample(2.0)],
        threshold=0.7,
        model_dir="custom-model-dir",
        bundle_loader=fake_loader,
    )

    assert out == {
        "anomaly_score": 0.8,
        "is_anomaly": True,
        "model_version": "v0",
    }
    assert bundle.scaler.seen.shape == (2, len(FEATURE_NAMES))
    assert bundle.model.seen.shape == (2, len(FEATURE_NAMES))


def test_inference_can_use_injected_bundle_without_loading_artifacts():
    bundle = _bundle(probabilities=[[0.9, 0.1]], version="test-bundle")

    out = run_inference([_sample(3.0)], threshold=0.5, bundle=bundle)

    assert set(out) == {"anomaly_score", "is_anomaly", "model_version"}
    assert out["anomaly_score"] == 0.1
    assert out["is_anomaly"] is False
    assert out["model_version"] == "test-bundle"


def test_inference_raises_predictable_error_when_bundle_load_fails():
    def broken_loader(model_dir: str, *, version: str | None = None):
        raise ModelLoadError(f"Unable to load model artifacts from '{model_dir}'.")

    with pytest.raises(ModelLoadError, match="Unable to load model artifacts"):
        run_inference([_sample()], model_dir="broken-dir", bundle_loader=broken_loader)
