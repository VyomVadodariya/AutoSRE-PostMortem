import time
from typing import Dict, List, Optional
from environment.observability.metrics import MetricsStore
from environment.observability.signals import SignalStore, ProcessInfo, LogEntry

class SimulationEnvironment:
    """
    Maintains the actual state of the simulated infrastructure.
    Tools interact with this state, and observability layers read from it.
    """
    def __init__(self, metrics_store: MetricsStore, signal_store: SignalStore):
        self.metrics = metrics_store
        self.signals = signal_store
        self._initialize_baseline()
        
    def _initialize_baseline(self):
        # Baseline healthy state
        self.inject_process(pid=1, name="systemd", cpu=1.0, memory=2.0)
        self.inject_process(pid=100, name="nginx", cpu=5.0, memory=10.0)
        self.inject_process(pid=200, name="api_server", cpu=8.0, memory=15.0)
        self.inject_process(pid=300, name="postgresql", cpu=10.0, memory=25.0)
        
        self.metrics.record("db_connections", 45.0)
        self.metrics.record("api_latency", 40.0)
        
    def inject_process(self, pid: int, name: str, cpu: float, memory: float):
        # Ensure unique PID
        self.remove_process(pid)
        self.signals.add_process(ProcessInfo(
            pid=pid, name=name, cpu_percent=cpu, memory_percent=memory, 
            status="running", user="root"
        ))
        self._recalculate_cpu()
        
    def remove_process(self, pid: int) -> bool:
        initial_len = len(self.signals.processes)
        self.signals.processes = [p for p in self.signals.processes if p.pid != pid]
        if len(self.signals.processes) < initial_len:
            self._recalculate_cpu()
            return True
        return False
        
    def reset_service(self, name: str):
        if name == "postgresql":
            self.metrics.record("db_connections", 20.0)
        elif name == "nginx":
            self.metrics.record("api_latency", 30.0)
            
    def _recalculate_cpu(self):
        total_cpu = min(100.0, sum(p.cpu_percent for p in self.signals.processes))
        self.metrics.record("cpu_usage", total_cpu)
