from typing import List
from environment.incidents.models import Incident
from rca.correlation.evidence import Evidence
import time

class InvestigationAgent:
    def __init__(self, signal_store, metrics_store):
        self.signal_store = signal_store
        self.metrics_store = metrics_store

    def investigate(self, incident: Incident) -> List[Evidence]:
        evidence = []
        
        # Real investigation based on actual metrics
        latest_metrics = self.metrics_store.get_all_latest()
        for metric_name, value in latest_metrics.items():
            if "cpu" in metric_name.lower() and value > 90.0:
                evidence.append(Evidence(
                    source="metrics",
                    description=f"High CPU utilization detected: {value}%",
                    timestamp=time.time(),
                    confidence_contribution=0.9
                ))
            elif "memory" in metric_name.lower() and value > 90.0:
                evidence.append(Evidence(
                    source="metrics",
                    description=f"High memory utilization detected: {value}%",
                    timestamp=time.time(),
                    confidence_contribution=0.8
                ))
            elif "connection" in metric_name.lower() and value > 900.0:
                evidence.append(Evidence(
                    source="metrics",
                    description=f"High database connections: {value}",
                    timestamp=time.time(),
                    confidence_contribution=0.9
                ))
            elif "latency" in metric_name.lower() and value > 2000.0:
                evidence.append(Evidence(
                    source="metrics",
                    description=f"High latency: {value}ms",
                    timestamp=time.time(),
                    confidence_contribution=0.8
                ))

        # Inspect Processes
        if hasattr(self.signal_store, 'processes'):
            for p in self.signal_store.processes:
                if p.cpu_percent > 50.0:
                    evidence.append(Evidence(
                        source="processes",
                        description=f"Process {p.name} (PID: {p.pid}) consuming {p.cpu_percent}% CPU.",
                        timestamp=time.time(),
                        confidence_contribution=0.95
                    ))

        # Inspect Logs
        if hasattr(self.signal_store, 'logs'):
            for log in self.signal_store.get_recent_logs(20):
                if log.level in ["ERROR", "FATAL"]:
                    evidence.append(Evidence(
                        source="logs",
                        description=f"[{log.service}] {log.level}: {log.message}",
                        timestamp=log.timestamp,
                        confidence_contribution=0.85
                    ))

        if not evidence:
            evidence.append(Evidence(
                source="symptoms",
                description=f"Based on symptoms: {', '.join(incident.symptoms)}",
                timestamp=time.time(),
                confidence_contribution=0.5
            ))
            
        return evidence
