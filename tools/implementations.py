from typing import Dict, Any
from tools.base import BaseTool, ToolResult
from policies.risk.levels import RiskLevel

class GetMetricsTool(BaseTool):
    name = "get_metrics"
    description = "Retrieves the latest metrics for a given service or resource."
    parameters = {"metric_name": "str"}
    risk_level = RiskLevel.LOW

    def validate(self, **kwargs) -> bool:
        return "metric_name" in kwargs

    def execute(self, **kwargs) -> ToolResult:
        metric_name = kwargs["metric_name"]
        # In the future, this calls the MetricsStore
        return ToolResult(
            success=True, 
            output=f"Retrieved metrics for {metric_name}",
            data={"value": 42.0} # Placeholder
        )

class RestartServiceTool(BaseTool):
    name = "restart_service"
    description = "Restarts a specific system service."
    parameters = {"service_name": "str"}
    risk_level = RiskLevel.MEDIUM

    def validate(self, **kwargs) -> bool:
        return "service_name" in kwargs and isinstance(kwargs["service_name"], str)

    def execute(self, **kwargs) -> ToolResult:
        service_name = kwargs["service_name"]
        # Simulated restart logic
        return ToolResult(
            success=True,
            output=f"Successfully restarted service: {service_name}"
        )

class TerminateProcessTool(BaseTool):
    name = "terminate_process"
    description = "Forcefully terminates a process by its PID."
    parameters = {"pid": "int"}
    risk_level = RiskLevel.HIGH

    def validate(self, **kwargs) -> bool:
        return "pid" in kwargs

    def execute(self, **kwargs) -> ToolResult:
        pid = kwargs["pid"]
        # Simulated kill
        return ToolResult(
            success=True,
            output=f"Process {pid} terminated."
        )
