from agents.orchestrator.orchestrator import ActionPlan
from rca.engine import RCA_Result

class PlanningAgent:
    def create_plan(self, rca_result: RCA_Result) -> ActionPlan:
        cause = rca_result.root_cause.lower()
        
        if "cpu" in cause:
            # Direct mapping for simulated environments
            action = {"tool_name": "kill_process", "parameters": {"pid": 1001}}
        elif "connection" in cause or "database" in cause:
            action = {"tool_name": "restart_service", "parameters": {"service_name": "postgresql"}}
        elif "latency" in cause or "network" in cause:
            action = {"tool_name": "restart_service", "parameters": {"service_name": "nginx"}}
        else:
            action = {"tool_name": "restart_service", "parameters": {"service_name": "api_server"}}
            
        return ActionPlan(actions=[action])
