import time
from typing import Dict, List, Optional
from environment.observability.metrics import MetricsStore
from environment.observability.signals import SignalStore, ProcessInfo, LogEntry
from environment.state import DatabaseState, ServiceState

class SimulationEnvironment:
    """
    Maintains the actual state of the simulated infrastructure.
    Tools interact with this state, and observability layers read from it.
    """
    def __init__(self, metrics_store: MetricsStore, signal_store: SignalStore):
        self.metrics = metrics_store
        self.signals = signal_store
        
        self.db_state = DatabaseState()
        self.services: Dict[str, ServiceState] = {}
        
        self.total_requests = 10000
        self.failed_requests = 0
        
        self._initialize_baseline()
        
    def _initialize_baseline(self):
        # Baseline healthy state
        self.services["nginx"] = ServiceState(name="nginx", dependencies=["api_server"])
        self.services["api_server"] = ServiceState(name="api_server", dependencies=["postgresql"])
        self.services["postgresql"] = ServiceState(name="postgresql")
        
        self.inject_process(pid=1, name="systemd", cpu=1.0, memory=2.0)
        self.inject_process(pid=100, name="nginx", cpu=5.0, memory=10.0)
        self.inject_process(pid=200, name="api_server", cpu=8.0, memory=15.0)
        self.inject_process(pid=300, name="postgresql", cpu=10.0, memory=25.0)
        
        self.recalculate_state()
        
    def recalculate_state(self):
        # Base database recalculation
        if self.db_state.active_connections > self.db_state.max_connections * 0.8:
            self.db_state.health = 0.5
            self.db_state.query_latency = 500.0
        else:
            self.db_state.health = 1.0
            self.db_state.query_latency = 10.0
            
        # Dependencies cascade
        for svc_name, svc in self.services.items():
            if "postgresql" in svc.dependencies:
                svc.health = self.db_state.health
            elif "api_server" in svc.dependencies:
                svc.health = self.services["api_server"].health
                
        # CPU affects everything
        total_cpu = min(100.0, sum(p.cpu_percent for p in self.signals.processes))
        if total_cpu > 90:
            for svc in self.services.values():
                svc.health *= 0.5
                
        # Update metrics
        self.metrics.record("cpu_usage", total_cpu)
        self.metrics.record("db_connections", float(self.db_state.active_connections))
        self.metrics.record("api_latency", self.db_state.query_latency + 30.0)
        
        # Calculate simulated requests based on health
        api_health = self.services.get("api_server", ServiceState(name="")).health
        nginx_health = self.services.get("nginx", ServiceState(name="")).health
        overall_health = api_health * nginx_health
        
        # Requests metrics
        self.total_requests += 500
        new_failed = int(500 * (1.0 - overall_health))
        self.failed_requests += new_failed
        
        self.metrics.record("total_requests", self.total_requests)
        self.metrics.record("failed_requests", self.failed_requests)

    def inject_process(self, pid: int, name: str, cpu: float, memory: float):
        # Ensure unique PID
        self.remove_process(pid)
        self.signals.add_process(ProcessInfo(
            pid=pid, name=name, cpu_percent=cpu, memory_percent=memory, 
            status="running", user="root"
        ))
        self.recalculate_state()
        
    def remove_process(self, pid: int) -> bool:
        initial_len = len(self.signals.processes)
        self.signals.processes = [p for p in self.signals.processes if p.pid != pid]
        if len(self.signals.processes) < initial_len:
            self.signals.add_log(LogEntry(service="kernel", level="INFO", message=f"Process {pid} terminated.", timestamp=time.time()))
            self.recalculate_state()
            return True
        return False
        
    def reset_service(self, name: str):
        if name in self.services:
            self.services[name].restart_count += 1
            self.services[name].status = "restarting"
            self.signals.add_log(LogEntry(service="systemd", level="INFO", message=f"Service {name} restarted.", timestamp=time.time()))
            
        if name == "postgresql":
            self.db_state.active_connections = 45
            self.db_state.connection_leaks = 0
            self.db_state.status = "healthy"
            
        elif name == "api_server":
            self.services["api_server"].health = 1.0
            
        self.recalculate_state()
