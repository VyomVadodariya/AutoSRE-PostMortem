from pydantic import BaseModel, Field, PrivateAttr
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
    root_cause: str # We keep the field name for pydantic loading but agents MUST NOT use it directly
    contributing_factors: List[str] = Field(default_factory=list)
    
    expected_impact: str
    available_remediations: List[str]
    difficulty: int = Field(default=1, ge=1, le=7)
    
    _hidden_root_cause: str = PrivateAttr(default="")
    
    def __init__(self, **data):
        super().__init__(**data)
        if "root_cause" in data:
            self._hidden_root_cause = data["root_cause"]
