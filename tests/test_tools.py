from tools.registry import ToolRegistry
from tools.implementations import GetMetricsTool, RestartServiceTool, TerminateProcessTool
from policies.risk.levels import RiskLevel

def test_tool_registry():
    registry = ToolRegistry()
    
    registry.register(GetMetricsTool())
    registry.register(RestartServiceTool())
    
    # Get Tool
    tool = registry.get_tool("get_metrics")
    assert tool is not None
    assert tool.risk_level == RiskLevel.LOW
    
    # Execute Tool
    result = registry.execute_tool("restart_service", service_name="nginx")
    assert result.success is True
    assert "nginx" in result.output
    
    # Execute Missing Tool
    result = registry.execute_tool("unknown_tool")
    assert result.success is False

def test_tool_validation():
    registry = ToolRegistry()
    registry.register(TerminateProcessTool())
    
    # Missing required 'pid' parameter
    result = registry.execute_tool("terminate_process")
    assert result.success is False
    assert "Validation failed" in result.output
    
    # Valid parameters
    result = registry.execute_tool("terminate_process", pid=101)
    assert result.success is True
