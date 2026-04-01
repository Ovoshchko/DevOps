from __future__ import annotations

import pytest

from app.model.anomaly_model import FEATURE_NAMES
from app.model.anomaly_model import FeaturePreparationError
from app.model.anomaly_model import prepare_feature_matrix


def test_prepare_feature_matrix_uses_canonical_feature_order():
    sample = {
        "packet_size": 10.0,
        "inter_arrival_time": 11.0,
        "src_port": 12.0,
        "dst_port": 13.0,
        "packet_count_5s": 14.0,
        "mean_packet_size": 15.0,
        "spectral_entropy": 16.0,
        "frequency_band_energy": 17.0,
        "protocol_type_TCP": 1.0,
        "protocol_type_UDP": 0.0,
        "src_ip_192.168.1.2": 1.0,
        "src_ip_192.168.1.3": 0.0,
        "dst_ip_192.168.1.5": 1.0,
        "dst_ip_192.168.1.6": 0.0,
        "tcp_flags_FIN": 0.0,
        "tcp_flags_SYN": 1.0,
        "tcp_flags_SYN-ACK": 0.0,
    }

    matrix = prepare_feature_matrix([sample])

    assert tuple(FEATURE_NAMES) == FEATURE_NAMES
    assert matrix.shape == (1, len(FEATURE_NAMES))
    assert matrix.tolist()[0] == [sample[name] for name in FEATURE_NAMES]


def test_prepare_feature_matrix_accepts_full_backend_compatible_feature_payload():
    samples = [
        {feature: float(index) for index, feature in enumerate(FEATURE_NAMES, start=1)},
        {feature: float(index * 2) for index, feature in enumerate(FEATURE_NAMES, start=1)},
    ]

    matrix = prepare_feature_matrix(samples)

    assert matrix.shape == (2, len(FEATURE_NAMES))
    assert matrix.tolist()[0] == [samples[0][name] for name in FEATURE_NAMES]
    assert matrix.tolist()[1] == [samples[1][name] for name in FEATURE_NAMES]


def test_prepare_feature_matrix_derives_missing_feature_values():
    incomplete_sample = {"bytes_per_sec": 100.0, "packets_per_sec": 10.0}

    matrix = prepare_feature_matrix([incomplete_sample])

    assert matrix.shape == (1, len(FEATURE_NAMES))
    assert matrix.tolist()[0][0] == 10.0


def test_prepare_feature_matrix_backfills_defaults_for_legacy_payloads():
    legacy_sample = {"bytes_per_sec": 120.0}

    matrix = prepare_feature_matrix([legacy_sample])

    row = matrix.tolist()[0]
    assert row[FEATURE_NAMES.index("packet_size")] == 120.0
    assert row[FEATURE_NAMES.index("mean_packet_size")] == 120.0
    assert row[FEATURE_NAMES.index("packet_count_5s")] == 0.0
    assert row[FEATURE_NAMES.index("protocol_type_TCP")] == 0.0


def test_prepare_feature_matrix_rejects_non_numeric_values():
    bad_sample = {feature: 1.0 for feature in FEATURE_NAMES}
    bad_sample["packet_size"] = "bad-value"

    with pytest.raises(FeaturePreparationError, match="must be numeric"):
        prepare_feature_matrix([bad_sample])
