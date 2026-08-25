from typing import List, Dict, Any, Optional
from environment.incidents.models import Incident
from pydantic import BaseModel

class ActionPlan(BaseModel):
    actions: List[Dict[str, Any]] # e.g. [{"tool_name": "restart_service", "parameters": {"service_name": "nginx"}}]

class Orchestrator:
    """
    Coordinates the workflow of the SRE AI Agents.
    """
    def __init__(self, investigation_agent, rca_agent, planning_agent, remediation_engine, postmortem_agent):
        self.investigation_agent = investigation_agent
        self.rca_agent = rca_agent
        self.planning_agent = planning_agent
        self.remediation_engine = remediation_engine
        self.postmortem_agent = postmortem_agent
        self.timeline: List[str] = []
        
    def handle_incident(self, incident: Incident) -> Dict[str, Any]:
        self.timeline.append(f"Incident {incident.incident_id} detected.")
        
        # 1. Investigate
        self.timeline.append("Investigation started.")
        evidence = self.investigation_agent.investigate(incident)
        
        # 2. RCA
        self.timeline.append("Root Cause Analysis started.")
        rca_result = self.rca_agent.analyze(incident, evidence)
        self.timeline.append(f"Root cause identified: {rca_result.root_cause}")
        
        # 3. Plan
        self.timeline.append("Remediation planning started.")
        plan = self.planning_agent.create_plan(rca_result)
        
        # 4. Remediate & Verify
        self.timeline.append("Executing remediation plan.")
        remediation_results = []
        recovery_success = True
        
        for action in plan.actions:
            tool_name = action["tool_name"]
            params = action["parameters"]
            
            res = self.remediation_engine.execute_and_verify(tool_name, params)
            remediation_results.append(res)
            
            self.timeline.append(f"Action '{tool_name}' verified as {res.verification_status}")
            
            if res.verification_status != "SUCCESS":
                recovery_success = False
                break
                
        if recovery_success:
            self.timeline.append("Recovery verified. Service restored.")
        else:
            self.timeline.append("Recovery failed. Further investigation required.")
            
        # 5. Postmortem
        report = self.postmortem_agent.generate(incident, rca_result, remediation_results)
        self.timeline.append("Postmortem generated.")
        
        return {
            "incident_id": incident.incident_id,
            "recovery_success": recovery_success,
            "timeline": self.timeline,
            "postmortem": report
        }
