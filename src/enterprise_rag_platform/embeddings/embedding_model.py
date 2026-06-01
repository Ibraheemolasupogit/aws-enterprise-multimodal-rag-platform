"""Deterministic local embedding model placeholder."""

from __future__ import annotations

import hashlib
import math


class MockEmbeddingModel:
    """Create stable mock embeddings without external model calls."""

    def __init__(self, dimension: int = 32) -> None:
        if dimension <= 0:
            raise ValueError("Embedding dimension must be greater than zero")
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        """Return a deterministic embedding for non-empty input text."""
        normalized_text = " ".join(text.split())
        if not normalized_text:
            raise ValueError("Text must not be empty")

        values = []
        seed = normalized_text.encode("utf-8")
        counter = 0

        while len(values) < self.dimension:
            digest = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
            for byte in digest:
                values.append((byte / 127.5) - 1.0)
                if len(values) == self.dimension:
                    break
            counter += 1

        magnitude = math.sqrt(sum(value * value for value in values))
        if magnitude == 0:
            return [0.0 for _ in values]

        return [round(value / magnitude, 8) for value in values]
