import re
from agents.orchestrator.orchestrator import ActionPlan
from rca.engine import RCA_Result

class PlanningAgent:
    def create_plan(self, rca_result: RCA_Result) -> ActionPlan:
        cause = rca_result.root_cause.lower()
        evidence_text = " ".join([e.description.lower() for e in rca_result.evidence])
        
        # Simulate LLM thought process
        self.timeline = []
        self.timeline.append(f"[Thought]: Analyzing root cause: {rca_result.root_cause}")
        self.timeline.append(f"[Thought]: Generating candidate actions based on RCA.")
        
        candidates = []
        if "cpu" in cause or "process" in cause or "miner" in cause:
            candidates = ["kill_process", "restart_service", "scale_service"]
        elif "connection" in cause or "database" in cause:
            candidates = ["restart_service", "kill_process"]
        else:
            candidates = ["restart_service"]
            
        self.timeline.append(f"[Thought]: Candidate actions generated: {', '.join(candidates)}")
        
        # Simulate What-If Evaluation
        self.timeline.append(f"[Thought]: Evaluating risk for candidate actions...")
        if "kill_process" in candidates and ("cpu" in cause or "process" in cause):
            # Extract PID from evidence
            pid = 9999
            match = re.search(r'pid:?\s*(\d+)', evidence_text)
            if match:
                pid = int(match.group(1))
            self.timeline.append(f"[Observation]: Evidence points to PID {pid}.")
            self.timeline.append(f"[What-If Analysis]: 'kill_process' on PID {pid} is expected to drop CPU substantially.")
            self.timeline.append(f"[Decision]: Selected 'kill_process' with High confidence.")
            action = {"tool_name": "kill_process", "parameters": {"pid": pid}}
        elif "restart_service" in candidates and ("connection" in cause or "database" in cause):
            self.timeline.append(f"[What-If Analysis]: 'restart_service' on postgresql will clear connection pool.")
            self.timeline.append(f"[Decision]: Selected 'restart_service' for postgresql.")
            action = {"tool_name": "restart_service", "parameters": {"service_name": "postgresql"}}
        else:
            self.timeline.append(f"[Decision]: Defaulting to safe restart of api_server.")
            action = {"tool_name": "restart_service", "parameters": {"service_name": "api_server"}}
            
        return ActionPlan(actions=[action])
