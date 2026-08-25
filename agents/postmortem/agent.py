from environment.incidents.models import Incident
from rca.engine import RCA_Result
from typing import List, Any
from datetime import datetime, timezone

class PostmortemAgent:
    """
    Generates a highly detailed, markdown-formatted incident postmortem report
    following industry SRE standards.
    """
    def generate(self, incident: Incident, rca_result: RCA_Result, remediation_results: List[Any], 
                 mttd: int = 15, mtta: int = 5) -> str:
        
        # Calculate mock recovery time (in a real system, calculate difference between start and end timestamps)
        recovery_time = len(remediation_results) * 12 # 12 seconds per action simulated
        mttr = recovery_time
        
        start_time_str = incident.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        
        successful_actions = [r for r in remediation_results if r.verification_status == "SUCCESS"]
        failed_actions = [r for r in remediation_results if r.verification_status != "SUCCESS"]
        
        # Business impact calculation (simulated estimate)
        business_impact = f"${(recovery_time / 60.0) * 1400:.2f} (Estimated)"
        
        report = f"# INCIDENT POSTMORTEM: {incident.incident_id}\n\n"
        
        report += f"**Severity**: {incident.severity.value}\n"
        report += f"**Start Time**: {start_time_str}\n"
        report += f"**Detection Time**: +{mttd}s\n"
        report += f"**Acknowledgement Time**: +{mtta}s\n"
        report += f"**Recovery Time**: {recovery_time}s\n"
        report += f"**MTTD**: {mttd}s | **MTTA**: {mtta}s | **MTTR**: {mttr}s\n\n"
        
        report += f"**Services Affected**: {', '.join(incident.services_affected)}\n\n"
        
        report += f"## Executive Summary\n"
        report += f"An incident of {incident.severity.value} severity occurred affecting {', '.join(incident.services_affected)}. "
        report += f"The root cause was identified as '{rca_result.root_cause}'. Service was restored after {len(remediation_results)} remediation action(s).\n\n"
        
        report += f"## Impact\n"
        report += f"{rca_result.impact}\n"
        report += f"**Estimated Business Impact**: {business_impact}\n\n"
        
        report += f"## Root Cause\n"
        report += f"{rca_result.root_cause}\n\n"
        
        report += f"## Contributing Factors\n"
        for factor in rca_result.contributing_factors:
            report += f"- {factor}\n"
        if not rca_result.contributing_factors:
            report += "- None identified\n"
        report += "\n"
        
        report += f"## Evidence\n"
        for ev in rca_result.evidence:
            report += f"- [{ev.source}] {ev.description} (Contribution: {ev.confidence_contribution})\n"
        if not rca_result.evidence:
            report += "- No concrete evidence collected.\n"
        report += "\n"
        
        report += f"## Actions Taken\n"
        report += "### Successful Actions\n"
        for r in successful_actions:
            report += f"- Executed `{r.action}`\n"
        if not successful_actions:
            report += "- None\n"
            
        report += "\n### Failed Actions\n"
        for r in failed_actions:
            report += f"- Executed `{r.action}` (Failed Verification)\n"
        if not failed_actions:
            report += "- None\n"
        report += "\n"
        
        report += f"## Lessons Learned\n"
        report += "- Ensure prompt detection of similar resource exhaustion.\n"
        report += "- Review dependencies and risk levels for automated remediation.\n\n"
        
        report += f"## Preventive Actions\n"
        report += "- Add stricter resource limits to affected containers.\n"
        report += "- Improve anomaly detection baseline for this service.\n"
        
        return report
