from typing import List, Dict, Any, Optional
from environment.incidents.models import Incident
from rca.correlation.evidence import Evidence
from rca.engine import RCAEngine, RCA_Result
from memory.incidents.store import IncidentMemoryStore

class RCAAgent:
    def __init__(self, rca_engine: RCAEngine, memory_store: Optional[IncidentMemoryStore] = None):
        self.engine = rca_engine
        self.memory_store = memory_store

    def analyze(self, incident: Incident, evidence: List[Evidence]) -> RCA_Result:
        evidence_text = " ".join([e.description.lower() for e in evidence])
        
        has_db_timeout = "connection" in evidence_text or "pool exhausted" in evidence_text or "too many clients" in evidence_text
        has_high_cpu = "cpu" in evidence_text or "95%" in evidence_text
        has_process_evidence = "pid" in evidence_text
        has_miner = "xmrig" in evidence_text
        has_latency = "latency" in evidence_text or "timeout" in evidence_text
        
        hypotheses = [
            {
                "name": "Crypto miner causing CPU exhaustion",
                "supporting": sum([has_miner, has_high_cpu, has_process_evidence]),
                "contradicting": sum([has_db_timeout]),
                "chain": ["Unidentified process (xmrig) executed", "CPU resource starvation", "System degradation"]
            },
            {
                "name": "Database failure causing API retries",
                "supporting": sum([has_db_timeout, has_high_cpu, has_latency]),
                "contradicting": sum([has_miner]),
                "chain": ["Database connection pool exhaustion", "API retries increase", "CPU increase", "Latency increase", "User impact"]
            },
            {
                "name": "Network latency spike",
                "supporting": sum([has_latency]),
                "contradicting": sum([has_miner, has_process_evidence, has_high_cpu]),
                "chain": ["Network congestion", "API timeouts", "Slow response times"]
            },
            {
                "name": "CPU exhaustion",
                "supporting": sum([has_high_cpu, has_process_evidence]),
                "contradicting": sum([has_db_timeout, has_miner]),
                "chain": ["Process over-consuming CPU", "Resource starvation", "Service slowness"]
            },
            {
                "name": "Database connection pool exhaustion",
                "supporting": sum([has_db_timeout, has_latency]),
                "contradicting": sum([has_high_cpu, has_miner, has_process_evidence]),
                "chain": ["Database connections limit reached", "API fails to connect", "User errors"]
            }
        ]
        
        for h in hypotheses:
            h["confidence"] = max(0.0, min(1.0, (h["supporting"] - (h["contradicting"] * 0.5)) / 3.0))
            
        # Boost confidence based on historical semantic matches
        if self.memory_store:
            past_incidents = self.memory_store.search_similar_incidents(incident.symptoms, top_k=2)
            for h in hypotheses:
                # If a similar past incident had this root cause, boost it
                for past in past_incidents:
                    if past.root_cause == h["name"]:
                        h["confidence"] = min(1.0, h["confidence"] + 0.2)
                        h["chain"].append(f"[Memory]: High similarity to past incident {past.incident_id}.")
            
        best_hypothesis = max(hypotheses, key=lambda x: x["confidence"])
        
        # Override the confidence in the result to be the hypothesis confidence
        result = self.engine.generate_rca(incident, evidence, best_hypothesis["name"], causal_chain=best_hypothesis["chain"])
        result.confidence = round(best_hypothesis["confidence"], 2)
        return result
