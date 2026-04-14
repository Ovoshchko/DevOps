from __future__ import annotations

import numpy as np
from fastapi.testclient import TestClient

from app.inference.service import run_inference
from app.main import app
from app.model.anomaly_model import FEATURE_NAMES
from app.model.anomaly_model import ModelBundle
from app.model.anomaly_model import prepare_feature_matrix
from app.model.anomaly_model import score_samples


class PredictOnlyModel:
    def predict(self, matrix):
        return np.asarray([0.12 for _ in range(len(matrix))], dtype=float)


class IdentityScaler:
    def transform(self, matrix):
        return matrix


def test_inference_route_rejects_empty_samples_payload():
    client = TestClient(app)

    response = client.post('/inference', json={'samples': []})

    assert response.status_code == 422
    assert 'samples' in response.text


def test_health_exposes_ml_runtime_configuration():
    client = TestClient(app)

    response = client.get('/health')
    body = response.json()

    assert response.status_code == 200
    assert body['status'] == 'ok'
    assert body['model_version']
    assert body['model_dir']
    assert isinstance(body['threshold'], float)


def test_metrics_endpoint_exposes_prometheus_metrics():
    client = TestClient(app)

    response = client.get('/metrics')

    assert response.status_code == 200
    assert 'ml_service_http_requests_total' in response.text
    assert 'ml_service_http_request_duration_seconds' in response.text


def test_prepare_feature_matrix_accepts_boolean_flags_from_backend_payload():
    matrix = prepare_feature_matrix([
        {
            'bytes_per_sec': 100.0,
            'packets_per_sec': 10.0,
            'tcp_flags_SYN': True,
            'protocol_type_TCP': True,
        }
    ])

    assert matrix.shape == (1, len(FEATURE_NAMES))
    row = matrix.tolist()[0]
    assert row[FEATURE_NAMES.index('packet_size')] == 10.0
    assert row[FEATURE_NAMES.index('tcp_flags_SYN')] == 1.0
    assert row[FEATURE_NAMES.index('protocol_type_TCP')] == 1.0


def test_score_samples_uses_predict_path_for_runtime_compatibility():
    bundle = ModelBundle(
        scaler=IdentityScaler(),
        model=PredictOnlyModel(),
        feature_names=('packet_size', 'protocol_type_TCP'),
        version='predict-fallback',
        scaler_path='scaler.joblib',
        model_path='model.joblib',
    )

    score, version = score_samples(
        [{'packet_size': 5.0, 'protocol_type_TCP': 1.0}],
        bundle=bundle,
    )

    assert score == 0.12
    assert version == 'predict-fallback'


def test_run_inference_marks_sample_below_threshold_as_non_anomaly():
    bundle = ModelBundle(
        scaler=IdentityScaler(),
        model=PredictOnlyModel(),
        feature_names=('packet_size', 'protocol_type_TCP'),
        version='lab-check',
        scaler_path='scaler.joblib',
        model_path='model.joblib',
    )

    result = run_inference(
        [{'packet_size': 9.0, 'protocol_type_TCP': 1.0}],
        threshold=0.7,
        bundle=bundle,
    )

    assert result == {
        'anomaly_score': 0.12,
        'is_anomaly': False,
        'model_version': 'lab-check',
    }
