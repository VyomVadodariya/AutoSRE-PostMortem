import argparse
import csv
import json
import os
from datetime import datetime, timezone

from agents.baselines import RandomBaselineAgent, RuleBasedBaselineAgent
from agents.investigation.agent import InvestigationAgent
from agents.orchestrator.orchestrator import Orchestrator
from agents.planning.agent import PlanningAgent
from agents.postmortem.agent import PostmortemAgent
from agents.rca.agent import RCAAgent
from agents.remediation.engine import RemediationEngine
from environment.chaos.evaluator import ChaosEvaluator
from environment.chaos.injector import ChaosInjector
from environment.incidents.generator import IncidentGenerator
from environment.observability.metrics import MetricsStore
from environment.observability.signals import SignalStore
from environment.simulation import SimulationEnvironment
from evaluation.benchmarker import Benchmarker
from memory.incidents.store import IncidentMemoryStore
from rca.dependency_graph.graph import DependencyGraph
from rca.engine import RCAEngine
from tools.implementations import RestartServiceTool, TerminateProcessTool
from tools.registry import ToolRegistry


def get_version_info():
    return {"version": "1.0.0", "commit": "unknown"}

def main():
    parser = argparse.ArgumentParser(description="Run AutoSRE Benchmarks")
    parser.add_argument("--episodes", type=int, default=50, help="Total number of episodes to run")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--out-dir", type=str, default="results", help="Directory to save benchmark results")
    args = parser.parse_args()
    
    print(f"Initializing AutoSRE Benchmarking Suite (Seed: {args.seed})...")
    
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
    
    random_baseline = RandomBaselineAgent(registry)
    rule_baseline = RuleBasedBaselineAgent(registry)
    
    generator = IncidentGenerator()
    injector = ChaosInjector(generator, env)
    evaluator = ChaosEvaluator()
    benchmarker = Benchmarker(injector, evaluator)
    
    # 4. Run Benchmark
    scenarios = ["cpu_failure", "adversarial_cpu", "network_latency", "database_failure"]
    iterations = max(1, args.episodes // len(scenarios))
    total_episodes = len(scenarios) * iterations
    
    print(f"Running benchmark with {len(scenarios)} scenarios, {iterations} iterations each (Total: {total_episodes} incidents).")
    
    agents = [random_baseline, rule_baseline, orchestrator]
    all_results = []
    
    for agent in agents:
        print(f"Evaluating {agent.name}...")
        res = benchmarker.run_benchmark(agent, scenarios, iterations=iterations, seed=args.seed)
        all_results.append(res)
        
    report = benchmarker.generate_report(all_results)
    print("\n" + report)
    
    # Export results
    os.makedirs(args.out_dir, exist_ok=True)
    
    meta_info = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": args.seed,
        "episodes": total_episodes,
        "scenarios": scenarios,
        "version": get_version_info(),
        "results": [r.model_dump() for r in all_results]
    }
    
    json_path = os.path.join(args.out_dir, "benchmark.json")
    with open(json_path, "w") as f:
        json.dump(meta_info, f, indent=2)
        
    csv_path = os.path.join(args.out_dir, "benchmark.csv")
    with open(csv_path, "w", newline="") as f:
        if all_results:
            writer = csv.DictWriter(f, fieldnames=all_results[0].model_dump().keys())
            writer.writeheader()
            for r in all_results:
                writer.writerow(r.model_dump())
                
    print(f"Saved machine-readable results to {args.out_dir}/")

if __name__ == "__main__":
    main()
