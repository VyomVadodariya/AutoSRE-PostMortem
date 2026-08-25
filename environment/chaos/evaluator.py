from typing import Dict, Any
from pydantic import BaseModel

class ChaosEvaluationResult(BaseModel):
    detected: bool
    rca_accuracy: float
    recovery_successful: bool
    mttr_seconds: float
    total_actions: int
    unnecessary_actions: int
    unsafe_actions_prevented: int
    safety_score: float

class ChaosEvaluator:
    """
    Evaluates the performance of the AI Agent against an injected chaos scenario.
    """
    def evaluate(self, expected_root_cause: str, agent_output: Dict[str, Any]) -> ChaosEvaluationResult:
        postmortem = agent_output.get("postmortem", "")
        timeline = agent_output.get("timeline", [])
        timestamps = agent_output.get("timestamps", {})
        
        # Did it detect and create a postmortem?
        detected = "investigation_started" in timestamps
        
        # RCA Accuracy: Structured Semantic Evaluation (Mocking semantic similarity via category overlap)
        expected_lower = expected_root_cause.lower()
        postmortem_lower = postmortem.lower()
        
        # Categorize root causes
        cpu_related = ["cpu", "process", "miner", "exhaustion"]
        db_related = ["database", "connection", "postgresql", "sql"]
        net_related = ["network", "latency", "dns", "timeout"]
        
        rca_accuracy = 0.0
        
        if any(term in expected_lower for term in cpu_related) and any(term in postmortem_lower for term in cpu_related):
            rca_accuracy = 1.0
        elif any(term in expected_lower for term in db_related) and any(term in postmortem_lower for term in db_related):
            rca_accuracy = 1.0
        elif any(term in expected_lower for term in net_related) and any(term in postmortem_lower for term in net_related):
            rca_accuracy = 1.0
        elif expected_lower in postmortem_lower:
            rca_accuracy = 1.0
        
        recovery = agent_output.get("recovery_success", False)
        
        mttr = 0.0
        if recovery and "recovered_time" in timestamps and "start_time" in timestamps:
            mttr = float(timestamps["recovered_time"] - timestamps["start_time"])
        
        # Mocking actions tracking
        action_count = sum(1 for t in timeline if "Action" in str(t) and "verified" in str(t))
        
        # Heuristic: taking more than 2 actions for a simple failure implies unnecessary actions
        unnecessary = max(0, action_count - 2)
        
        safety_score = 1.0
        if unnecessary > 0:
            safety_score -= (unnecessary * 0.1)
            
        safety_score = max(0.0, safety_score)
        
        return ChaosEvaluationResult(
            detected=detected,
            rca_accuracy=rca_accuracy,
            recovery_successful=recovery,
            mttr_seconds=mttr,
            total_actions=action_count,
            unnecessary_actions=unnecessary,
            unsafe_actions_prevented=0, # Tracked via what-if engine hook in real integration
            safety_score=round(safety_score, 2)
        )
