"""Collect dashboard-ready metrics from local pipeline artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from enterprise_rag_platform.ingestion.ingestion_runner import resolve_project_path


def _read_json(path: Path, default: object) -> object:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 4)


def collect_dashboard_metrics(
    config: dict[str, object],
    pipeline_health: dict[str, object],
) -> dict[str, object]:
    """Collect local monitoring metrics for dashboard/reporting artifacts."""
    retrieval_context = _read_json(
        resolve_project_path(str(config["retrieval_context_output_path"])),
        {},
    )
    generated_answer = _read_json(
        resolve_project_path(str(config["generated_answer_output_path"])),
        {},
    )
    evaluation = _read_json(
        resolve_project_path(str(config["evaluation_results_json_path"])),
        {},
    )
    guardrails = _read_json(
        resolve_project_path(str(config["guardrail_results_output_path"])),
        {},
    )

    contexts = list(retrieval_context.get("contexts", []))
    similarity_scores = [float(context["similarity_score"]) for context in contexts]
    answer = dict(generated_answer.get("answer", {}))
    citation_validation = dict(generated_answer.get("citation_validation", {}))
    evaluation_results = list(evaluation.get("results", []))
    query_guardrail = dict(guardrails.get("query_guardrail", {}))
    answer_guardrail = dict(guardrails.get("answer_guardrail", {}) or {})

    citation_valid_values = [
        1.0 if bool(result["citation_valid"]) else 0.0
        for result in evaluation_results
    ]
    insufficient_values = [
        1.0 if bool(result["insufficient_evidence_handled"]) else 0.0
        for result in evaluation_results
        if result["evaluation_category"] == "insufficient_evidence"
    ]

    triggered_rules = list(query_guardrail.get("triggered_rules", [])) + list(
        answer_guardrail.get("triggered_rules", [])
    )

    return {
        "retrieval_result_count": len(contexts),
        "average_similarity_score": _average(similarity_scores),
        "max_similarity_score": round(max(similarity_scores), 4)
        if similarity_scores
        else 0.0,
        "min_similarity_score": round(min(similarity_scores), 4)
        if similarity_scores
        else 0.0,
        "generated_answer_available": bool(answer.get("answer_text")),
        "used_citation_count": len(answer.get("used_citations", [])),
        "generation_mode": answer.get("generation_mode", "unknown"),
        "citation_validation_passed": bool(citation_validation.get("is_valid", False)),
        "evaluation_question_count": len(evaluation_results),
        "average_overall_score": float(
            evaluation.get("evaluation_metadata", {}).get("average_overall_score", 0.0)
        ),
        "average_keyword_coverage_score": _average(
            [float(result["keyword_coverage_score"]) for result in evaluation_results]
        ),
        "average_groundedness_score": _average(
            [float(result["groundedness_score"]) for result in evaluation_results]
        ),
        "average_answer_completeness_score": _average(
            [float(result["answer_completeness_score"]) for result in evaluation_results]
        ),
        "citation_valid_rate": _average(citation_valid_values),
        "insufficient_evidence_handled_rate": _average(insufficient_values),
        "query_allowed": bool(query_guardrail.get("is_allowed", False)),
        "query_risk_level": query_guardrail.get("risk_level", "unknown"),
        "answer_allowed": bool(answer_guardrail.get("is_allowed", False)),
        "answer_risk_level": answer_guardrail.get("risk_level", "unknown"),
        "triggered_rule_count": len(triggered_rules),
        "missing_artifact_count": len(pipeline_health["missing_artifacts"]),
        "pipeline_health_status": pipeline_health["pipeline_health_status"],
    }
