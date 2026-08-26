from __future__ import annotations

import copy
from typing import Any

from pydantic import BaseModel

from environment.simulation import SimulationEnvironment
from policies.risk.levels import RiskLevel
from tools.registry import ToolRegistry


class WhatIfOutcome(BaseModel):
    proposed_action: str
    expected_outcome: str
    risk: RiskLevel
    blast_radius: str
    recovery_probability: float
    historical_success: float
    root_cause_alignment: float
    utility_score: float
    confidence: float
    recommendation: str
    predicted_metrics: dict[str, float]

class WhatIfEngine:
    def __init__(self, tool_registry: ToolRegistry, env: SimulationEnvironment | None = None):
        self.tool_registry = tool_registry
        self.env = env

    def estimate_outcome(self, tool_name: str, parameters: dict[str, Any], context: str = "") -> WhatIfOutcome:
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return WhatIfOutcome(
                proposed_action=tool_name, expected_outcome="Unknown action and unknown outcome.",
                risk=RiskLevel.HIGH, blast_radius="UNKNOWN", recovery_probability=0.0,
                historical_success=0.0, root_cause_alignment=0.0, utility_score=-100.0,
                confidence=0.0, recommendation="Do not execute. Tool does not exist.",
                predicted_metrics={}
            )
            
        service = parameters.get("service_name", "unknown")
        if service in ["database", "payment_gateway", "postgresql"]:
            blast_radius = "GLOBAL"
        elif service in ["nginx", "api"]:
            blast_radius = "REGIONAL"
        else:
            blast_radius = "LOCAL"

        if not self.env:
            return WhatIfOutcome(
                proposed_action=tool_name, expected_outcome="Cannot simulate without environment.",
                risk=tool.risk_level, blast_radius=blast_radius, recovery_probability=0.5,
                historical_success=0.5, root_cause_alignment=0.5, utility_score=0.0,
                confidence=0.5, recommendation="Proceed with caution.", predicted_metrics={}
            )
            
        try:
            cloned_env = copy.deepcopy(self.env)
            cloned_tool = copy.deepcopy(tool)
            if hasattr(cloned_tool, "env"):
                cloned_tool.env = cloned_env
                
            cloned_tool.execute(**parameters)
            
            new_metrics = cloned_env.metrics.get_all_latest()
            old_metrics = self.env.metrics.get_all_latest()
            
            improved = False
            if "cpu_usage" in new_metrics and new_metrics["cpu_usage"] < old_metrics.get("cpu_usage", 0) - 10:
                improved = True
            if "db_connections" in new_metrics and new_metrics["db_connections"] < old_metrics.get("db_connections", 0) - 100:
                improved = True
                
            recovery_probability = 0.9 if improved else 0.1
            historical_success = 0.8 # Mocked historical success
            root_cause_alignment = 0.8 if improved else 0.2
            
            risk_penalty = {"LOW": 0.1, "MEDIUM": 0.5, "HIGH": 0.9}.get(tool.risk_level.value, 0.5)
            blast_penalty = {"LOCAL": 0.1, "REGIONAL": 0.5, "GLOBAL": 0.9}.get(blast_radius, 0.5)
            
            utility_score = (recovery_probability + root_cause_alignment + historical_success) - risk_penalty - blast_penalty
            
            if utility_score > 1.0:
                recommendation = "RECOMMENDED. High utility."
            elif utility_score > 0.0:
                recommendation = "NEUTRAL. Marginal utility."
            else:
                recommendation = "NOT RECOMMENDED. Negative utility."
                
            return WhatIfOutcome(
                proposed_action=tool_name,
                expected_outcome="System metrics predicted to stabilize." if improved else "No significant improvement.",
                risk=tool.risk_level,
                blast_radius=blast_radius,
                recovery_probability=recovery_probability,
                historical_success=historical_success,
                root_cause_alignment=root_cause_alignment,
                utility_score=round(utility_score, 2),
                confidence=0.95 if improved else 0.8,
                recommendation=recommendation,
                predicted_metrics=new_metrics
            )
        except Exception as e: # noqa: BLE001
            return WhatIfOutcome(
                proposed_action=tool_name, expected_outcome=f"Simulation failed: {e!s}",
                risk=tool.risk_level, blast_radius=blast_radius, recovery_probability=0.0,
                historical_success=0.0, root_cause_alignment=0.0, utility_score=-50.0,
                confidence=0.0, recommendation="Simulation error.", predicted_metrics={}
            )
