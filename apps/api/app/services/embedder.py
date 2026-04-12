from __future__ import annotations

from dataclasses import dataclass
import random
import time

import httpx
import numpy as np

from app.services.local_embeddings import embed_texts


RETRIABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
LOCAL_EMBEDDING_DIMENSION = 1536


@dataclass
class Embedder:
    endpoint: str
    api_key: str
    embedding_model: str
    timeout_seconds: float = 45.0
    max_retries: int = 5
    base_backoff_seconds: float = 1.0

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _retry_delay(self, attempt: int) -> float:
        jitter = random.uniform(0, 0.25)
        return self.base_backoff_seconds * (2**attempt) + jitter

    @staticmethod
    def _extract_embeddings(body: dict) -> list[list[float]]:
        if "data" in body and isinstance(body["data"], list):
            return [item["embedding"] for item in body["data"] if "embedding" in item]
        if "embeddings" in body and isinstance(body["embeddings"], list):
            return body["embeddings"]
        raise ValueError(f"Unexpected embeddings response format: keys={list(body.keys())}")

    @staticmethod
    def _l2_normalize(vector: np.ndarray) -> np.ndarray:
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        # Run in offline mode when no API key is configured.
        if not self.api_key.strip():
            return embed_texts(texts, dimension=LOCAL_EMBEDDING_DIMENSION)

        payload = {
            "model": self.embedding_model,
            "input": texts,
        }

        last_error: RuntimeError | None = None

        # Retry transient HTTP and network failures with exponential backoff.
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_seconds) as client:
                    response = client.post(self.endpoint, headers=self._headers(), json=payload)
                response.raise_for_status()
                vectors = self._extract_embeddings(response.json())
                array = np.asarray(vectors, dtype=np.float32)
                if array.ndim != 2:
                    raise ValueError(f"Expected 2D embeddings output; got shape={array.shape}")
                return array
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                should_retry = status in RETRIABLE_STATUS_CODES and attempt < self.max_retries
                if not should_retry:
                    last_error = RuntimeError(f"Embedding API returned non-retriable status {status}")
                    break
                time.sleep(self._retry_delay(attempt))
            except httpx.RequestError as exc:
                if attempt >= self.max_retries:
                    last_error = RuntimeError(f"Embedding request failed after retries: {exc}")
                    break
                time.sleep(self._retry_delay(attempt))

        # Keep search functional even when the remote provider is unavailable.
        if self.api_key.strip():
            return embed_texts(texts, dimension=LOCAL_EMBEDDING_DIMENSION)

        if last_error is not None:
            raise last_error
        raise RuntimeError("Embedding request failed after all retries")

    def embed(self, text: str) -> np.ndarray:
        batch = self.embed_batch([text])
        if len(batch) != 1:
            raise RuntimeError("Expected exactly one embedding vector for single query")
        # Query vectors must be normalized to match cosine-style FAISS indexing.
        return self._l2_normalize(batch[0].astype(np.float32))
