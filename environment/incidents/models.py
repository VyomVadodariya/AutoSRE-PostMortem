from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class IncidentSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class IncidentClass(str, Enum):
    INFRASTRUCTURE = "INFRASTRUCTURE"
    NETWORK = "NETWORK"
    APPLICATION = "APPLICATION"
    DATABASE = "DATABASE"
    SECURITY = "SECURITY"

class Incident(BaseModel):
    incident_id: str
    timestamp: datetime
    incident_class: IncidentClass
    severity: IncidentSeverity
    services_affected: List[str]
    symptoms: List[str]
    root_cause: str
    contributing_factors: List[str] = Field(default_factory=list)
    
    # State snapshots (simulated initial data state)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    logs: List[str] = Field(default_factory=list)
    network_state: Dict[str, Any] = Field(default_factory=dict)
    deployment_state: Dict[str, Any] = Field(default_factory=dict)
    
    expected_impact: str
    available_remediations: List[str]
    difficulty: int = Field(default=1, ge=1, le=7)
