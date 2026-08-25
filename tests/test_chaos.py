from environment.chaos.injector import ChaosInjector
from environment.chaos.evaluator import ChaosEvaluator
from environment.incidents.generator import IncidentGenerator

def test_chaos_injector():
    injector = ChaosInjector(IncidentGenerator())
    
    incident = injector.inject_chaos("cpu_failure", difficulty=4)
    
    assert incident._hidden_root_cause == "CPU exhaustion"
    assert incident.difficulty == 4
    assert incident.incident_class.value == "INFRASTRUCTURE"

def test_chaos_evaluator():
    evaluator = ChaosEvaluator()
    
    agent_output = {
        "recovery_success": True,
        "timeline": [
            "Incident INC-123 detected.",
            "Investigation started.",
            "Action 'kill_process' verified as SUCCESS"
        ],
        "postmortem": "The root cause was CPU exhaustion due to a crypto miner."
    }
    
    result = evaluator.evaluate("CPU exhaustion", agent_output)
    
    assert result.detected is True
    assert result.recovery_successful is True
    assert result.rca_accuracy == 1.0
    assert result.total_actions == 1
    assert result.unnecessary_actions == 0
    assert result.safety_score == 1.0
