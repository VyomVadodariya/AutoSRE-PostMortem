from pydantic import BaseModel, Field
from typing import List, Optional

class LogEntry(BaseModel):
    timestamp: float
    service: str
    level: str
    message: str

class ProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str
    user: str

class NetworkEvent(BaseModel):
    timestamp: float
    source_ip: str
    dest_ip: str
    port: int
    bytes_transferred: int
    status: str

class DeploymentEvent(BaseModel):
    timestamp: float
    service: str
    version: str
    status: str
    deployed_by: str

class SignalStore(BaseModel):
    """
    Simulated storage for various non-metric observability signals.
    """
    logs: List[LogEntry] = Field(default_factory=list)
    processes: List[ProcessInfo] = Field(default_factory=list)
    network_events: List[NetworkEvent] = Field(default_factory=list)
    deployments: List[DeploymentEvent] = Field(default_factory=list)
    
    def add_log(self, log: LogEntry):
        self.logs.append(log)
        
    def add_process(self, process: ProcessInfo):
        self.processes.append(process)

    def add_network_event(self, event: NetworkEvent):
        self.network_events.append(event)
        
    def add_deployment(self, event: DeploymentEvent):
        self.deployments.append(event)
        
    def get_recent_logs(self, limit: int = 50) -> List[LogEntry]:
        return self.logs[-limit:]
        
    def get_recent_deployments(self, limit: int = 5) -> List[DeploymentEvent]:
        return self.deployments[-limit:]
