from typing import Dict, Any, Optional
from tools.base import BaseTool, ToolResult

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        tool = self.get_tool(name)
        if not tool:
            return ToolResult(success=False, output=f"Tool '{name}' not found in registry.")
            
        if not tool.validate(**kwargs):
            return ToolResult(success=False, output=f"Validation failed for tool '{name}'.")
            
        try:
            return tool.execute(**kwargs)
        except Exception as e:
            return ToolResult(success=False, output=f"Tool '{name}' execution error: {str(e)}")
