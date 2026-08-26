from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from policies.risk.levels import RiskLevel


class ToolResult(BaseModel):
    success: bool
    output: str
    data: dict[str, Any] | None = None

class BaseTool:
    name: str = ""
    description: str = ""
    parameters: dict[str, Any] = {}
    risk_level: RiskLevel = RiskLevel.LOW
    permissions: list[str] = []

    def validate(self, **kwargs) -> bool:
        """Validate input parameters."""
        return True

    def execute(self, **kwargs) -> ToolResult:
        """Execute the tool logic. Override in subclasses."""
        raise NotImplementedError()
