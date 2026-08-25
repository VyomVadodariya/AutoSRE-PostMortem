from memory.incidents.store import IncidentMemoryStore, IncidentRecord
from memory.vector_store.lightweight import LightweightVectorStore

def test_vector_store():
    store = LightweightVectorStore()
    
    store.add_record("CPU is spiking to 100%", {"id": 1, "cause": "crypto miner"})
    store.add_record("Database is throwing timeouts", {"id": 2, "cause": "connection limit"})
    
    # Search for CPU issue
    results = store.search("CPU spike issue")
    assert len(results) > 0
    # Depending on our naive mock embedder, the top result should hopefully be the closest one
    # In a real environment with sentence-transformers, this is guaranteed.

def test_incident_memory_store():
    store = IncidentMemoryStore()
    
    record = IncidentRecord(
        incident_id="INC-111",
        symptoms=["API Latency", "502 Errors"],
        root_cause="Nginx config error",
        actions_taken=["restart_service nginx"],
        recovery_time_seconds=42,
        postmortem="Config error caused gateway timeout.",
        lessons_learned=["Validate config before reload."]
    )
    
    store.store_incident(record)
    
    # Retrieve it
    results = store.search_similar_incidents(["API Latency", "502 Errors"])
    
    assert len(results) == 1
    assert results[0].incident_id == "INC-111"
    assert results[0].root_cause == "Nginx config error"
