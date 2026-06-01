"""Local retrieval orchestration for citation-ready context building."""

from __future__ import annotations

from pathlib import Path

from enterprise_rag_platform.ingestion.ingestion_runner import (
    DEFAULT_CONFIG_PATH,
    load_config,
    resolve_project_path,
)
from enterprise_rag_platform.retrieval.context_builder import build_contexts
from enterprise_rag_platform.retrieval.query_processor import process_query
from enterprise_rag_platform.retrieval.vector_store import LocalVectorStore


def filter_results_by_similarity(
    results: list[dict[str, object]],
    minimum_similarity_score: float,
) -> list[dict[str, object]]:
    """Keep retrieval results that meet the minimum similarity score."""
    return [
        result
        for result in results
        if float(result["similarity_score"]) >= minimum_similarity_score
    ]


def run_retrieval_orchestration(
    raw_query: str,
    config_path: str | Path = DEFAULT_CONFIG_PATH,
) -> dict[str, object]:
    """Process a query, retrieve chunks, and build citation-ready contexts."""
    config = load_config(config_path)
    embedding_output_path = resolve_project_path(str(config["embedding_output_path"]))
    embedding_dimension = int(config["embedding_dimension"])
    retrieval_top_k = int(config["retrieval_top_k"])
    minimum_query_words = int(config["minimum_query_words"])
    minimum_similarity_score = float(config["minimum_similarity_score"])

    query = process_query(raw_query, minimum_query_words=minimum_query_words)
    vector_store = LocalVectorStore.from_json(
        embedding_output_path,
        embedding_dimension=embedding_dimension,
    )
    retrieved_results = vector_store.search(
        str(query["normalized_query"]),
        top_k=retrieval_top_k,
    )
    filtered_results = filter_results_by_similarity(
        retrieved_results,
        minimum_similarity_score=minimum_similarity_score,
    )
    contexts = build_contexts(query, filtered_results)

    no_result_reason = None
    if not contexts:
        no_result_reason = (
            "No retrieved chunks met the minimum similarity score threshold."
        )

    return {
        "query": query,
        "retrieval_parameters": {
            "top_k": retrieval_top_k,
            "minimum_similarity_score": minimum_similarity_score,
            "embedding_dimension": embedding_dimension,
        },
        "contexts": contexts,
        "result_count": len(contexts),
        "no_result_reason": no_result_reason,
    }
