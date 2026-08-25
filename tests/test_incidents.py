import pytest
from datetime import datetime
from environment.incidents.models import Incident, IncidentClass, IncidentSeverity
from environment.incidents.generator import IncidentGenerator

def test_incident_model_creation():
    incident = Incident(
        incident_id="INC-123",
        timestamp=datetime.now(),
        incident_class=IncidentClass.INFRASTRUCTURE,
        severity=IncidentSeverity.HIGH,
        services_affected=["nginx"],
        symptoms=["CPU 100%"],
        root_cause="Crypto miner",
        expected_impact="High latency",
        available_remediations=["kill_process"]
    )
    assert incident.incident_id == "INC-123"
    assert incident.severity == IncidentSeverity.HIGH
    assert incident.difficulty == 1 # default

def test_generator_default():
    generator = IncidentGenerator()
    incident = generator.generate_incident()
    assert isinstance(incident, Incident)
    assert incident.incident_id.startswith("INC-")

def test_generator_specific_category():
    generator = IncidentGenerator()
    incident = generator.generate_incident(category="database", difficulty=4)
    assert incident.incident_class == IncidentClass.DATABASE
    assert incident.difficulty == 4
    assert incident.severity == IncidentSeverity.CRITICAL

def test_generator_all_categories():
    generator = IncidentGenerator()
    categories = ["infrastructure", "network", "application", "database", "security", "multi_failure", "cascading"]
    for cat in categories:
        incident = generator.generate_incident(category=cat)
        assert isinstance(incident, Incident)
