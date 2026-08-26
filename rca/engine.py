from __future__ import annotations

from pydantic import BaseModel

from environment.incidents.models import Incident
from rca.correlation.evidence import Evidence
from rca.dependency_graph.graph import DependencyGraph


class RCA_Result(BaseModel):
    symptoms: list[str]
    root_cause: str
    contributing_factors: list[str]
    impact: str
    evidence: list[Evidence]
    confidence: float
    causal_chain: list[str] = []

class RCAEngine:
    """
    Root Cause Analysis Engine.
    Structures the AI agent's findings into a formal RCA.
    """
    def __init__(self, dependency_graph: DependencyGraph):
        self.dependency_graph = dependency_graph
        
    def generate_rca(self, incident: Incident, evidence_collected: list[Evidence], deduced_cause: str, causal_chain: list[str] | None = None) -> RCA_Result:
        # Calculate impact based on the dependency graph
        all_affected = set(incident.services_affected)
        for s in incident.services_affected:
            impacts = self.dependency_graph.get_downstream_impact(s)
            all_affected.update(impacts)
            
        impact_statement = f"Service degradation affecting: {', '.join(sorted(all_affected))}"
        if incident.expected_impact:
            impact_statement += f". Expected: {incident.expected_impact}"
            
        # Basic confidence calculation based on evidence volume 
        # (The AI will provide more nuanced confidence later)
        confidence = 0.5
        if evidence_collected:
            confidence = min(0.99, 0.5 + (len(evidence_collected) * 0.15))
            
        return RCA_Result(
            symptoms=incident.symptoms,
            root_cause=deduced_cause,
            contributing_factors=incident.contributing_factors,
            impact=impact_statement,
            evidence=evidence_collected,
            confidence=round(confidence, 2),
            causal_chain=causal_chain or []
        )
