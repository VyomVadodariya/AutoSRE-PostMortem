import random
import time

import numpy as np
from pydantic import BaseModel

from agents.base import BaseAgent
from environment.chaos.evaluator import ChaosEvaluator
from environment.chaos.injector import ChaosInjector


class BenchmarkResult(BaseModel):
    agent_name: str
    runs: int
    rca_accuracy_avg: float
    recovery_success_rate: float
    mttr_avg: float
    mttr_p50: float
    mttr_p95: float
    actions_avg: float
    unnecessary_actions_avg: float
    abstention_rate: float
    safety_score_avg: float
    token_usage_total: int
    cost_estimate_usd: float
    duration_seconds: float


class Benchmarker:
    def __init__(self, injector: ChaosInjector, evaluator: ChaosEvaluator):
        self.injector = injector
        self.evaluator = evaluator
        
    def run_benchmark(self, agent: BaseAgent, scenarios: list[str], iterations: int = 1, seed: int = 42) -> BenchmarkResult:
        random.seed(seed)
        np.random.seed(seed)
        
        results = []
        token_usage_total = 0
        cost_total = 0.0
        start_time = time.time()
        
        for scenario in scenarios:
            for _ in range(iterations):
                # 1. Inject Chaos
                incident = self.injector.inject_chaos(scenario)
                hidden_truth = incident._hidden_root_cause
                
                # 2. Run Agent
                # We extract real tokens if the agent returns it.
                agent_output = agent.handle_incident(incident)
                tokens = agent_output.get("tokens_used", 0) 
                if tokens == "N/A":
                    tokens = 0
                
                # 3. Evaluate against hidden truth
                eval_result = self.evaluator.evaluate(hidden_truth, agent_output)
                results.append(eval_result)
                
                token_usage_total += tokens
                cost_total += (tokens / 1000.0) * 0.002
                
        duration = time.time() - start_time
        runs = len(results)
        
        if runs == 0:
            return BenchmarkResult(
                agent_name=agent.name, runs=0, rca_accuracy_avg=0.0, recovery_success_rate=0.0,
                mttr_avg=0.0, mttr_p50=0.0, mttr_p95=0.0, actions_avg=0.0, unnecessary_actions_avg=0.0,
                abstention_rate=0.0, safety_score_avg=0.0,
                token_usage_total=0, cost_estimate_usd=0.0, duration_seconds=duration
            )
            
        rca_acc = sum(r.rca_accuracy for r in results) / runs
        rec_succ = sum(1.0 for r in results if r.recovery_successful) / runs
        
        mttrs = [r.mttr_seconds for r in results if r.recovery_successful]
        if not mttrs:
            mttrs = [0.0]
        mttr = sum(mttrs) / len(mttrs)
        mttr_p50 = float(np.percentile(mttrs, 50))
        mttr_p95 = float(np.percentile(mttrs, 95))
        
        actions = sum(r.total_actions for r in results) / runs
        unnecessary = sum(r.unnecessary_actions for r in results) / runs
        
        # Abstention: actions == 0
        abstentions = sum(1.0 for r in results if r.total_actions == 0) / runs
        
        safety = sum(r.safety_score for r in results) / runs
        
        return BenchmarkResult(
            agent_name=agent.name,
            runs=runs,
            rca_accuracy_avg=round(rca_acc, 2),
            recovery_success_rate=round(rec_succ, 2),
            mttr_avg=round(mttr, 1),
            mttr_p50=round(mttr_p50, 1),
            mttr_p95=round(mttr_p95, 1),
            actions_avg=round(actions, 1),
            unnecessary_actions_avg=round(unnecessary, 1),
            abstention_rate=round(abstentions, 2),
            safety_score_avg=round(safety, 2),
            token_usage_total=token_usage_total,
            cost_estimate_usd=round(cost_total, 4),
            duration_seconds=round(duration, 2)
        )
        
    def generate_report(self, benchmarks: list[BenchmarkResult]) -> str:
        report = f"{'Agent':<20} {'RCA':<7} {'Recov':<7} {'MTTR':<7} {'p95':<7} {'Acts':<5} {'Abst':<6} {'Safety':<8}\n"
        report += "-" * 75 + "\n"
        for b in benchmarks:
            rca_pct = f"{int(b.rca_accuracy_avg * 100)}%"
            rec_pct = f"{int(b.recovery_success_rate * 100)}%"
            safety_pct = f"{int(b.safety_score_avg * 100)}%"
            mttr_str = f"{b.mttr_avg}s"
            p95_str = f"{b.mttr_p95}s"
            abst_pct = f"{int(b.abstention_rate * 100)}%"
            report += f"{b.agent_name:<20} {rca_pct:<7} {rec_pct:<7} {mttr_str:<7} {p95_str:<7} {b.actions_avg:<5} {abst_pct:<6} {safety_pct:<8}\n"
        return report
