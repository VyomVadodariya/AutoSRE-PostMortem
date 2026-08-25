from environment.incidents.generator import IncidentGenerator
from environment.incidents.models import Incident
from typing import Optional

class ChaosInjector:
    """
    Injects intentional failures into the environment for chaos engineering testing.
    """
    def __init__(self, incident_generator: IncidentGenerator):
        self.generator = incident_generator
        
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
        elif failure_type == "network_latency":
            incident._hidden_root_cause = "High latency"
            incident.symptoms = ["API timeouts", "Slow response times"]
        elif failure_type == "database_failure":
            incident._hidden_root_cause = "Connection pool exhaustion"
            incident.symptoms = ["API failing to connect to DB"]
            
        return incident
