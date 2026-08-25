from environment.observability.sre_metrics import SREMetricsTracker
from environment.observability.business_impact import BusinessImpactCalculator

def test_sre_metrics():
    tracker = SREMetricsTracker(slo_target=99.95)
    
    # Record a new incident taking 10 minutes (600 seconds)
    tracker.record_incident_metrics(mttd=60, mtta=10, mttr=600, downtime_minutes=10)
    
    status = tracker.calculate_status()
    
    assert status.slo_target == 99.95
    # Allowed downtime = 0.05% of (43200 + 22) = ~21.6 minutes
    # We used 12 + 10 = 22 minutes
    # So error budget is > 100%
    assert status.status == "VIOLATED"
    assert status.error_budget_consumed_percent > 100.0

def test_business_impact():
    calculator = BusinessImpactCalculator(request_rate_per_sec=100, revenue_per_request=0.05)
    
    # Incident duration 6m 14s = 374 seconds
    impact = calculator.calculate_impact(duration_seconds=374.0, failure_rate_percent=100.0)
    
    # 100 * 0.05 = $5 per second.
    # $5 * 60 = $300 per minute
    # Total = 5 * 374 = $1870
    assert impact.impact_per_minute == 300.0
    assert impact.total_impact == 1870.0
    assert "$300/min" in impact.formatted_estimate
    assert "$1,870" in impact.formatted_estimate
