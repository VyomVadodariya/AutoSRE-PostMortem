from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from environment.incidents.models import Incident
from rca.engine import RCA_Result


class PostmortemAgent:
    def generate(self, incident: Incident, rca_result: RCA_Result, remediation_results: list[Any], 
                 timestamps: dict[str, float] | None = None) -> str:
        
        timestamps = timestamps or {}
        start = timestamps.get("start_time", incident.timestamp.timestamp())
        detected = timestamps.get("detected_time")
        acknowledged = timestamps.get("acknowledged_time")
        recovered = timestamps.get("recovered_time")
        
        def safe_time_diff(end, start_val):
            return int(end - start_val) if end and start_val else "N/A"
            
        mttd = safe_time_diff(detected, start)
        mtta = safe_time_diff(acknowledged, detected) if detected else "N/A"
        mttr = safe_time_diff(recovered, start)
        recovery_time = mttr if mttr != "N/A" else 0
        
        start_time_str = datetime.fromtimestamp(start, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        
        successful_actions = [r for r in remediation_results if r.verification_status == "SUCCESS"]
        failed_actions = [r for r in remediation_results if r.verification_status != "SUCCESS"]
        
        impact_per_min = float(os.environ.get("BUSINESS_IMPACT_PER_MINUTE", "1400.0"))
        business_impact = f"${(recovery_time / 60.0) * impact_per_min:.2f} (Estimated using configured simulation assumptions)"
        
        report = f"# INCIDENT POSTMORTEM: {incident.incident_id}\n\n"
        
        report += f"**Severity**: {incident.severity.value}\n"
        report += f"**Start Time**: {start_time_str}\n"
        report += f"**Detection Time**: +{mttd}s\n"
        report += f"**Acknowledgement Time**: +{mtta}s\n"
        report += f"**Recovery Time**: {recovery_time}s\n"
        report += f"**MTTD**: {mttd}s | **MTTA**: {mtta}s | **MTTR**: {mttr}s\n\n"
        
        report += f"**Services Affected**: {', '.join(incident.services_affected)}\n\n"
        
        report += "## Executive Summary\n"
        report += f"An incident of {incident.severity.value} severity occurred affecting {', '.join(incident.services_affected)}. "
        report += f"The root cause was identified as '{rca_result.root_cause}'. Service was restored after {len(remediation_results)} remediation action(s).\n\n"
        
        report += "## Impact\n"
        report += f"{rca_result.impact}\n"
        report += f"**Estimated Business Impact**: {business_impact}\n\n"
        
        report += "## Root Cause\n"
        report += f"{rca_result.root_cause}\n\n"
        
        report += "## Contributing Factors\n"
        for factor in rca_result.contributing_factors:
            report += f"- {factor}\n"
        if not rca_result.contributing_factors:
            report += "- None identified\n"
        report += "\n"
        
        report += "## Evidence\n"
        for ev in rca_result.evidence:
            report += f"- [{ev.source}] {ev.description} (Contribution: {ev.confidence_contribution})\n"
        if not rca_result.evidence:
            report += "- No concrete evidence collected.\n"
        report += "\n"
        
        report += "## Actions Taken\n"
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
        
        # Dynamically generate lessons based on RCA
        report += "## Lessons Learned\n"
        if "cpu" in rca_result.root_cause.lower():
            report += "- Monitor CPU limits more aggressively.\n"
        elif "connection" in rca_result.root_cause.lower():
            report += "- Add PgBouncer or connection limits.\n"
        else:
            report += "- Review dependencies and risk levels for automated remediation.\n\n"
        
        report += "## Preventive Actions\n"
        report += "- Update alerting thresholds.\n"
        
        return report
