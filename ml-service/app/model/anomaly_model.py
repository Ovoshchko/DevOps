from __future__ import annotations

def score_samples(samples: list[dict[str, float]]) -> float:
    values = [v for sample in samples for v in sample.values() if isinstance(v, (int, float))]
    if not values:
        return 0.0
    avg = sum(values) / len(values)
    return min(max(avg, 0.0), 1.0)
