import re
from typing import Optional
from agents.orchestrator.orchestrator import ActionPlan
from rca.engine import RCA_Result
from agents.remediation.what_if import WhatIfEngine

class PlanningAgent:
    def __init__(self, whatif_engine: Optional[WhatIfEngine] = None):
        self.whatif_engine = whatif_engine
        
    def create_plan(self, rca_result: RCA_Result) -> ActionPlan:
        cause = rca_result.root_cause.lower()
        evidence_text = " ".join([e.description.lower() for e in rca_result.evidence])
        
        self.timeline = []
        self.timeline.append(f"[Thought]: Analyzing root cause: {rca_result.root_cause}")
        self.timeline.append(f"[Thought]: Generating candidate actions based on RCA.")
        
        # Candidate generation
        candidates = []
        if "cpu" in cause or "process" in cause or "miner" in cause:
            candidates.append({"tool_name": "kill_process", "needs_pid": True})
            candidates.append({"tool_name": "restart_service", "service_name": "api_server"})
        elif "connection" in cause or "database" in cause:
            candidates.append({"tool_name": "restart_service", "service_name": "postgresql"})
            candidates.append({"tool_name": "restart_service", "service_name": "api_server"})
        else:
            candidates.append({"tool_name": "restart_service", "service_name": "api_server"})
            
        self.timeline.append(f"[Thought]: Candidate actions generated: {', '.join([c['tool_name'] for c in candidates])}")
        
        best_action = None
        best_score = -1.0
        
        if self.whatif_engine:
            self.timeline.append(f"[Thought]: Evaluating risk and predicted state for {len(candidates)} candidates using What-If counterfactuals...")
            
            for candidate in candidates:
                params = {}
                if candidate.get("needs_pid"):
                    match = re.search(r'pid:?\s*(\d+)', evidence_text)
                    if match:
                        params["pid"] = int(match.group(1))
                    else:
                        continue # Can't execute without PID
                if "service_name" in candidate:
                    params["service_name"] = candidate["service_name"]
                    
                outcome = self.whatif_engine.estimate_outcome(candidate["tool_name"], params)
                self.timeline.append(f"[What-If Analysis]: Evaluated '{candidate['tool_name']}' -> {outcome.expected_outcome}")
                self.timeline.append(f"   ↳ Risk: {outcome.risk.value}, Confidence: {outcome.confidence}, Rec: {outcome.recommendation}")
                
                score = outcome.confidence
                if "RECOMMENDED" in outcome.recommendation:
                    score += 1.0 # High priority
                    
                if score > best_score:
                    best_score = score
                    best_action = {"tool_name": candidate["tool_name"], "parameters": params}
                    
        if best_action:
            self.timeline.append(f"[Decision]: Selected '{best_action['tool_name']}' as the optimal remediation.")
            return ActionPlan(actions=[best_action])
            
        # Fallback if no engine or no good candidates
        self.timeline.append(f"[Decision]: Defaulting to safe restart of api_server due to lack of confident candidates.")
        return ActionPlan(actions=[{"tool_name": "restart_service", "parameters": {"service_name": "api_server"}}])
