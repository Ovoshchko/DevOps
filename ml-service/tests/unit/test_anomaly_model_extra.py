from __future__ import annotations

import numpy as np
import pytest

from app.model import anomaly_model
from app.model.anomaly_model import ModelLoadError, load_model_bundle, score_samples


class LoaderScaler:
    def transform(self, matrix):
        return matrix


class LoaderModel:
    def predict(self, matrix):
        return np.asarray([1.4 for _ in range(len(matrix))], dtype=float)


def test_load_model_bundle_uses_cache_for_repeated_loads():
    anomaly_model._MODEL_BUNDLE_CACHE.clear()
    calls: list[str] = []

    def loader(path: str):
        calls.append(path)
        if path.endswith('scaler.joblib'):
            return LoaderScaler()
        return LoaderModel()

    first = load_model_bundle('ml-service/models/v0', loader=loader, use_cache=False, version='cached-v0')
    second = load_model_bundle('ml-service/models/v0', loader=loader, use_cache=False, version='cached-v0')

    assert first.version == 'cached-v0'
    assert second.version == 'cached-v0'
    assert len(calls) == 4


def test_load_model_bundle_raises_model_load_error_when_artifacts_fail():
    def broken_loader(path: str):
        raise FileNotFoundError(path)

    with pytest.raises(ModelLoadError, match='Unable to load model artifacts'):
        load_model_bundle('ml-service/models/v0', loader=broken_loader, use_cache=False)


def test_score_samples_uses_predict_fallback_and_clamps_score():
    bundle = anomaly_model.ModelBundle(
        scaler=LoaderScaler(),
        model=LoaderModel(),
        feature_names=('packet_size',),
        version='predict-only',
        scaler_path='scaler.joblib',
        model_path='model.joblib',
    )

    score, version = score_samples([{'packet_size': 10.0}], bundle=bundle)

    assert score == 1.0
    assert version == 'predict-only'


def test_score_samples_requires_model_dir_when_bundle_is_missing():
    with pytest.raises(ModelLoadError, match='Model directory is required'):
        score_samples([{'packet_size': 10.0}])
