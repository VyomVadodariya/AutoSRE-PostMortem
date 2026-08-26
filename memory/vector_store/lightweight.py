import math
from typing import Any

from memory.vector_store.embedding import EmbeddingProvider, HashingEmbeddingProvider


class LightweightVectorStore:
    """
    A simple in-memory vector store.
    """
    def __init__(self, embedding_provider: EmbeddingProvider = None):
        self.records: list[tuple[list[float], Any]] = []
        self.embedding_provider = embedding_provider or HashingEmbeddingProvider()

    def add_record(self, text_to_embed: str, payload: Any):
        vector = self.embedding_provider.embed(text_to_embed)
        self.records.append((vector, payload))

    def search(self, query: str, top_k: int = 3) -> list[Any]:
        if not self.records:
            return []
            
        q_vec = self.embedding_provider.embed(query)
        
        results = []
        for vec, payload in self.records:
            sim = self._cosine_similarity(q_vec, vec)
            results.append((sim, payload))
            
        # Sort by highest similarity
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [r[1] for r in results[:top_k]]

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)
