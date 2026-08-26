from policies.risk.levels import RiskLevel
from tools.base import BaseTool, ToolResult


class GetMetricsTool(BaseTool):
    name = "get_metrics"
    description = "Retrieves the latest metrics for a given service or resource."
    parameters = {"metric_name": "str"}
    risk_level = RiskLevel.LOW

    def validate(self, **kwargs) -> bool:
        return "metric_name" in kwargs

    def execute(self, **kwargs) -> ToolResult:
        metric_name = kwargs["metric_name"]
        metrics_store = kwargs.get("_metrics_store")
        
        value = 0.0
        if metrics_store:
            latest = metrics_store.get_all_latest()
            value = latest.get(metric_name, 0.0)
            
        return ToolResult(
            success=True, 
            output=f"Retrieved metrics for {metric_name}",
            data={"value": value}
        )

class RestartServiceTool(BaseTool):
    name = "restart_service"
    description = "Restarts a specific system service."
    parameters = {"service_name": "str"}
    risk_level = RiskLevel.MEDIUM

    def __init__(self, env=None):
        self.env = env
        super().__init__()

    def validate(self, **kwargs) -> bool:
        return "service_name" in kwargs and isinstance(kwargs["service_name"], str)

    def execute(self, **kwargs) -> ToolResult:
        service_name = kwargs["service_name"]
        
        if self.env:
            self.env.reset_service(service_name)
            return ToolResult(
                success=True,
                output=f"Successfully restarted service: {service_name}"
            )
            
        return ToolResult(
            success=False,
            output="Simulation environment not attached."
        )

class TerminateProcessTool(BaseTool):
    name = "kill_process"
    description = "Forcefully terminates a process by its PID."
    parameters = {"pid": "int"}
    risk_level = RiskLevel.HIGH

    def __init__(self, env=None):
        self.env = env
        super().__init__()

    def validate(self, **kwargs) -> bool:
        return "pid" in kwargs

    def execute(self, **kwargs) -> ToolResult:
        pid = kwargs["pid"]
        
        if self.env:
            success = self.env.remove_process(pid)
            if success:
                return ToolResult(
                    success=True,
                    output=f"Process {pid} terminated successfully."
                )
            else:
                return ToolResult(
                    success=False,
                    output=f"Process {pid} not found."
                )
                
        return ToolResult(
            success=False,
            output="Simulation environment not attached."
        )
