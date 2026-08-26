
from adapters.kubernetes import KubernetesAdapter
from environment.observability.metrics import MetricsStore
from policies.risk.levels import RiskLevel
from policies.safety_pipeline import SafetyPipeline
from tools.base import BaseTool


class DummyTool(BaseTool):
    def __init__(self, name, risk):
        self.name = name
        self.risk_level = risk

def test_kubernetes_adapter_dry_run():
    metrics = MetricsStore()
    pipeline = SafetyPipeline(metrics)
    adapter = KubernetesAdapter(pipeline)
    
    # Must be in dry_run by default
    assert adapter.is_dry_run
    
    tool = DummyTool("restart_pod", RiskLevel.LOW)
    result = adapter.execute_action(tool, {"service_name": "local_service"})
    
    assert result["success"]
    assert result["dry_run"]
    assert "message" in result

def test_kubernetes_adapter_safety_block():
    metrics = MetricsStore()
    pipeline = SafetyPipeline(metrics)
    adapter = KubernetesAdapter(pipeline)
    
    high_risk_tool = DummyTool("drop_namespace", RiskLevel.HIGH)
    result = adapter.execute_action(high_risk_tool, {"service_name": "database"})
    
    # Should be blocked by safety policy before execution
    assert not result["success"]
    assert "Blocked by policy" in result["reason"]
