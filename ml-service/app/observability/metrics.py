from __future__ import annotations

from fastapi.responses import Response

try:
    from prometheus_client import CONTENT_TYPE_LATEST
    from prometheus_client import CollectorRegistry
    from prometheus_client import Counter
    from prometheus_client import Gauge
    from prometheus_client import Histogram
    from prometheus_client import generate_latest
except ModuleNotFoundError:  # pragma: no cover - compatibility for bare local envs
    CONTENT_TYPE_LATEST = 'text/plain; version=0.0.4; charset=utf-8'

    class _MetricHandle:
        def __init__(self, metric: '_MetricBase', key: tuple[str, ...]) -> None:
            self.metric = metric
            self.key = key

        def inc(self, amount: float = 1.0) -> None:
            self.metric.values[self.key] = self.metric.values.get(self.key, 0.0) + amount

        def dec(self, amount: float = 1.0) -> None:
            self.metric.values[self.key] = self.metric.values.get(self.key, 0.0) - amount

        def observe(self, amount: float) -> None:
            self.metric.values[self.key] = self.metric.values.get(self.key, 0.0) + amount

    class _MetricBase:
        metric_type = 'gauge'

        def __init__(
            self,
            name: str,
            documentation: str,
            labelnames: tuple[str, ...] | tuple = (),
            registry: 'CollectorRegistry | None' = None,
            **_: object,
        ) -> None:
            self.name = name
            self.documentation = documentation
            self.labelnames = tuple(labelnames)
            self.values: dict[tuple[str, ...], float] = {}
            if registry is not None:
                registry.register(self)

        def labels(self, **kwargs: str) -> _MetricHandle:
            key = tuple(str(kwargs.get(label, '')) for label in self.labelnames)
            return _MetricHandle(self, key)

        def render(self) -> str:
            lines = [
                f'# HELP {self.name} {self.documentation}',
                f'# TYPE {self.name} {self.metric_type}',
            ]
            if not self.values:
                lines.append(f'{self.name} 0.0')
                return '\n'.join(lines)
            for key, value in self.values.items():
                if self.labelnames:
                    labels = ','.join(
                        f'{label}="{label_value}"'
                        for label, label_value in zip(self.labelnames, key)
                    )
                    lines.append(f'{self.name}{{{labels}}} {value}')
                else:
                    lines.append(f'{self.name} {value}')
            return '\n'.join(lines)

    class Counter(_MetricBase):
        metric_type = 'counter'

    class Gauge(_MetricBase):
        metric_type = 'gauge'

    class Histogram(_MetricBase):
        metric_type = 'histogram'

    class CollectorRegistry:
        def __init__(self) -> None:
            self.metrics: list[_MetricBase] = []

        def register(self, metric: _MetricBase) -> None:
            self.metrics.append(metric)

    def generate_latest(registry: CollectorRegistry) -> bytes:
        return '\n'.join(metric.render() for metric in registry.metrics).encode('utf-8')


REGISTRY = CollectorRegistry()

REQUEST_COUNTER = Counter(
    'ml_service_http_requests_total',
    'Total HTTP requests served by the ML service.',
    labelnames=('method', 'path', 'status_code'),
    registry=REGISTRY,
)
REQUEST_LATENCY = Histogram(
    'ml_service_http_request_duration_seconds',
    'HTTP request duration for ML service routes.',
    labelnames=('method', 'path'),
    registry=REGISTRY,
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)
IN_PROGRESS = Gauge(
    'ml_service_http_requests_in_progress',
    'Number of ML service requests currently being processed.',
    labelnames=('method', 'path'),
    registry=REGISTRY,
)
EXCEPTION_COUNTER = Counter(
    'ml_service_http_request_exceptions_total',
    'Total uncaught ML service request exceptions.',
    labelnames=('method', 'path', 'exception_type'),
    registry=REGISTRY,
)


def observe_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    REQUEST_COUNTER.labels(method=method, path=path, status_code=str(status_code)).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(duration_seconds)


def metrics_response() -> Response:
    payload = generate_latest(REGISTRY)
    return Response(content=payload, media_type=CONTENT_TYPE_LATEST)
