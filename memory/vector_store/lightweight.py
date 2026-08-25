import math
from typing import List, Tuple, Dict, Any

class LightweightVectorStore:
    """
    A simple in-memory vector store that avoids heavy external dependencies.
    Uses a naive mock embedding for demonstration purposes, but provides
    the exact interface needed for the AI agent to search historical incidents.
    """
    def __init__(self):
        self.records: List[Tuple[List[float], Any]] = []

    def add_record(self, text_to_embed: str, payload: Any):
        vector = self._mock_embed(text_to_embed)
        self.records.append((vector, payload))

    def search(self, query: str, top_k: int = 3) -> List[Any]:
        if not self.records:
            return []
            
        q_vec = self._mock_embed(query)
        
        results = []
        for vec, payload in self.records:
            sim = self._cosine_similarity(q_vec, vec)
            results.append((sim, payload))
            
        # Sort by highest similarity
        results.sort(key=lambda x: x[0], reverse=True)
        
        return [r[1] for r in results[:top_k]]

    def _mock_embed(self, text: str) -> List[float]:
        # A simple simulated embedding just to provide vector functionality without an LLM dependency yet.
        # Uses word counts and basic character sums.
        text = text.lower()
        val = sum(ord(c) for c in text)
        words = len(text.split())
        return [float(val % 100) / 100.0, float(words % 50) / 50.0, float((val * words) % 100) / 100.0]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)
