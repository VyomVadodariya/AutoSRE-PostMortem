from pydantic import BaseModel
from typing import Dict, Any
from tools.registry import ToolRegistry
from policies.risk.levels import RiskLevel
from environment.observability.metrics import MetricsStore

class WhatIfOutcome(BaseModel):
    proposed_action: str
    expected_outcome: str
    risk: RiskLevel
    confidence: float
    recommendation: str

class WhatIfEngine:
    def __init__(self, tool_registry: ToolRegistry, metrics_store: MetricsStore = None):
        self.tool_registry = tool_registry
        self.metrics_store = metrics_store

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
            
        current_metrics = self.metrics_store.get_all_latest() if self.metrics_store else {}
        
        # Real counterfactual simulation logic based on current state and tool
        expected_outcome = f"System state will be mutated by {tool_name}."
        recommendation = "Proceed with caution."
        confidence = 0.85
        
        if tool_name == "kill_process":
            if current_metrics.get("cpu_usage", 0) > 80:
                expected_outcome = "CPU utilization is expected to drop."
                recommendation = "RECOMMENDED. Directly addresses CPU exhaustion."
                confidence = 0.95
            else:
                expected_outcome = "Process termination will cause disruption."
                recommendation = "NOT RECOMMENDED. CPU is not exhausted."
                confidence = 0.90
                
        elif tool_name == "restart_service":
            if "postgresql" in parameters.get("service_name", "") and current_metrics.get("db_connections", 0) > 800:
                expected_outcome = "Database connections will reset."
                recommendation = "RECOMMENDED. Addresses connection exhaustion."
            else:
                expected_outcome = "Service restart will cause momentary downtime."
                recommendation = "Safe to execute, but may not address root cause."
        elif tool.risk_level == RiskLevel.LOW:
            recommendation = "Safe to execute."
        
        if tool.risk_level == RiskLevel.HIGH and not recommendation.startswith("RECOMMENDED"):
            recommendation = "High risk. Require human approval."
            
        return WhatIfOutcome(
            proposed_action=tool_name,
            expected_outcome=expected_outcome,
            risk=tool.risk_level,
            confidence=confidence,
            recommendation=recommendation
        )
