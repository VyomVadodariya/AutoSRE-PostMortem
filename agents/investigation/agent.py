from typing import List
from environment.incidents.models import Incident
from rca.correlation.evidence import Evidence
import time

class InvestigationAgent:
    def __init__(self, signal_store, metrics_store):
        self.signal_store = signal_store
        self.metrics_store = metrics_store

    def investigate(self, incident: Incident) -> List[Evidence]:
        # Simulated investigation gathering signals
        return [
            Evidence(
                source="metrics",
                description="Simulated metric anomaly related to " + str(incident.symptoms),
                timestamp=time.time(),
                confidence_contribution=0.5
            )
        ]
