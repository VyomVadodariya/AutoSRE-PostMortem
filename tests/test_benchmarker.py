from evaluation.benchmarker import Benchmarker
from environment.chaos.injector import ChaosInjector
from environment.chaos.evaluator import ChaosEvaluator
from environment.incidents.generator import IncidentGenerator
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

def test_benchmarker():
    # Setup dependencies
    generator = IncidentGenerator()
    injector = ChaosInjector(generator)
    evaluator = ChaosEvaluator()
    
    metrics = MetricsStore()
    graph = DependencyGraph()
    
    from agents.remediation.what_if import WhatIfEngine
    from environment.observability.signals import SignalStore
    from environment.simulation import SimulationEnvironment
    
    env = SimulationEnvironment(metrics, SignalStore())
    
    registry = ToolRegistry()
    registry.register(RestartServiceTool(env))
    registry.register(TerminateProcessTool(env))
    
    whatif = WhatIfEngine(registry, env)
    
    # Setup Orchestrator (Simulated AutoSRE Agent)
    orchestrator = Orchestrator(
        InvestigationAgent(None, metrics),
        RCAAgent(RCAEngine(graph)),
        PlanningAgent(whatif),
        RemediationEngine(registry, metrics),
        PostmortemAgent()
    )
    
    benchmarker = Benchmarker(injector, evaluator)
    
    # Run Benchmark
    scenarios = ["cpu_failure", "database_failure", "adversarial_cpu"]
    result = benchmarker.run_benchmark("AutoSRE_v2", orchestrator, scenarios, iterations=1)
    
    assert result.agent_name == "AutoSRE_v2"
    assert result.runs == 3
    # Our mocked agents always succeed in simulation
    assert result.recovery_success_rate == 1.0
    assert result.token_usage_total == 0
    assert result.cost_estimate_usd == 0.0
    
    report = benchmarker.generate_report([result])
    assert "AutoSRE_v2" in report
    assert "RCA" in report
    assert "MTTR" in report
