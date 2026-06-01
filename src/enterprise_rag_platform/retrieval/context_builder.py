"""Build citation-ready retrieval context records."""

from __future__ import annotations


def build_citation_label(source_file: str, chunk_id: str) -> str:
    """Create a human-readable citation label."""
    return f"[{source_file} | {chunk_id}]"


def build_contexts(
    query: dict[str, object],
    retrieval_results: list[dict[str, object]],
) -> list[dict[str, object]]:
    """Convert ranked retrieval results into citation-ready contexts."""
    query_id = str(query["query_id"])
    contexts = []

    for result in retrieval_results:
        source_file = str(result["source_file"])
        chunk_id = str(result["chunk_id"])
        rank = int(result["rank"])
        similarity_score = float(result["similarity_score"])

        contexts.append(
            {
                "context_id": f"{query_id}_context_{rank:04d}",
                "query_id": query_id,
                "rank": rank,
                "document_id": result["document_id"],
                "chunk_id": chunk_id,
                "source_file": source_file,
                "chunk_index": result["chunk_index"],
                "text": result["text"],
                "similarity_score": similarity_score,
                "citation_label": build_citation_label(source_file, chunk_id),
                "citation_metadata": {
                    "document_id": result["document_id"],
                    "chunk_id": chunk_id,
                    "source_file": source_file,
                    "rank": rank,
                    "similarity_score": similarity_score,
                },
            }
        )

    return contexts
