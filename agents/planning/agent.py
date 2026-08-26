from __future__ import annotations

import re

from agents.orchestrator.orchestrator import ActionPlan
from agents.remediation.what_if import WhatIfEngine
from rca.engine import RCA_Result


class PlanningAgent:
    def __init__(self, whatif_engine: WhatIfEngine | None = None):
        self.whatif_engine = whatif_engine
        
    def create_plan(self, rca_result: RCA_Result) -> ActionPlan:
        cause = rca_result.root_cause.lower()
        evidence_text = " ".join([e.description.lower() for e in rca_result.evidence])
        
        self.timeline = []
        self.timeline.append(f"[Thought]: Analyzing root cause: {rca_result.root_cause}")
        self.timeline.append("[Thought]: Generating candidate actions based on RCA.")
        
        # Candidate generation
        candidates = []
        
        if self.whatif_engine:
            registered_tools = list(self.whatif_engine.tool_registry._tools.keys())
            self.timeline.append(f"[Thought]: Available tools: {', '.join(registered_tools)}")
            
            for tool_name in registered_tools:
                if tool_name == "kill_process":
                    match = re.search(r'pid:?\s*(\d+)', evidence_text)
                    if match:
                        pid = int(match.group(1))
                        candidates.append({"tool_name": tool_name, "parameters": {"pid": pid}})
                elif tool_name == "restart_service":
                    for svc in ["postgresql", "api_server", "nginx"]:
                        candidates.append({"tool_name": tool_name, "parameters": {"service_name": svc}})
                else:
                    candidates.append({"tool_name": tool_name, "parameters": {}})
        else:
            candidates.append({"tool_name": "restart_service", "parameters": {"service_name": "api_server"}})
            
        self.timeline.append(f"[Thought]: Candidate actions generated: {len(candidates)} candidates.")
        
        best_action = None
        best_score = -1.0
        
        if self.whatif_engine and candidates:
            self.timeline.append(f"[Thought]: Evaluating risk and predicted state for {len(candidates)} candidates using What-If counterfactuals...")
            
            for candidate in candidates:
                tool_name = candidate["tool_name"]
                params = candidate["parameters"]
                
                outcome = self.whatif_engine.estimate_outcome(tool_name, params)
                self.timeline.append(f"[What-If Analysis]: Evaluated '{tool_name}' with {params} -> {outcome.expected_outcome}")
                self.timeline.append(f"   ↳ Risk: {outcome.risk.value}, Confidence: {outcome.confidence}, Rec: {outcome.recommendation}")
                
                score = outcome.confidence
                
                # Root cause alignment bonus
                if tool_name == "kill_process" and ("miner" in cause or "cpu" in cause):
                    score += 0.5
                if tool_name == "restart_service" and params.get("service_name") == "postgresql" and ("database" in cause or "connection" in cause):
                    score += 0.5
                
                if "RECOMMENDED" in outcome.recommendation:
                    score += 1.0 # High priority
                    
                if score > best_score:
                    best_score = score
                    best_action = candidate
                    
        if best_action:
            self.timeline.append(f"[Decision]: Selected '{best_action['tool_name']}' as the optimal remediation.")
            return ActionPlan(actions=[best_action])
            
        # Fallback if no engine or no good candidates
        self.timeline.append("[Decision]: Defaulting to safe restart of api_server due to lack of confident candidates.")
        return ActionPlan(actions=[{"tool_name": "restart_service", "parameters": {"service_name": "api_server"}}])
