import re
from agents.orchestrator.orchestrator import ActionPlan
from rca.engine import RCA_Result

class PlanningAgent:
    def create_plan(self, rca_result: RCA_Result) -> ActionPlan:
        cause = rca_result.root_cause.lower()
        evidence_text = " ".join([e.description.lower() for e in rca_result.evidence])
        
        if "cpu" in cause or "process" in cause:
            # Extract PID from evidence
            pid = 9999 # Default safe fallback
            match = re.search(r'pid:\s*(\d+)', evidence_text)
            if match:
                pid = int(match.group(1))
            action = {"tool_name": "kill_process", "parameters": {"pid": pid}}
        elif "connection" in cause or "database" in cause:
            action = {"tool_name": "restart_service", "parameters": {"service_name": "postgresql"}}
        elif "latency" in cause or "network" in cause:
            action = {"tool_name": "restart_service", "parameters": {"service_name": "nginx"}}
        else:
            action = {"tool_name": "restart_service", "parameters": {"service_name": "api_server"}}
            
        return ActionPlan(actions=[action])
