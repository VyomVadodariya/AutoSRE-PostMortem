import sys
import argparse
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
from environment.observability.signals import SignalStore
from environment.simulation import SimulationEnvironment
from memory.incidents.store import IncidentMemoryStore

def main():
    parser = argparse.ArgumentParser(description="Run AutoSRE Benchmarks")
    parser.add_argument("--episodes", type=int, default=50, help="Total number of episodes to run")
    args = parser.parse_args()
    
    print("Initializing AutoSRE Benchmarking Suite...")
    
    # 1. Setup Simulation Environment
    metrics_store = MetricsStore()
    signal_store = SignalStore()
    env = SimulationEnvironment(metrics_store, signal_store)
    
    # 2. Setup Tools
    registry = ToolRegistry()
    registry.register(RestartServiceTool(env))
    registry.register(TerminateProcessTool(env))
    
    # 3. Setup Agents
    graph = DependencyGraph()
    memory_store = IncidentMemoryStore()
    
    from agents.remediation.what_if import WhatIfEngine
    whatif = WhatIfEngine(registry, env)
    
    investigation_agent = InvestigationAgent(env.signals, env.metrics)
    rca_agent = RCAAgent(RCAEngine(graph), memory_store)
    planning_agent = PlanningAgent(whatif)
    remediation_engine = RemediationEngine(registry, env.metrics)
    postmortem_agent = PostmortemAgent()
    
    orchestrator = Orchestrator(
        investigation_agent,
        rca_agent,
        planning_agent,
        remediation_engine,
        postmortem_agent,
        memory_store
    )
    
    generator = IncidentGenerator()
    injector = ChaosInjector(generator, env)
    evaluator = ChaosEvaluator()
    benchmarker = Benchmarker(injector, evaluator)
    
    # 4. Run Benchmark
    scenarios = ["cpu_failure", "adversarial_cpu", "network_latency", "database_failure"]
    iterations = max(1, args.episodes // len(scenarios))
    
    print(f"Running benchmark with {len(scenarios)} scenarios, {iterations} iterations each (Total: {len(scenarios) * iterations} incidents).")
    print("This may take a moment to simulate state changes...\n")
    
    result = benchmarker.run_benchmark("AutoSRE_v3", orchestrator, scenarios, iterations=iterations)
    report = benchmarker.generate_report([result])
    
    print(report)

if __name__ == "__main__":
    main()
