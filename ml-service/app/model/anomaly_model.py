from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
import warnings

import joblib
import numpy as np

ArtifactLoader = Callable[[str], Any]

FEATURE_NAMES: tuple[str, ...] = (
    "packet_size",
    "inter_arrival_time",
    "src_port",
    "dst_port",
    "packet_count_5s",
    "mean_packet_size",
    "spectral_entropy",
    "frequency_band_energy",
    "protocol_type_TCP",
    "protocol_type_UDP",
    "src_ip_192.168.1.2",
    "src_ip_192.168.1.3",
    "dst_ip_192.168.1.5",
    "dst_ip_192.168.1.6",
    "tcp_flags_FIN",
    "tcp_flags_SYN",
    "tcp_flags_SYN-ACK",
)

FEATURE_DEFAULTS: dict[str, float] = {
    "packet_size": 0.0,
    "inter_arrival_time": 0.0,
    "src_port": 0.0,
    "dst_port": 0.0,
    "packet_count_5s": 0.0,
    "mean_packet_size": 0.0,
    "spectral_entropy": 0.0,
    "frequency_band_energy": 0.0,
    "protocol_type_TCP": 0.0,
    "protocol_type_UDP": 0.0,
    "src_ip_192.168.1.2": 0.0,
    "src_ip_192.168.1.3": 0.0,
    "dst_ip_192.168.1.5": 0.0,
    "dst_ip_192.168.1.6": 0.0,
    "tcp_flags_FIN": 0.0,
    "tcp_flags_SYN": 0.0,
    "tcp_flags_SYN-ACK": 0.0,
}

_MODEL_BUNDLE_CACHE: dict[str, "ModelBundle"] = {}


class FeaturePreparationError(ValueError):
    """Raised when incoming samples cannot be converted into model features."""


class ModelLoadError(RuntimeError):
    """Raised when packaged model artifacts cannot be loaded."""


@dataclass(frozen=True)
class ModelBundle:
    scaler: Any
    model: Any
    feature_names: tuple[str, ...]
    version: str
    scaler_path: str
    model_path: str


def _coerce_numeric(value: Any, feature_name: str, sample_index: int) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    raise FeaturePreparationError(
        f"Feature '{feature_name}' in sample {sample_index} must be numeric."
    )


def _sample_metric(sample: dict[str, float], name: str) -> float | None:
    value = sample.get(name)
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _derive_feature_value(sample: dict[str, float], feature_name: str) -> float:
    direct = _sample_metric(sample, feature_name)
    if direct is not None:
        return direct

    bytes_per_sec = _sample_metric(sample, "bytes_per_sec")
    packets_per_sec = _sample_metric(sample, "packets_per_sec")

    if feature_name in {"packet_size", "mean_packet_size"}:
        if bytes_per_sec is not None and packets_per_sec not in (None, 0.0):
            return bytes_per_sec / packets_per_sec
        if bytes_per_sec is not None:
            return bytes_per_sec
    if feature_name == "packet_count_5s" and packets_per_sec is not None:
        return packets_per_sec * 5.0
    if feature_name == "inter_arrival_time" and packets_per_sec not in (None, 0.0):
        return 1.0 / packets_per_sec

    return FEATURE_DEFAULTS[feature_name]


def prepare_feature_matrix(
    samples: list[dict[str, float]],
    feature_names: tuple[str, ...] = FEATURE_NAMES,
) -> np.ndarray:
    rows: list[list[float]] = []
    for sample_index, sample in enumerate(samples):
        row: list[float] = []
        for feature_name in feature_names:
            if feature_name in sample:
                row.append(_coerce_numeric(sample[feature_name], feature_name, sample_index))
                continue
            try:
                row.append(_derive_feature_value(sample, feature_name))
            except KeyError as exc:
                raise FeaturePreparationError(
                    f"Missing required feature '{feature_name}' in sample {sample_index}."
                ) from exc
        rows.append(row)
    return np.asarray(rows, dtype=float)


def load_model_bundle(
    model_dir: str | Path,
    *,
    loader: ArtifactLoader | None = None,
    use_cache: bool = True,
    version: str | None = None,
) -> ModelBundle:
    resolved_model_dir = Path(model_dir).resolve()
    cache_key = str(resolved_model_dir)
    if use_cache and loader is None and cache_key in _MODEL_BUNDLE_CACHE:
        return _MODEL_BUNDLE_CACHE[cache_key]

    active_loader = loader or joblib.load
    scaler_path = resolved_model_dir / "scaler.joblib"
    model_path = resolved_model_dir / "model.joblib"
    bundle_version = version or resolved_model_dir.name

    try:
        scaler = active_loader(str(scaler_path))
        model = active_loader(str(model_path))
    except Exception as exc:
        raise ModelLoadError(
            f"Unable to load model artifacts from '{resolved_model_dir}'."
        ) from exc

    bundle = ModelBundle(
        scaler=scaler,
        model=model,
        feature_names=FEATURE_NAMES,
        version=bundle_version,
        scaler_path=str(scaler_path),
        model_path=str(model_path),
    )
    if use_cache and loader is None:
        _MODEL_BUNDLE_CACHE[cache_key] = bundle
    return bundle


def score_samples(
    samples: list[dict[str, float]],
    *,
    bundle: ModelBundle | None = None,
    bundle_loader: Callable[..., ModelBundle] | None = None,
    model_dir: str | Path | None = None,
    version: str | None = None,
) -> tuple[float, str]:
    if bundle is None:
        if model_dir is None:
            raise ModelLoadError("Model directory is required when bundle is not provided.")
        active_loader = bundle_loader or load_model_bundle
        bundle = active_loader(model_dir, version=version)

    matrix = prepare_feature_matrix(samples, feature_names=bundle.feature_names)
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="X does not have valid feature names, but StandardScaler was fitted with feature names",
            category=UserWarning,
        )
        transformed = bundle.scaler.transform(matrix)

    if hasattr(bundle.model, "predict_proba"):
        probabilities = bundle.model.predict_proba(transformed)
        score = float(np.max(probabilities[:, -1]))
    else:
        predictions = bundle.model.predict(transformed)
        score = float(np.max(predictions))

    return min(max(score, 0.0), 1.0), bundle.version
