"""Lightweight local vector-store-style retrieval."""

from __future__ import annotations

import json
import math
from pathlib import Path

from enterprise_rag_platform.embeddings.embedding_model import MockEmbeddingModel


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Calculate cosine similarity for two same-length vectors."""
    if len(left) != len(right):
        raise ValueError("Vectors must have the same dimension")
    if not left:
        raise ValueError("Vectors must not be empty")

    dot_product = sum(left_value * right_value for left_value, right_value in zip(left, right))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot_product / (left_norm * right_norm)


class LocalVectorStore:
    """In-memory vector store loaded from local JSON records."""

    def __init__(self, records: list[dict[str, object]], embedding_dimension: int) -> None:
        self.records = records
        self.embedding_model = MockEmbeddingModel(dimension=embedding_dimension)

    @classmethod
    def from_json(
        cls,
        vector_records_path: str | Path,
        embedding_dimension: int,
    ) -> "LocalVectorStore":
        """Load vector records from a local JSON artifact."""
        path = Path(vector_records_path)
        records = json.loads(path.read_text(encoding="utf-8"))
        return cls(records=records, embedding_dimension=embedding_dimension)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, object]]:
        """Return ranked vector search results for a query."""
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero")

        query_embedding = self.embedding_model.embed(query)
        scored_results = []

        for record in self.records:
            similarity_score = cosine_similarity(query_embedding, record["embedding"])
            scored_results.append(
                {
                    "document_id": record["document_id"],
                    "chunk_id": record["chunk_id"],
                    "source_file": record["source_file"],
                    "text": record["text"],
                    "similarity_score": round(similarity_score, 8),
                }
            )

        scored_results.sort(key=lambda result: result["similarity_score"], reverse=True)

        return [
            {"rank": rank, **result}
            for rank, result in enumerate(scored_results[:top_k], start=1)
        ]
