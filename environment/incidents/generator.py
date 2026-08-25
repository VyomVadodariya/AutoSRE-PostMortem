import uuid
import random
from datetime import datetime, timezone
from typing import Optional, List
from environment.incidents.models import Incident, IncidentClass, IncidentSeverity

class IncidentGenerator:
    def __init__(self):
        pass

    def _generate_id(self) -> str:
        return f"INC-{uuid.uuid4().hex[:8].upper()}"

    def generate_incident(self, category: Optional[str] = None, difficulty: Optional[int] = None) -> Incident:
        categories = ["infrastructure", "network", "application", "database", "security", "multi_failure", "cascading"]
        if not category:
            category = random.choice(categories)
            
        if not difficulty:
            difficulty = random.randint(1, 7)

        method_name = f"_generate_{category}_incident"
        if hasattr(self, method_name):
            return getattr(self, method_name)(difficulty)
        
        return self._generate_infrastructure_incident(difficulty)

    def _generate_infrastructure_incident(self, difficulty: int) -> Incident:
        infra_types = [
            ("CPU exhaustion", ["High CPU utilization (>95%)", "Service latency spikes"], ["kill_process", "restart_service"]),
            ("Memory exhaustion", ["OOM Kill messages in logs", "Container restarts"], ["restart_service", "scale_service"]),
            ("Disk exhaustion", ["Disk usage at 100%", "Write errors in logs"], ["clear_logs"]),
            ("Inode exhaustion", ["No space left on device (but disk has space)"], ["clear_logs", "delete_files"]),
            ("Process crash", ["Process not running", "502 Bad Gateway"], ["restart_service"]),
            ("File descriptor exhaustion", ["Too many open files error"], ["restart_service", "modify_limits"])
        ]
        
        choice = random.choice(infra_types)
        return Incident(
            incident_id=self._generate_id(),
            timestamp=datetime.now(timezone.utc),
            incident_class=IncidentClass.INFRASTRUCTURE,
            severity=IncidentSeverity.HIGH,
            services_affected=["nginx", "worker"],
            symptoms=choice[1],
            root_cause=choice[0],
            contributing_factors=["Lack of resource limits"],
            expected_impact="Service degradation or complete outage",
            available_remediations=choice[2],
            difficulty=difficulty
        )

    def _generate_network_incident(self, difficulty: int) -> Incident:
        net_types = [
            ("Packet loss", ["Intermittent connectivity issues", "Retries spiking"], ["restart_service", "modify_network"]),
            ("High latency", ["API timeouts", "Slow response times"], ["modify_network"]),
            ("DNS failure", ["Cannot resolve internal services", "503 Service Unavailable"], ["restart_service"]),
            ("Connection exhaustion", ["Connection timeouts", "Port exhaustion"], ["restart_service", "scale_service"]),
        ]
        choice = random.choice(net_types)
        return Incident(
            incident_id=self._generate_id(),
            timestamp=datetime.now(timezone.utc),
            incident_class=IncidentClass.NETWORK,
            severity=IncidentSeverity.MEDIUM,
            services_affected=["api_gateway", "load_balancer"],
            symptoms=choice[1],
            root_cause=choice[0],
            contributing_factors=["Network configuration change"],
            expected_impact="Increased latency and error rates",
            available_remediations=choice[2],
            difficulty=difficulty
        )

    def _generate_application_incident(self, difficulty: int) -> Incident:
        app_types = [
            ("HTTP 500 spike", ["Error rate increased > 10%"], ["rollback_deployment"]),
            ("Memory leak", ["Gradual memory increase", "Periodic OOM kills"], ["rollback_deployment", "restart_service"]),
            ("Database connection exhaustion", ["DB timeout errors", "Max connections reached"], ["restart_service"]),
            ("Queue backlog", ["Queue depth growing", "Delayed processing"], ["scale_service"]),
            ("Dependency failure", ["Third-party API timeouts", "502 Bad Gateway"], ["modify_network"]),
            ("Deadlock", ["Threads stuck", "No CPU usage but app unresponsive"], ["restart_service"])
        ]
        choice = random.choice(app_types)
        return Incident(
            incident_id=self._generate_id(),
            timestamp=datetime.now(timezone.utc),
            incident_class=IncidentClass.APPLICATION,
            severity=IncidentSeverity.HIGH,
            services_affected=["api_server", "background_worker"],
            symptoms=choice[1],
            root_cause=choice[0],
            contributing_factors=["Recent deployment v2.4.1"],
            expected_impact="Failed user requests",
            available_remediations=choice[2],
            difficulty=difficulty
        )

    def _generate_database_incident(self, difficulty: int) -> Incident:
        db_types = [
            ("Slow query", ["DB CPU high", "API latency increased"], ["restart_service", "kill_process"]),
            ("Connection pool exhaustion", ["API failing to connect to DB"], ["restart_service", "scale_service"]),
            ("Replication lag", ["Stale data read by users"], ["restart_database"]),
            ("Locked table", ["Queries piling up", "Write timeouts"], ["kill_process"]),
            ("Database disk pressure", ["DB write latency spikes", "Disk usage high"], ["clear_logs"])
        ]
        choice = random.choice(db_types)
        return Incident(
            incident_id=self._generate_id(),
            timestamp=datetime.now(timezone.utc),
            incident_class=IncidentClass.DATABASE,
            severity=IncidentSeverity.CRITICAL,
            services_affected=["postgresql"],
            symptoms=choice[1],
            root_cause=choice[0],
            contributing_factors=["Unoptimized query introduced recently"],
            expected_impact="Database unavailability leading to complete system outage",
            available_remediations=choice[2],
            difficulty=difficulty
        )

    def _generate_security_incident(self, difficulty: int) -> Incident:
        sec_types = [
            ("Crypto miner", ["CPU at 100%", "Unknown process xmrig running"], ["kill_process"]),
            ("Suspicious process", ["Unknown binary in /tmp"], ["kill_process", "delete_files"]),
            ("Brute-force activity", ["High rate of failed logins in logs"], ["modify_network"]),
            ("Malicious outbound connection", ["Unexpected connections to known bad IPs"], ["modify_network", "kill_process"]),
            ("Unauthorized deployment", ["Unexpected container running"], ["terminate_process", "rollback_deployment"])
        ]
        choice = random.choice(sec_types)
        return Incident(
            incident_id=self._generate_id(),
            timestamp=datetime.now(timezone.utc),
            incident_class=IncidentClass.SECURITY,
            severity=IncidentSeverity.CRITICAL,
            services_affected=["worker", "auth_service"],
            symptoms=choice[1],
            root_cause=choice[0],
            contributing_factors=["Compromised credentials", "Missing security group rules"],
            expected_impact="Potential data exfiltration or resource theft",
            available_remediations=choice[2],
            difficulty=difficulty
        )

    def _generate_multi_failure_incident(self, difficulty: int) -> Incident:
        return Incident(
            incident_id=self._generate_id(),
            timestamp=datetime.now(timezone.utc),
            incident_class=IncidentClass.SECURITY,
            severity=IncidentSeverity.CRITICAL,
            services_affected=["api_server", "nginx"],
            symptoms=["High CPU utilization (>95%)", "API latency spikes", "Unknown process running"],
            root_cause="Crypto miner causing CPU exhaustion",
            contributing_factors=["Missing resource limits", "Compromised container"],
            expected_impact="Service outage and resource theft",
            available_remediations=["kill_process", "restart_service"],
            difficulty=max(difficulty, 3)
        )
        
    def _generate_cascading_incident(self, difficulty: int) -> Incident:
        return Incident(
            incident_id=self._generate_id(),
            timestamp=datetime.now(timezone.utc),
            incident_class=IncidentClass.DATABASE,
            severity=IncidentSeverity.CRITICAL,
            services_affected=["postgresql", "api_server", "nginx"],
            symptoms=["HTTP 500 increases", "API latency increases", "Python CPU increases", "DB connection timeouts"],
            root_cause="Database failure caused API retries, which caused Python CPU increase",
            contributing_factors=["Lack of circuit breaker", "Aggressive retry policy"],
            expected_impact="System wide outage due to cascading failure",
            available_remediations=["restart_database", "restart_service"],
            difficulty=max(difficulty, 5)
        )
