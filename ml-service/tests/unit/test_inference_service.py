from app.inference.service import run_inference


def test_inference_returns_score_and_flag():
    out = run_inference([{"bytes_per_sec": 0.9}, {"bytes_per_sec": 0.8}])
    assert 'anomaly_score' in out
    assert 'is_anomaly' in out
    assert out['model_version'] == 'simple-v1'
