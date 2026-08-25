import os
from typing import List

class EmbeddingProvider:
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

class MockEmbeddingProvider(EmbeddingProvider):
    def embed(self, text: str) -> List[float]:
        text = text.lower()
        val = sum(ord(c) for c in text)
        words = len(text.split())
        return [float(val % 100) / 100.0, float(words % 50) / 50.0, float((val * words) % 100) / 100.0]

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
