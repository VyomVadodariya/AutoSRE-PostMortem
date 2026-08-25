from pydantic import BaseModel, Field
from typing import List, Dict

class DatabaseState(BaseModel):
    status: str = "healthy"
    max_connections: int = 1000
    active_connections: int = 45
    connection_leaks: int = 0
    query_latency: float = 10.0
    health: float = 1.0

class ServiceState(BaseModel):
    name: str
    status: str = "running"
    version: str = "1.0.0"
    restart_count: int = 0
    health: float = 1.0
    dependencies: List[str] = Field(default_factory=list)
    resource_usage: Dict[str, float] = Field(default_factory=dict)
