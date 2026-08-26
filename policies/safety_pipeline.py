from typing import Any
from pydantic import BaseModel

from policies.risk.levels import RiskLevel
from environment.observability.metrics import MetricsStore
from tools.base import BaseTool

class SafetyDecision(BaseModel):
    approved: bool
    reason: str
    budget_remaining: float
    blast_radius: str

class SafetyPipeline:
    def __init__(self, metrics_store: MetricsStore):
        self.metrics_store = metrics_store
        self.error_budget = 100.0  # arbitrary starting budget
        
    def _analyze_blast_radius(self, tool: BaseTool, parameters: dict[str, Any]) -> str:
        service = parameters.get("service_name", "unknown")
        if service in ["database", "payment_gateway", "postgresql"]:
            return "GLOBAL"
        elif service in ["nginx", "api"]:
            return "REGIONAL"
        return "LOCAL"
        
    def evaluate_request(self, tool: BaseTool, parameters: dict[str, Any]) -> SafetyDecision:
        # Risk Classification
        risk = tool.risk_level
        
        # Blast Radius Analysis
        blast_radius = self._analyze_blast_radius(tool, parameters)
        
        # Budget Check & Approval Gate
        cost = 10.0 if risk == RiskLevel.HIGH else (5.0 if risk == RiskLevel.MEDIUM else 1.0)
        
        if self.error_budget < cost:
            return SafetyDecision(
                approved=False,
                reason="Error budget exhausted",
                budget_remaining=self.error_budget,
                blast_radius=blast_radius
            )
            
        if risk == RiskLevel.HIGH and blast_radius == "GLOBAL":
            return SafetyDecision(
                approved=False, # Adversarial check: block high risk + global blast without explicit human override
                reason="High risk action on global blast radius requires explicit override.",
                budget_remaining=self.error_budget,
                blast_radius=blast_radius
            )
            
        # Approved
        self.error_budget -= cost
        return SafetyDecision(
            approved=True,
            reason="Approved by safety policy",
            budget_remaining=self.error_budget,
            blast_radius=blast_radius
        )
