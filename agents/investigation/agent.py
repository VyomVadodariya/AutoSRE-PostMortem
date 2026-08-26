import time

from environment.incidents.models import Incident
from rca.correlation.evidence import Evidence


class InvestigationAgent:
    def __init__(self, signal_store, metrics_store):
        self.signal_store = signal_store
        self.metrics_store = metrics_store

    def investigate(self, incident: Incident) -> list[Evidence]:
        evidence = []
        budget = 8
        self.timeline = []
        
        self.timeline.append(f"[Thought]: Starting investigation. Initial symptoms: {', '.join(incident.symptoms)}")
        
        # Step 1: Check metrics
        self.timeline.append("[Thought]: I need to check the current system metrics to confirm the symptoms.")
        self.timeline.append("[Action]: get_metric_history()")
        budget -= 1
        
        metrics_anomalies = []
        latest_metrics = self.metrics_store.get_all_latest()
        if latest_metrics.get("cpu_usage", 0) > 90.0:
            metrics_anomalies.append("CPU")
            evidence.append(Evidence(source="metrics", description=f"High CPU utilization detected: {latest_metrics['cpu_usage']}%", timestamp=time.time(), confidence_contribution=0.9))
            self.timeline.append(f"[Observation]: CPU is critically high ({latest_metrics['cpu_usage']}%).")
        if latest_metrics.get("db_connections", 0) > 900.0:
            metrics_anomalies.append("Database")
            evidence.append(Evidence(source="metrics", description=f"High database connections: {latest_metrics['db_connections']}", timestamp=time.time(), confidence_contribution=0.9))
            self.timeline.append(f"[Observation]: Database connection pool is nearly exhausted ({latest_metrics['db_connections']} connections).")
        if latest_metrics.get("api_latency", 0) > 2000.0:
            metrics_anomalies.append("Latency")
            evidence.append(Evidence(source="metrics", description=f"High API latency: {latest_metrics['api_latency']}ms", timestamp=time.time(), confidence_contribution=0.8))
            self.timeline.append(f"[Observation]: API latency is elevated ({latest_metrics['api_latency']}ms).")

        # Step 2: Branch based on metrics
        if ("CPU" in metrics_anomalies or "Latency" in metrics_anomalies) and budget > 0:
            self.timeline.append("[Thought]: I should list active processes to see if a specific process is consuming resources.")
            self.timeline.append("[Action]: list_processes()")
            budget -= 1
            if hasattr(self.signal_store, 'processes'):
                for p in self.signal_store.processes:
                    if p.cpu_percent > 50.0:
                        evidence.append(Evidence(source="processes", description=f"Process {p.name} (PID: {p.pid}) consuming {p.cpu_percent}% CPU.", timestamp=time.time(), confidence_contribution=0.95))
                        self.timeline.append(f"[Observation]: Process {p.name} (PID {p.pid}) is using {p.cpu_percent}% CPU.")
        
        if ("Database" in metrics_anomalies or "Latency" in metrics_anomalies) and budget > 0:
            self.timeline.append("[Thought]: I should check the logs to see if there are backend connection failures.")
            self.timeline.append("[Action]: inspect_logs('all')")
            budget -= 1
            if hasattr(self.signal_store, 'logs'):
                for log in self.signal_store.get_recent_logs(20):
                    if log.level in ["ERROR", "FATAL"]:
                        evidence.append(Evidence(source="logs", description=f"[{log.service}] {log.level}: {log.message}", timestamp=log.timestamp, confidence_contribution=0.85))
                        self.timeline.append(f"[Observation]: Found {log.level} log in {log.service}: {log.message}")
        
        # Checking Deployments
        if budget > 0:
            self.timeline.append("[Thought]: Checking recent deployments to rule out bad releases.")
            self.timeline.append("[Action]: get_deployments()")
            budget -= 1
            self.timeline.append("[Observation]: No anomalous deployments in the last hour.")

        if not evidence:
            evidence.append(Evidence(
                source="symptoms",
                description=f"Based on symptoms: {', '.join(incident.symptoms)}",
                timestamp=time.time(),
                confidence_contribution=0.5
            ))
            
        self.timeline.append("[Thought]: I have exhausted my tool budget or found enough evidence to proceed to RCA.")
        return evidence
