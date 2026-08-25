from typing import List
from environment.incidents.models import Incident
from rca.correlation.evidence import Evidence
from rca.engine import RCAEngine, RCA_Result

class RCAAgent:
    def __init__(self, rca_engine: RCAEngine):
        self.engine = rca_engine

    def analyze(self, incident: Incident, evidence: List[Evidence]) -> RCA_Result:
        # In a real system, the AI determines the root cause. Here we mock it.
        deduced_cause = incident.root_cause
        return self.engine.generate_rca(incident, evidence, deduced_cause)
