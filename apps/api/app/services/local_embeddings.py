from __future__ import annotations

import hashlib
import re

import numpy as np


TOKEN_RE = re.compile(r"[a-z0-9_+#]+")


def _tokenize(text: str) -> list[str]:
    tokens = TOKEN_RE.findall(text.lower())
    return tokens or ["empty"]


def embed_text(text: str, dimension: int = 1536) -> np.ndarray:
    vector = np.zeros(dimension, dtype=np.float32)
    for token in _tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big", signed=False) % dimension
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign

    norm = np.linalg.norm(vector)
    if norm == 0:
        return vector
    return vector / norm


def embed_texts(texts: list[str], dimension: int = 1536) -> np.ndarray:
    if not texts:
        return np.empty((0, dimension), dtype=np.float32)
    return np.vstack([embed_text(text, dimension=dimension) for text in texts]).astype(np.float32)
