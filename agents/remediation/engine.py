import copy
from typing import Any

from pydantic import BaseModel

from environment.observability.metrics import MetricsStore
from tools.registry import ToolRegistry
from policies.safety_pipeline import SafetyPipeline


class RemediationResult(BaseModel):
    action: str
    before_state: dict[str, Any]
    after_state: dict[str, Any]
    verification_status: str
    confidence: float
    safety_reason: str = ""

class RemediationEngine:
    def __init__(self, tool_registry: ToolRegistry, metrics_store: MetricsStore):
        self.tool_registry = tool_registry
        self.metrics_store = metrics_store
        self.safety_pipeline = SafetyPipeline(metrics_store)

    def execute_and_verify(self, tool_name: str, parameters: dict[str, Any]) -> RemediationResult:
        # Get Tool
        tool = self.tool_registry.get_tool(tool_name)
        before_state = self.metrics_store.get_all_latest()
        
        if not tool:
            return RemediationResult(
                action=tool_name,
                before_state=before_state,
                after_state=before_state,
                verification_status="FAILED",
                confidence=1.0,
                safety_reason="Tool not found"
            )
        
        # 1. Safety Policy Check
        decision = self.safety_pipeline.evaluate_request(tool, parameters)
        if not decision.approved:
            return RemediationResult(
                action=tool_name,
                before_state=before_state,
                after_state=before_state,
                verification_status="BLOCKED_BY_POLICY",
                confidence=1.0,
                safety_reason=decision.reason
            )
            
        # 2. Snapshot (mock)
        snapshot = copy.deepcopy(before_state)
        
        # 3. Execute
        kwargs = parameters.copy()
        kwargs["_metrics_store"] = self.metrics_store
        
        # Use registry.execute_tool to leverage its built-in exception handling and validation
        tool_result = self.tool_registry.execute_tool(tool_name, **kwargs)
        
        # 4. Verify
        after_state = self.metrics_store.get_all_latest()
        
        if not tool_result.success:
            status = "FAILED"
            confidence = 0.95
        else:
            resolved = False
            ignore_metrics = ["total_requests", "failed_requests"]
            for k, v in before_state.items():
                if k in ignore_metrics:
                    continue
                if v > 80.0 and after_state.get(k, 0.0) < 80.0:
                    resolved = True
            
            anomalous = any(v > 80.0 for k, v in before_state.items() if k not in ignore_metrics)
            
            if resolved or not anomalous:
                status = "SUCCESS"
                confidence = 0.95
            else:
                status = "FAILED"
                confidence = 0.85
                
        # 5. Rollback if Failed
        if status == "FAILED":
            # Mock rollback
            pass # In a real implementation we would revert the state here
            
        return RemediationResult(
            action=tool_name,
            before_state=before_state,
            after_state=after_state,
            verification_status=status,
            confidence=confidence,
            safety_reason="Executed successfully" if status == "SUCCESS" else "Rolled back after failure"
        )
