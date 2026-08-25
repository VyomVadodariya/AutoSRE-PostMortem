from typing import List, Dict, Any, Optional
from environment.incidents.models import Incident
from pydantic import BaseModel
import time

class ActionPlan(BaseModel):
    actions: List[Dict[str, Any]]

class Orchestrator:
    def __init__(self, investigation_agent, rca_agent, planning_agent, remediation_engine, postmortem_agent):
        self.investigation_agent = investigation_agent
        self.rca_agent = rca_agent
        self.planning_agent = planning_agent
        self.remediation_engine = remediation_engine
        self.postmortem_agent = postmortem_agent
        self.timeline: List[str] = []
        
    def handle_incident(self, incident: Incident) -> Dict[str, Any]:
        timestamps = {}
        # Use actual incident injection time
        timestamps["incident_created"] = incident.timestamp.timestamp()
        timestamps["start_time"] = timestamps["incident_created"]
        
        self.timeline.append(f"Incident {incident.incident_id} detected.")
        timestamps["anomaly_detected"] = time.time()
        timestamps["detected_time"] = timestamps["anomaly_detected"]
        
        # 1. Investigate
        self.timeline.append("Investigation started.")
        timestamps["investigation_started"] = time.time()
        evidence = self.investigation_agent.investigate(incident)
        if hasattr(self.investigation_agent, 'timeline'):
            self.timeline.extend(self.investigation_agent.timeline)
        timestamps["acknowledged_time"] = time.time()
        
        # 2. RCA
        self.timeline.append("Root Cause Analysis started.")
        timestamps["rca_started"] = time.time()
        rca_result = self.rca_agent.analyze(incident, evidence)
        timestamps["rca_completed"] = time.time()
        self.timeline.append(f"Root cause identified: {rca_result.root_cause}")
        
        # 3. Plan
        self.timeline.append("Remediation planning started.")
        timestamps["plan_created"] = time.time()
        plan = self.planning_agent.create_plan(rca_result)
        if hasattr(self.planning_agent, 'timeline'):
            self.timeline.extend(self.planning_agent.timeline)
        
        # 4. Remediate & Verify
        self.timeline.append("Executing remediation plan.")
        timestamps["remediation_started"] = time.time()
        remediation_results = []
        recovery_success = True
        
        for action in plan.actions:
            tool_name = action["tool_name"]
            params = action.get("parameters", {})
            
            res = self.remediation_engine.execute_and_verify(tool_name, params)
            remediation_results.append(res)
            
            self.timeline.append(f"Action '{tool_name}' verified as {res.verification_status}")
            
            if res.verification_status != "SUCCESS":
                recovery_success = False
                break
                
        timestamps["remediation_completed"] = time.time()
        timestamps["verification_started"] = time.time()
        
        if recovery_success:
            self.timeline.append("Recovery verified. Service restored.")
            timestamps["recovery_verified"] = time.time()
            timestamps["recovered_time"] = timestamps["recovery_verified"]
        else:
            self.timeline.append("Recovery failed. Further investigation required.")
            timestamps["recovered_time"] = None
            
        # 5. Postmortem
        report = self.postmortem_agent.generate(incident, rca_result, remediation_results, timestamps)
        timestamps["postmortem_generated"] = time.time()
        self.timeline.append("Postmortem generated.")
        
        return {
            "incident_id": incident.incident_id,
            "recovery_success": recovery_success,
            "timeline": self.timeline,
            "postmortem": report,
            "timestamps": timestamps,
            "tokens_used": "N/A",
            "cost": "N/A"
        }
