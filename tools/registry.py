from __future__ import annotations

from tools.base import BaseTool, ToolResult


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, output=f"Tool '{name}' not found in registry.")
            
        if not tool.validate(**kwargs):
            return ToolResult(success=False, output=f"Validation failed for tool '{name}'.")
            
        try:
            return tool.execute(**kwargs)
        except Exception as e: # noqa: BLE001
            return ToolResult(success=False, output=f"Tool '{name}' execution error: {e!s}")
