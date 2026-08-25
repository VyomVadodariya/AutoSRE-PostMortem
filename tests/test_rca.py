import time
from rca.dependency_graph.graph import DependencyGraph
from rca.engine import RCAEngine
from environment.incidents.models import Incident, IncidentClass, IncidentSeverity
from rca.correlation.evidence import Evidence
from datetime import datetime, timezone

def test_dependency_graph():
    graph = DependencyGraph()
    # Users -> Load Balancer -> Nginx -> API -> PostgreSQL
    graph.add_service("PostgreSQL", is_database=True)
    graph.add_service("API", dependencies=["PostgreSQL"])
    graph.add_service("Nginx", dependencies=["API"])
    graph.add_service("Load Balancer", dependencies=["Nginx"])
    
    # If API fails, who is impacted?
    impacted = graph.get_downstream_impact("API")
    # Both Nginx and Load Balancer depend on it (directly or indirectly)
    assert "Nginx" in impacted
    assert "Load Balancer" in impacted
    assert "PostgreSQL" not in impacted
    
    # What does Load Balancer depend on?
    deps = graph.get_upstream_dependencies("Load Balancer")
    assert "Nginx" in deps
    assert "API" in deps
    assert "PostgreSQL" in deps

def test_rca_engine():
    graph = DependencyGraph()
    graph.add_service("Worker", dependencies=["Redis"])
    graph.add_service("Queue", dependencies=["Worker"])
    
    engine = RCAEngine(dependency_graph=graph)
    
    incident = Incident(
        incident_id="INC-001",
        timestamp=datetime.now(timezone.utc),
        incident_class=IncidentClass.APPLICATION,
        severity=IncidentSeverity.HIGH,
        services_affected=["Redis"],
        symptoms=["Worker timeout"],
        root_cause="Redis memory exhausted",
        expected_impact="Queue will stop processing",
        available_remediations=[]
    )
    
    evidence = [
        Evidence(source="metrics", description="Redis memory hit 100%", timestamp=time.time())
    ]
    
    result = engine.generate_rca(incident, evidence, deduced_cause="Memory leak in Redis")
    
    # Redis failure affects Worker, which affects Queue
    assert "Worker" in result.impact
    assert "Queue" in result.impact
    assert result.root_cause == "Memory leak in Redis"
    assert result.confidence == 0.65  # 0.5 + (1 * 0.15)
