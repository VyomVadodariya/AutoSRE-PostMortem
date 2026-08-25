from tools.registry import ToolRegistry
from tools.implementations import GetMetricsTool, TerminateProcessTool
from environment.observability.metrics import MetricsStore
from agents.remediation.engine import RemediationEngine
from agents.remediation.what_if import WhatIfEngine
from policies.risk.levels import RiskLevel

def test_remediation_engine():
    registry = ToolRegistry()
    registry.register(TerminateProcessTool())
    
    metrics = MetricsStore()
    metrics.record("cpu_usage", 99.0)
    
    engine = RemediationEngine(registry, metrics)
    
    # Execute successful remediation
    result = engine.execute_and_verify("kill_process", parameters={"pid": 1234})
    
    assert result.action == "kill_process"
    assert result.verification_status == "SUCCESS"
    assert "cpu_usage" in result.before_state
    
    # Execute failing remediation
    result_fail = engine.execute_and_verify("kill_process", parameters={})
    assert result_fail.verification_status == "FAILED"

def test_what_if_engine():
    registry = ToolRegistry()
    registry.register(TerminateProcessTool())
    registry.register(GetMetricsTool())
    
    what_if = WhatIfEngine(registry)
    
    # High risk action
    outcome1 = what_if.estimate_outcome("kill_process", {"pid": 1234})
    assert outcome1.risk == RiskLevel.HIGH
    assert "Require human approval" in outcome1.recommendation
    
    # Low risk action
    outcome2 = what_if.estimate_outcome("get_metrics", {"metric_name": "cpu"})
    assert outcome2.risk == RiskLevel.LOW
    assert "Safe to execute" in outcome2.recommendation
    
    # Invalid action
    outcome3 = what_if.estimate_outcome("unknown", {})
    assert outcome3.risk == RiskLevel.HIGH
    assert outcome3.confidence == 0.0
