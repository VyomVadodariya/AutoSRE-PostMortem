import time

from environment.observability.signals import LogEntry, SignalStore
from rca.correlation.evidence import CorrelationEngine


def test_signal_store():
    store = SignalStore()
    
    store.add_log(LogEntry(
        timestamp=time.time(),
        service="nginx",
        level="ERROR",
        message="Connection refused"
    ))
    
    assert len(store.logs) == 1
    assert store.logs[0].service == "nginx"

def test_correlation_engine():
    engine = CorrelationEngine()
    
    dep_time = time.time() - 100 # 100 seconds ago
    metric_time = time.time()
    
    finding = engine.correlate_deployment_and_metric(
        deployment_time=dep_time,
        metric_time=metric_time,
        deployment_desc="Deployed v2.4.1",
        metric_desc="CPU spiked to 99%"
    )
    
    assert finding is not None
    assert finding.confidence == 0.9  # 0.4 + 0.5
    assert len(finding.evidence_list) == 2
    
def test_correlation_engine_no_correlation():
    engine = CorrelationEngine()
    
    dep_time = time.time() - 400 # 400 seconds ago (>300s window)
    metric_time = time.time()
    
    finding = engine.correlate_deployment_and_metric(
        deployment_time=dep_time,
        metric_time=metric_time,
        deployment_desc="Deployed v2.4.1",
        metric_desc="CPU spiked to 99%"
    )
    
    assert finding is None
