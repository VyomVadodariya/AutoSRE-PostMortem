from pydantic import BaseModel
from typing import Dict, Any
from tools.registry import ToolRegistry
from environment.observability.metrics import MetricsStore
import time

class RemediationResult(BaseModel):
    action: str
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    verification_status: str
    confidence: float

class RemediationEngine:
    def __init__(self, tool_registry: ToolRegistry, metrics_store: MetricsStore):
        self.tool_registry = tool_registry
        self.metrics_store = metrics_store

    def execute_and_verify(self, tool_name: str, parameters: Dict[str, Any]) -> RemediationResult:
        # Collect state before remediation
        before_state = self.metrics_store.get_all_latest()
        
        # Execute tool
        kwargs = parameters.copy()
        kwargs["_metrics_store"] = self.metrics_store
        tool_result = self.tool_registry.execute_tool(tool_name, **kwargs)
        
        # In a real environment, we'd wait for the system to stabilize.
        # time.sleep(1)
        
        # Collect state after remediation
        after_state = self.metrics_store.get_all_latest()
        
        # Compute verification status based on actual state changes
        if not tool_result.success:
            status = "FAILED"
            confidence = 0.95
        else:
            # Check if any anomalous metric in before_state was resolved in after_state
            resolved = False
            for k, v in before_state.items():
                if v > 80.0 and after_state.get(k, 0.0) < 80.0:
                    resolved = True
            
            # If we didn't have anomalous metrics, or they were resolved
            if resolved or not any(v > 80.0 for v in before_state.values()):
                status = "SUCCESS"
                confidence = 0.95
            else:
                status = "FAILED"
                confidence = 0.85
            
        return RemediationResult(
            action=tool_name,
            before_state=before_state,
            after_state=after_state,
            verification_status=status,
            confidence=confidence
        )
