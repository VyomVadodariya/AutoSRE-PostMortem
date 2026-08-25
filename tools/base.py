from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from policies.risk.levels import RiskLevel

class ToolResult(BaseModel):
    success: bool
    output: str
    data: Optional[Dict[str, Any]] = None

class BaseTool:
    name: str = ""
    description: str = ""
    parameters: Dict[str, Any] = {}
    risk_level: RiskLevel = RiskLevel.LOW
    permissions: List[str] = []

    def validate(self, **kwargs) -> bool:
        """Validate input parameters."""
        return True

    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool logic. Override in subclasses."""
        raise NotImplementedError()
