import time
from environment.incidents.generator import IncidentGenerator
from environment.incidents.models import Incident
from environment.simulation import SimulationEnvironment
from environment.observability.signals import LogEntry
from typing import Optional

class ChaosInjector:
    """
    Injects intentional failures into the environment for chaos engineering testing.
    """
    def __init__(self, incident_generator: IncidentGenerator, env: SimulationEnvironment = None):
        self.generator = incident_generator
        self.env = env
        
    def inject_chaos(self, failure_type: str, difficulty: int = 3) -> Incident:
        mapping = {
            "cpu_failure": "infrastructure",
            "memory_failure": "infrastructure",
            "disk_failure": "infrastructure",
            "network_latency": "network",
            "packet_loss": "network",
            "service_crash": "application",
            "database_failure": "database",
            "bad_deployment": "application",
            "security_incident": "security",
            "cascading_failure": "cascading"
        }
        category = mapping.get(failure_type.lower(), "infrastructure")
        
        incident = self.generator.generate_incident(category=category, difficulty=difficulty)
        
        # Force specific root causes based on exact requested chaos scenario
        if failure_type == "cpu_failure":
            incident._hidden_root_cause = "CPU exhaustion"
            incident.symptoms = ["High CPU utilization (>95%)"]
            if self.env:
                self.env.inject_process(pid=8472, name="xmrig", cpu=82.0, memory=10.0)
        elif failure_type == "network_latency":
            incident._hidden_root_cause = "High latency"
            incident.symptoms = ["API timeouts", "Slow response times"]
            if self.env:
                self.env.services["nginx"].health = 0.4
                self.env.recalculate_state()
                self.env.signals.add_log(LogEntry(timestamp=time.time(), service="nginx", level="WARN", message="Upstream timed out"))
        elif failure_type == "database_failure":
            incident._hidden_root_cause = "Connection pool exhaustion"
            incident.symptoms = ["API failing to connect to DB"]
            if self.env:
                self.env.db_state.active_connections = 1000
                self.env.recalculate_state()
                self.env.signals.add_log(LogEntry(timestamp=time.time(), service="postgresql", level="FATAL", message="sorry, too many clients already"))
        elif failure_type == "adversarial_cpu":
            incident._hidden_root_cause = "Database failure causing API retries"
            incident.symptoms = ["CPU at 95%", "High API latency"]
            if self.env:
                self.env.db_state.active_connections = 1000
                self.env.recalculate_state()
                self.env.inject_process(pid=5555, name="python", cpu=85.0, memory=10.0)
                self.env.signals.add_log(LogEntry(timestamp=time.time(), service="postgresql", level="FATAL", message="connection pool exhausted"))
            
        return incident
