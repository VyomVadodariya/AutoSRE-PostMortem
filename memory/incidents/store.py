
from pydantic import BaseModel, Field

from memory.vector_store.lightweight import LightweightVectorStore


class IncidentRecord(BaseModel):
    incident_id: str
    symptoms: list[str]
    root_cause: str
    actions_taken: list[str]
    recovery_time_seconds: int
    postmortem: str
    lessons_learned: list[str] = Field(default_factory=list)

from memory.vector_store.embedding import EmbeddingProvider


class IncidentMemoryStore:
    def __init__(self, embedding_provider: EmbeddingProvider = None):
        self.records: dict[str, IncidentRecord] = {}
        self.vector_store = LightweightVectorStore(embedding_provider=embedding_provider)

    def store_incident(self, record: IncidentRecord):
        self.records[record.incident_id] = record
        
        # Build a semantic document to represent this incident
        searchable_text = f"Symptoms: {', '.join(record.symptoms)}. Root Cause: {record.root_cause}. Actions: {', '.join(record.actions_taken)}."
        
        self.vector_store.add_record(searchable_text, record)

    def search_similar_incidents(self, current_symptoms: list[str], top_k: int = 3) -> list[IncidentRecord]:
        query = f"Symptoms: {', '.join(current_symptoms)}."
        return self.vector_store.search(query, top_k=top_k)
