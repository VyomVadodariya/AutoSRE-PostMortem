from typing import List
from environment.incidents.models import Incident
from rca.correlation.evidence import Evidence
from rca.engine import RCAEngine, RCA_Result

class RCAAgent:
    def __init__(self, rca_engine: RCAEngine):
        self.engine = rca_engine

    def analyze(self, incident: Incident, evidence: List[Evidence]) -> RCA_Result:
        deduced_cause = "Unknown service failure"
        
        evidence_text = " ".join([e.description.lower() for e in evidence])
        symptoms = " ".join(incident.symptoms).lower()
        
        if "cpu" in evidence_text or "cpu" in symptoms:
            deduced_cause = "CPU exhaustion"
        elif "connection" in evidence_text or "database" in symptoms:
            deduced_cause = "Database connection exhaustion"
        elif "memory" in evidence_text or "oom" in symptoms:
            deduced_cause = "Memory exhaustion"
        elif "latency" in evidence_text or "timeout" in symptoms:
            deduced_cause = "High network latency"
            
        return self.engine.generate_rca(incident, evidence, deduced_cause)
