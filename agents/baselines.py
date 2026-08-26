import random
import time
from typing import Any

from agents.base import BaseAgent
from environment.incidents.models import Incident
from tools.registry import ToolRegistry


class RandomBaselineAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "RandomBaseline"

    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self.timeline = []

    def handle_incident(self, incident: Incident) -> dict[str, Any]:
        start = time.time()
        self.timeline = [f"Incident {incident.incident_id} started."]
        
        # Pick a random number of actions 1-3
        num_actions = random.randint(1, 3)
        available_tools = list(self.registry._tools.values())
        
        for _ in range(num_actions):
            if available_tools:
                tool = random.choice(available_tools)
                # Naively supply random parameters if required
                params = {}
                if "service_name" in tool.parameters:
                    params["service_name"] = random.choice(incident.services_affected) if incident.services_affected else "nginx"
                if "pid" in tool.parameters:
                    params["pid"] = random.randint(100, 9999)
                    
                tool.execute(**params)
                self.timeline.append(f"Randomly executed {tool.name}")
                
        end = time.time()
        
        return {
            "incident_id": incident.incident_id,
            "recovery_success": random.choice([True, False]), # Random baseline doesn't actually know if it succeeded
            "timeline": self.timeline,
            "postmortem": "Random baseline postmortem.",
            "timestamps": {
                "start_time": start,
                "recovered_time": end if random.choice([True, False]) else None
            },
            "tokens_used": 0,
            "cost": 0.0
        }


class RuleBasedBaselineAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "RuleBasedBaseline"

    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self.timeline = []

    def handle_incident(self, incident: Incident) -> dict[str, Any]:
        start = time.time()
        self.timeline = [f"Incident {incident.incident_id} started."]
        recovery_success = False
        
        # Simple rules mapping keywords to actions
        rules = {
            "cpu": ("restart_service", "service_name"),
            "memory": ("restart_service", "service_name"),
            "process": ("kill_process", "pid"),
            "miner": ("kill_process", "pid"),
        }
        
        symptoms_text = " ".join(incident.symptoms).lower()
        root_cause_text = (incident.root_cause or "").lower()
        
        target_tool = None
        target_param = None
        for keyword, action in rules.items():
            if keyword in symptoms_text or keyword in root_cause_text:
                target_tool = action[0]
                target_param = action[1]
                break
                
        if not target_tool:
            # Fallback
            target_tool = "restart_service"
            target_param = "service_name"
            
        tool = self.registry.get_tool(target_tool)
        if tool:
            params = {}
            if target_param == "service_name":
                params["service_name"] = incident.services_affected[0] if incident.services_affected else "nginx"
            elif target_param == "pid":
                params["pid"] = 999  # Dummy pid
            
            tool.execute(**params)
            self.timeline.append(f"Rule match executed {tool.name}")
            recovery_success = True
        else:
            self.timeline.append(f"Required tool {target_tool} not available.")
            
        end = time.time()
        
        return {
            "incident_id": incident.incident_id,
            "recovery_success": recovery_success,
            "timeline": self.timeline,
            "postmortem": "Rule-based action completed.",
            "timestamps": {
                "start_time": start,
                "recovered_time": end if recovery_success else None
            },
            "tokens_used": 0,
            "cost": 0.0
        }
