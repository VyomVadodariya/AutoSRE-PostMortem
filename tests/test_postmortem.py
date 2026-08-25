from agents.postmortem.agent import PostmortemAgent
from environment.incidents.models import Incident, IncidentClass, IncidentSeverity
from rca.engine import RCA_Result
from agents.remediation.engine import RemediationResult
from datetime import datetime, timezone
import time

def test_postmortem_generation():
    agent = PostmortemAgent()
    
    incident = Incident(
        incident_id="INC-999",
        timestamp=datetime.now(timezone.utc),
        incident_class=IncidentClass.SECURITY,
        severity=IncidentSeverity.CRITICAL,
        services_affected=["auth_service"],
        symptoms=["CPU 100%"],
        root_cause="Crypto miner",
        expected_impact="Service Outage",
        available_remediations=["kill_process"]
    )
    
    rca = RCA_Result(
        symptoms=["CPU 100%"],
        root_cause="Crypto miner",
        contributing_factors=["Missing CPU limit"],
        impact="Service Outage affecting auth_service",
        evidence=[],
        confidence=0.9
    )
    
    remediation_res = RemediationResult(
        action="kill_process",
        before_state={"cpu": 100},
        after_state={"cpu": 20},
        verification_status="SUCCESS",
        confidence=0.95
    )
    
    now = time.time()
    timestamps = {
        "start_time": now - 100,
        "detected_time": now - 90,
        "acknowledged_time": now - 87,
        "recovered_time": now
    }
    
    report = agent.generate(incident, rca, [remediation_res], timestamps)
    
    # Assert formatting structure
    assert "# INCIDENT POSTMORTEM: INC-999" in report
    assert "**Severity**: CRITICAL" in report
    assert "**MTTD**: 10s | **MTTA**: 3s | **MTTR**: 100s" in report
    assert "## Executive Summary" in report
    assert "Crypto miner" in report
    assert "Missing CPU limit" in report
    assert "Estimated Business Impact" in report
    assert "`kill_process`" in report
    assert "## Lessons Learned" in report
    assert "## Preventive Actions" in report
