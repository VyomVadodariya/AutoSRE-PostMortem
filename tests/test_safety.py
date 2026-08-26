from environment.observability.metrics import MetricsStore
from policies.risk.levels import RiskLevel
from policies.safety_pipeline import SafetyPipeline
from tools.base import BaseTool


class DummyTool(BaseTool):
    def __init__(self, name, risk):
        self.name = name
        self.risk_level = risk

def test_safety_bypass_attempt():
    metrics = MetricsStore()
    pipeline = SafetyPipeline(metrics)
    
    high_risk_tool = DummyTool("drop_database", RiskLevel.HIGH)
    params = {"service_name": "database"}
    
    # Attempt to bypass safety on high-risk global blast radius
    decision = pipeline.evaluate_request(high_risk_tool, params)
    
    assert not decision.approved
    assert "override" in decision.reason.lower()

def test_budget_exhaustion():
    metrics = MetricsStore()
    pipeline = SafetyPipeline(metrics)
    pipeline.error_budget = 4.0 # Less than MEDIUM risk cost
    
    med_risk_tool = DummyTool("restart_service", RiskLevel.MEDIUM)
    decision = pipeline.evaluate_request(med_risk_tool, {"service_name": "api"})
    
    assert not decision.approved
    assert "exhausted" in decision.reason.lower()

def test_low_risk_approval():
    metrics = MetricsStore()
    pipeline = SafetyPipeline(metrics)
    
    low_risk = DummyTool("get_metrics", RiskLevel.LOW)
    decision = pipeline.evaluate_request(low_risk, {"service_name": "api"})
    
    assert decision.approved
    assert decision.blast_radius == "REGIONAL"
