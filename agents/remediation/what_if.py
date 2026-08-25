from pydantic import BaseModel
from typing import Dict, Any
from tools.registry import ToolRegistry
from policies.risk.levels import RiskLevel

class WhatIfOutcome(BaseModel):
    proposed_action: str
    expected_outcome: str
    risk: RiskLevel
    confidence: float
    recommendation: str

class WhatIfEngine:
    def __init__(self, tool_registry: ToolRegistry):
        self.tool_registry = tool_registry

    def estimate_outcome(self, tool_name: str, parameters: Dict[str, Any], context: str = "") -> WhatIfOutcome:
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return WhatIfOutcome(
                proposed_action=tool_name,
                expected_outcome="Unknown action and unknown outcome.",
                risk=RiskLevel.HIGH,
                confidence=0.0,
                recommendation="Do not execute. Tool does not exist."
            )
            
        # Simulated heuristic logic (this would be powered by LLM or Simulation rules)
        expected_outcome = f"System state will be mutated by {tool_name}."
        recommendation = "Proceed with caution."
        
        if tool.risk_level == RiskLevel.LOW:
            recommendation = "Safe to execute automatically."
            expected_outcome = "No service disruption expected."
        elif tool.risk_level == RiskLevel.HIGH:
            recommendation = "High risk. Require human approval."
            expected_outcome = "Potential service disruption or data loss during execution."
            
        return WhatIfOutcome(
            proposed_action=tool_name,
            expected_outcome=expected_outcome,
            risk=tool.risk_level,
            confidence=0.85,
            recommendation=recommendation
        )
