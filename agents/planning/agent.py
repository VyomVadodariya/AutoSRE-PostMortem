from agents.orchestrator.orchestrator import ActionPlan
from rca.engine import RCA_Result

class PlanningAgent:
    def create_plan(self, rca_result: RCA_Result) -> ActionPlan:
        # Simple heuristic: If it's a known cause with a clear available remediation, pick the first one
        # This will be replaced by an LLM-based planner
        action = {"tool_name": "restart_service", "parameters": {"service_name": "nginx"}}
        
        # In testing we can mock this out, but let's provide a safe default
        return ActionPlan(actions=[action])
