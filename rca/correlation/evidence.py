from pydantic import BaseModel, Field
from typing import List, Optional

class Evidence(BaseModel):
    source: str  # e.g., "metrics", "logs", "deployment", "process"
    description: str
    timestamp: float
    confidence_contribution: float = 0.0

class CorrelatedFinding(BaseModel):
    title: str
    evidence_list: List[Evidence] = Field(default_factory=list)
    confidence: float
    deduced_cause: str
    
    def add_evidence(self, evidence: Evidence):
        self.evidence_list.append(evidence)
        self._recalculate_confidence()
        
    def _recalculate_confidence(self):
        # A simple additive model for confidence based on evidence
        total_contribution = sum(e.confidence_contribution for e in self.evidence_list)
        # Cap at 99%
        self.confidence = min(0.99, total_contribution)

class CorrelationEngine:
    """
    A foundational engine that takes multiple signals (deployments, anomalies, logs)
    and helps pre-correlate them into findings for the AI agent to evaluate.
    """
    def __init__(self):
        self.findings: List[CorrelatedFinding] = []
        
    def correlate_deployment_and_metric(self, deployment_time: float, metric_time: float, 
                                        deployment_desc: str, metric_desc: str) -> Optional[CorrelatedFinding]:
        """
        If a metric spike happens shortly after a deployment, correlate them.
        """
        time_diff = metric_time - deployment_time
        
        # If metric spiked within 5 minutes (300 seconds) after deployment
        if 0 <= time_diff <= 300:
            finding = CorrelatedFinding(
                title="Deployment-Induced Metric Anomaly",
                confidence=0.0,
                deduced_cause="Recent deployment likely caused system degradation."
            )
            finding.add_evidence(Evidence(
                source="deployment", 
                description=deployment_desc, 
                timestamp=deployment_time, 
                confidence_contribution=0.4
            ))
            finding.add_evidence(Evidence(
                source="metrics", 
                description=metric_desc, 
                timestamp=metric_time, 
                confidence_contribution=0.5
            ))
            self.findings.append(finding)
            return finding
            
        return None
