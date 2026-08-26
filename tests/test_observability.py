from environment.observability.anomaly_detector import AnomalyDetector, AnomalyEvent
from environment.observability.metrics import MetricsStore, TimeSeriesMetric


def test_metrics_store():
    store = MetricsStore()
    
    # Record some metrics
    store.record("cpu_usage", 45.0)
    store.record("cpu_usage", 46.5)
    store.record("memory_usage", 60.0)
    
    metric = store.get_metric("cpu_usage")
    assert len(metric.points) == 2
    assert metric.points[-1].value == 46.5
    
    latest = store.get_all_latest()
    assert latest["cpu_usage"] == 46.5
    assert latest["memory_usage"] == 60.0

def test_anomaly_detector_zscore():
    detector = AnomalyDetector(z_score_threshold=2.0)
    metric = TimeSeriesMetric(name="request_rate")
    
    # Add normal baseline data
    for val in [100.0, 102.0, 98.0, 101.0, 99.0, 100.5]:
        metric.add_point(val)
        
    # No anomaly yet
    assert detector.detect(metric) is None
    
    # Add anomalous spike
    metric.add_point(300.0) # Massive spike
    
    event = detector.detect(metric)
    assert event is not None
    assert isinstance(event, AnomalyEvent)
    assert event.metric == "request_rate"
    assert event.current_value == 300.0
    assert event.deviation > 2.0

def test_anomaly_detector_not_enough_data():
    detector = AnomalyDetector()
    metric = TimeSeriesMetric(name="cpu_usage")
    
    metric.add_point(99.0)
    # Not enough data points to detect properly (requires >= 5)
    assert detector.detect(metric) is None
