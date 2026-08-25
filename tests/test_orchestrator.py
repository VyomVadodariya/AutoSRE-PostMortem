from agents.orchestrator.orchestrator import Orchestrator
from agents.investigation.agent import InvestigationAgent
from agents.rca.agent import RCAAgent
from agents.planning.agent import PlanningAgent
from agents.postmortem.agent import PostmortemAgent
from agents.remediation.engine import RemediationEngine
from tools.registry import ToolRegistry
from tools.implementations import RestartServiceTool, TerminateProcessTool
from rca.dependency_graph.graph import DependencyGraph
from rca.engine import RCAEngine
from environment.observability.metrics import MetricsStore
from environment.incidents.generator import IncidentGenerator

def test_orchestrator_full_flow():
    # Setup Tools
    registry = ToolRegistry()
    registry.register(RestartServiceTool())
    registry.register(TerminateProcessTool())
    
    # Setup Environment/Signals
    metrics = MetricsStore()
    graph = DependencyGraph()
    graph.add_service("nginx")
    
    # Setup Sub-Agents
    investigation = InvestigationAgent(None, metrics)
    rca = RCAAgent(RCAEngine(graph))
    planning = PlanningAgent()
    remediation = RemediationEngine(registry, metrics)
    postmortem = PostmortemAgent()
    
    # Setup Orchestrator
    orchestrator = Orchestrator(
        investigation,
        rca,
        planning,
        remediation,
        postmortem
    )
    
    # Generate Incident
    generator = IncidentGenerator()
    incident = generator.generate_incident(category="infrastructure")
    
    # Run Flow
    result = orchestrator.handle_incident(incident)
    
    assert result["incident_id"] == incident.incident_id
    assert result["recovery_success"] is True
    assert "Postmortem generated." in result["timeline"]
    assert "INCIDENT POSTMORTEM" in result["postmortem"]
