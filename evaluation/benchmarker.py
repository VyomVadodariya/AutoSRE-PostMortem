from pydantic import BaseModel
from typing import List, Dict, Any
from environment.chaos.injector import ChaosInjector
from environment.chaos.evaluator import ChaosEvaluator
from agents.orchestrator.orchestrator import Orchestrator

class BenchmarkResult(BaseModel):
    agent_name: str
    runs: int
    rca_accuracy_avg: float
    recovery_success_rate: float
    mttr_avg: float
    actions_avg: float
    unnecessary_actions_avg: float
    safety_score_avg: float
    token_usage_total: int
    cost_estimate_usd: float

class Benchmarker:
    def __init__(self, injector: ChaosInjector, evaluator: ChaosEvaluator):
        self.injector = injector
        self.evaluator = evaluator
        
    def run_benchmark(self, agent_name: str, orchestrator: Orchestrator, scenarios: List[str], iterations: int = 1) -> BenchmarkResult:
        results = []
        token_usage_total = 0
        cost_total = 0.0
        
        for scenario in scenarios:
            for _ in range(iterations):
                # 1. Inject Chaos
                incident = self.injector.inject_chaos(scenario)
                hidden_truth = incident._hidden_root_cause
                
                # 2. Run Orchestrator
                # We extract real tokens if the agent returns it.
                agent_output = orchestrator.handle_incident(incident)
                tokens = agent_output.get("tokens_used", 0) 
                
                # 3. Evaluate against hidden truth
                eval_result = self.evaluator.evaluate(hidden_truth, agent_output)
                results.append(eval_result)
                
                token_usage_total += tokens
                cost_total += (tokens / 1000.0) * 0.002
                
        runs = len(results)
        if runs == 0:
            return BenchmarkResult(
                agent_name=agent_name, runs=0, rca_accuracy_avg=0.0, recovery_success_rate=0.0,
                mttr_avg=0.0, actions_avg=0.0, unnecessary_actions_avg=0.0, safety_score_avg=0.0,
                token_usage_total=0, cost_estimate_usd=0.0
            )
            
        rca_acc = sum(r.rca_accuracy for r in results) / runs
        rec_succ = sum(1.0 for r in results if r.recovery_successful) / runs
        mttr = sum(r.mttr_seconds for r in results) / runs
        actions = sum(r.total_actions for r in results) / runs
        unnecessary = sum(r.unnecessary_actions for r in results) / runs
        safety = sum(r.safety_score for r in results) / runs
        
        return BenchmarkResult(
            agent_name=agent_name,
            runs=runs,
            rca_accuracy_avg=round(rca_acc, 2),
            recovery_success_rate=round(rec_succ, 2),
            mttr_avg=round(mttr, 1),
            actions_avg=round(actions, 1),
            unnecessary_actions_avg=round(unnecessary, 1),
            safety_score_avg=round(safety, 2),
            token_usage_total=token_usage_total,
            cost_estimate_usd=round(cost_total, 4)
        )
        
    def generate_report(self, benchmarks: List[BenchmarkResult]) -> str:
        report = f"{'Agent':<16} {'RCA':<7} {'MTTR':<7} {'Actions':<10} {'Safety':<9} {'Cost':<6}\n"
        report += "-" * 60 + "\n"
        for b in benchmarks:
            rca_pct = f"{int(b.rca_accuracy_avg * 100)}%"
            safety_pct = f"{int(b.safety_score_avg * 100)}%"
            mttr_str = f"{b.mttr_avg}s"
            report += f"{b.agent_name:<16} {rca_pct:<7} {mttr_str:<7} {b.actions_avg:<10} {safety_pct:<9} ${b.cost_estimate_usd:<6.4f}\n"
        return report
