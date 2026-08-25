import os
from typing import List

class EmbeddingProvider:
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

import re
import math
from collections import defaultdict

class HashingEmbeddingProvider(EmbeddingProvider):
    """
    Dependency-free embedding provider using the hashing trick (Feature Hashing).
    Maps text into a fixed-dimensional vector space, preserving semantic overlap.
    """
    def __init__(self, dimensions: int = 256):
        self.dimensions = dimensions

    def embed(self, text: str) -> List[float]:
        # Tokenize and normalize
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Calculate term frequencies in hashed buckets
        vector = [0.0] * self.dimensions
        for word in words:
            # Use a stable hash modulo dimensions
            idx = hash(word) % self.dimensions
            vector[idx] += 1.0
            
        # L2 Normalize the vector so cosine similarity works out of the box
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
            
        return vector

class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIEmbeddingProvider")
        import openai
        self.client = openai.OpenAI(api_key=self.api_key)
        
    def embed(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
