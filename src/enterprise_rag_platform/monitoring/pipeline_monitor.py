"""Local artifact-based pipeline health monitoring."""

from __future__ import annotations

import json
from pathlib import Path

from enterprise_rag_platform.ingestion.ingestion_runner import resolve_project_path


ARTIFACT_CONFIG_KEYS = {
    "documents": "processed_output_dir",
    "document_chunks": "processed_output_dir",
    "chunk_embeddings": "embedding_output_path",
    "retrieval_context": "retrieval_context_output_path",
    "generated_answer": "generated_answer_output_path",
    "evaluation_results_json": "evaluation_results_json_path",
    "evaluation_results_csv": "evaluation_results_csv_path",
    "guardrail_results": "guardrail_results_output_path",
}


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_paths(config: dict[str, object]) -> dict[str, Path]:
    processed_output_dir = resolve_project_path(str(config["processed_output_dir"]))
    return {
        "documents": processed_output_dir / "documents.json",
        "document_chunks": processed_output_dir / "document_chunks.json",
        "chunk_embeddings": resolve_project_path(str(config["embedding_output_path"])),
        "retrieval_context": resolve_project_path(
            str(config["retrieval_context_output_path"])
        ),
        "generated_answer": resolve_project_path(str(config["generated_answer_output_path"])),
        "evaluation_results_json": resolve_project_path(
            str(config["evaluation_results_json_path"])
        ),
        "evaluation_results_csv": resolve_project_path(
            str(config["evaluation_results_csv_path"])
        ),
        "guardrail_results": resolve_project_path(str(config["guardrail_results_output_path"])),
    }


def inspect_pipeline_health(config: dict[str, object]) -> dict[str, object]:
    """Inspect local pipeline artifacts and return a health summary."""
    paths = _artifact_paths(config)
    missing_artifacts = [
        str(path)
        for path in paths.values()
        if not path.is_file()
    ]

    documents = _read_json(paths["documents"]) if paths["documents"].is_file() else []
    chunks = (
        _read_json(paths["document_chunks"])
        if paths["document_chunks"].is_file()
        else []
    )
    embeddings = (
        _read_json(paths["chunk_embeddings"])
        if paths["chunk_embeddings"].is_file()
        else []
    )
    evaluation = (
        _read_json(paths["evaluation_results_json"])
        if paths["evaluation_results_json"].is_file()
        else {}
    )
    guardrails = (
        _read_json(paths["guardrail_results"])
        if paths["guardrail_results"].is_file()
        else {}
    )

    evaluation_metadata = dict(evaluation.get("evaluation_metadata", {}))
    average_overall_score = float(evaluation_metadata.get("average_overall_score", 0.0))
    minimum_score = float(config.get("evaluation_minimum_overall_score", 0.0))
    guardrail_allowed = bool(guardrails.get("final_response", {}).get("is_allowed", False))
    guardrail_risk_level = str(
        guardrails.get("query_guardrail", {}).get("risk_level", "unknown")
    )

    if missing_artifacts:
        pipeline_health_status = "incomplete"
    elif average_overall_score < minimum_score or not guardrail_allowed:
        pipeline_health_status = "degraded"
    else:
        pipeline_health_status = "healthy"

    return {
        "documents_available": paths["documents"].is_file(),
        "chunks_available": paths["document_chunks"].is_file(),
        "embeddings_available": paths["chunk_embeddings"].is_file(),
        "retrieval_context_available": paths["retrieval_context"].is_file(),
        "generated_answer_available": paths["generated_answer"].is_file(),
        "evaluation_results_available": paths["evaluation_results_json"].is_file()
        and paths["evaluation_results_csv"].is_file(),
        "guardrail_results_available": paths["guardrail_results"].is_file(),
        "total_documents": len(documents) if isinstance(documents, list) else 0,
        "total_chunks": len(chunks) if isinstance(chunks, list) else 0,
        "total_embeddings": len(embeddings) if isinstance(embeddings, list) else 0,
        "evaluation_question_count": int(evaluation_metadata.get("question_count", 0)),
        "average_overall_score": average_overall_score,
        "guardrail_allowed": guardrail_allowed,
        "guardrail_risk_level": guardrail_risk_level,
        "missing_artifacts": missing_artifacts,
        "pipeline_health_status": pipeline_health_status,
    }
