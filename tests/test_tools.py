from tools.registry import ToolRegistry
from tools.implementations import GetMetricsTool, RestartServiceTool, TerminateProcessTool
from policies.risk.levels import RiskLevel

def test_tool_registration():
    registry = ToolRegistry()
    registry.register(GetMetricsTool())
    registry.register(RestartServiceTool())
    
    tool = registry.get_tool("get_metrics")
    assert tool is not None
    assert tool.risk_level == RiskLevel.LOW
    
    tool_missing = registry.get_tool("nonexistent")
    assert tool_missing is None

def test_tool_validation():
    registry = ToolRegistry()
    registry.register(TerminateProcessTool())
    
    # Missing required 'pid' parameter
    result = registry.execute_tool("kill_process")
    assert result.success is False
    assert "Validation failed" in result.output
    
    # Valid parameters
    result2 = registry.execute_tool("kill_process", pid=1234)
    assert result2.success is True
