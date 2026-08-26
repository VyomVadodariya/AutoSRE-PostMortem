from __future__ import annotations

import math

from pydantic import BaseModel

from environment.observability.metrics import TimeSeriesMetric


class AnomalyEvent(BaseModel):
    metric: str
    baseline: float
    current_value: float
    deviation: float
    confidence: float
    timestamp: float

class AnomalyDetector:
    def __init__(self, z_score_threshold: float = 3.0, ewma_alpha: float = 0.2):
        self.z_score_threshold = z_score_threshold
        self.ewma_alpha = ewma_alpha
        self.ewma_state: dict[str, float] = {}

    def detect(self, metric: TimeSeriesMetric) -> AnomalyEvent | None:
        points = metric.points
        if len(points) < 5:
            # Not enough data to establish a baseline
            return None

        # Calculate basic stats on all points except the latest one to form the "baseline"
        history = [p.value for p in points[:-1]]
        latest = points[-1]
        
        baseline_mean = sum(history) / len(history)
        variance = sum((x - baseline_mean) ** 2 for x in history) / len(history)
        std_dev = math.sqrt(variance) if variance > 0 else 0.001 # prevent div by zero

        # 1. Z-Score Detection
        z_score = abs(latest.value - baseline_mean) / std_dev
        
        # 2. EWMA Calculation
        if metric.name not in self.ewma_state:
            self.ewma_state[metric.name] = baseline_mean
        
        prev_ewma = self.ewma_state[metric.name]
        current_ewma = (self.ewma_alpha * latest.value) + ((1 - self.ewma_alpha) * prev_ewma)
        self.ewma_state[metric.name] = current_ewma
        
        abs(latest.value - current_ewma)

        # Decide if anomalous (using Z-score primarily)
        if z_score > self.z_score_threshold:
            # Confidence approaches 99% as z_score increases
            confidence = min(0.99, 0.5 + (z_score / (self.z_score_threshold * 2)))
            
            return AnomalyEvent(
                metric=metric.name,
                baseline=round(baseline_mean, 2),
                current_value=round(latest.value, 2),
                deviation=round(z_score, 2),
                confidence=round(confidence, 2),
                timestamp=latest.timestamp
            )

        # Simple static threshold fallbacks based on metric names
        # e.g., CPU > 90% is anomalous even if historically high, but Z-score is better
        if "cpu" in metric.name.lower() and latest.value > 90.0:
             return AnomalyEvent(
                metric=metric.name,
                baseline=round(baseline_mean, 2),
                current_value=round(latest.value, 2),
                deviation=round(latest.value - baseline_mean, 2),
                confidence=0.85,
                timestamp=latest.timestamp
            )
            
        return None
