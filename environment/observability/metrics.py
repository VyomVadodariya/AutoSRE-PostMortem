from __future__ import annotations

import time

from pydantic import BaseModel, Field


class MetricPoint(BaseModel):
    timestamp: float
    value: float

class TimeSeriesMetric(BaseModel):
    name: str
    points: list[MetricPoint] = Field(default_factory=list)

    def add_point(self, value: float, timestamp: float | None = None):
        ts = timestamp if timestamp else time.time()
        self.points.append(MetricPoint(timestamp=ts, value=value))
        # Keep only the last 100 points to save memory in simulation
        if len(self.points) > 100:
            self.points.pop(0)

    def get_recent_values(self, limit: int = 10) -> list[float]:
        return [p.value for p in self.points[-limit:]]
        
    def get_recent_points(self, limit: int = 10) -> list[MetricPoint]:
        return self.points[-limit:]

class MetricsStore:
    def __init__(self):
        self.metrics: dict[str, TimeSeriesMetric] = {}

    def get_metric(self, name: str) -> TimeSeriesMetric:
        if name not in self.metrics:
            self.metrics[name] = TimeSeriesMetric(name=name)
        return self.metrics[name]

    def record(self, name: str, value: float, timestamp: float | None = None):
        metric = self.get_metric(name)
        metric.add_point(value, timestamp)

    def get_all_latest(self) -> dict[str, float]:
        return {
            name: m.points[-1].value if m.points else 0.0
            for name, m in self.metrics.items()
        }
