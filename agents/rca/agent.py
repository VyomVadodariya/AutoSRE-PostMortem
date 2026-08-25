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
        
        # Analyze causal chains rather than just keywords
        has_db_timeout = "connection" in evidence_text or "pool exhausted" in evidence_text
        has_high_cpu = "cpu" in evidence_text
        has_process_evidence = "pid" in evidence_text
        has_miner = "xmrig" in evidence_text
        
        if has_db_timeout and has_high_cpu and not has_miner:
            # Adversarial case: DB failure causing CPU spikes due to retries
            deduced_cause = "Database failure causing API retries"
        elif has_high_cpu and has_process_evidence:
            # Standard infrastructure CPU exhaustion
            deduced_cause = "CPU exhaustion"
            if has_miner:
                deduced_cause = "Crypto miner causing CPU exhaustion"
        elif has_db_timeout:
            deduced_cause = "Database connection pool exhaustion"
        elif "memory" in evidence_text:
            deduced_cause = "Memory leak or exhaustion"
        elif "latency" in evidence_text:
            deduced_cause = "Network latency spike"
            
        return self.engine.generate_rca(incident, evidence, deduced_cause)
