from environment.incidents.models import Incident
from rca.engine import RCA_Result
from typing import List, Any

class PostmortemAgent:
    def generate(self, incident: Incident, rca_result: RCA_Result, remediation_results: List[Any]) -> str:
        report = f"""
# INCIDENT POSTMORTEM: {incident.incident_id}
**Severity**: {incident.severity.value}
**Impact**: {rca_result.impact}

## Root Cause
{rca_result.root_cause}

## Timeline & Actions Taken
"""
        for r in remediation_results:
            report += f"- Executed `{r.action}`: Result -> {r.verification_status}\n"
            
        return report
