import copy
from pydantic import BaseModel
from typing import Dict, Any, Optional
from tools.registry import ToolRegistry
from policies.risk.levels import RiskLevel
from environment.simulation import SimulationEnvironment

class WhatIfOutcome(BaseModel):
    proposed_action: str
    expected_outcome: str
    risk: RiskLevel
    confidence: float
    recommendation: str
    predicted_metrics: Dict[str, float]

class WhatIfEngine:
    def __init__(self, tool_registry: ToolRegistry, env: Optional[SimulationEnvironment] = None):
        self.tool_registry = tool_registry
        self.env = env

    def estimate_outcome(self, tool_name: str, parameters: Dict[str, Any], context: str = "") -> WhatIfOutcome:
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return WhatIfOutcome(
                proposed_action=tool_name,
                expected_outcome="Unknown action and unknown outcome.",
                risk=RiskLevel.HIGH,
                confidence=0.0,
                recommendation="Do not execute. Tool does not exist.",
                predicted_metrics={}
            )
            
        if not self.env:
            # Fallback to static rules if environment is missing
            rec = "Proceed with caution."
            if tool.risk_level == RiskLevel.HIGH:
                rec = "Require human approval."
            elif tool.risk_level == RiskLevel.LOW:
                rec = "Safe to execute."
                
            return WhatIfOutcome(
                proposed_action=tool_name,
                expected_outcome="Cannot simulate without environment.",
                risk=tool.risk_level,
                confidence=0.5,
                recommendation=rec,
                predicted_metrics={}
            )
            
        # Real counterfactual simulation
        try:
            cloned_env = copy.deepcopy(self.env)
            
            # Re-bind the tool to the cloned environment
            cloned_tool = copy.deepcopy(tool)
            if hasattr(cloned_tool, "env"):
                cloned_tool.env = cloned_env
                
            cloned_tool.execute(**parameters)
            
            # Observe the mutated state
            new_metrics = cloned_env.metrics.get_all_latest()
            old_metrics = self.env.metrics.get_all_latest()
            
            improved = False
            if "cpu_usage" in new_metrics and new_metrics["cpu_usage"] < old_metrics.get("cpu_usage", 0) - 10:
                improved = True
                
            if "db_connections" in new_metrics and new_metrics["db_connections"] < old_metrics.get("db_connections", 0) - 100:
                improved = True
                
            if improved:
                expected_outcome = "System metrics are predicted to stabilize."
                recommendation = "RECOMMENDED. State improves."
                confidence = 0.95
            else:
                expected_outcome = "System metrics do not show significant improvement."
                recommendation = "NOT RECOMMENDED. Action appears ineffective."
                confidence = 0.8
                
            return WhatIfOutcome(
                proposed_action=tool_name,
                expected_outcome=expected_outcome,
                risk=tool.risk_level,
                confidence=confidence,
                recommendation=recommendation,
                predicted_metrics=new_metrics
            )
        except Exception as e:
            return WhatIfOutcome(
                proposed_action=tool_name,
                expected_outcome=f"Simulation failed: {str(e)}",
                risk=tool.risk_level,
                confidence=0.0,
                recommendation="Simulation error. Require human approval.",
                predicted_metrics={}
            )
