"""Markdown reporting utilities for local monitoring artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


KEY_METRICS = [
    "pipeline_health_status",
    "retrieval_result_count",
    "average_similarity_score",
    "generation_mode",
    "citation_validation_passed",
    "evaluation_question_count",
    "average_overall_score",
    "citation_valid_rate",
    "query_allowed",
    "answer_allowed",
    "triggered_rule_count",
]


def build_monitoring_report(
    pipeline_health: dict[str, object],
    metrics: dict[str, object],
) -> str:
    """Build a portfolio-ready Markdown monitoring report."""
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    missing_artifacts = list(pipeline_health["missing_artifacts"])
    missing_text = "\n".join(f"- `{artifact}`" for artifact in missing_artifacts)
    if not missing_text:
        missing_text = "- None"

    key_metric_rows = "\n".join(
        f"| `{metric}` | {metrics.get(metric, pipeline_health.get(metric, 'n/a'))} |"
        for metric in KEY_METRICS
    )

    return f"""# Monitoring Report

Generated at: {generated_at}

## Project Summary

This report summarizes the local AWS Enterprise Multimodal RAG Platform pipeline artifacts. It covers ingestion, embeddings, retrieval, mock generation, deterministic evaluation, and local guardrails.

## Pipeline Health

Status: **{pipeline_health["pipeline_health_status"]}**

- Documents: {pipeline_health["total_documents"]}
- Chunks: {pipeline_health["total_chunks"]}
- Embeddings: {pipeline_health["total_embeddings"]}
- Evaluation questions: {pipeline_health["evaluation_question_count"]}
- Guardrail allowed: {pipeline_health["guardrail_allowed"]}
- Guardrail risk level: {pipeline_health["guardrail_risk_level"]}

## Key Metrics

| Metric | Value |
| --- | --- |
{key_metric_rows}

## Retrieval Summary

- Result count: {metrics["retrieval_result_count"]}
- Average similarity score: {metrics["average_similarity_score"]}
- Max similarity score: {metrics["max_similarity_score"]}
- Min similarity score: {metrics["min_similarity_score"]}

## Generation Summary

- Generated answer available: {metrics["generated_answer_available"]}
- Generation mode: {metrics["generation_mode"]}
- Used citation count: {metrics["used_citation_count"]}
- Citation validation passed: {metrics["citation_validation_passed"]}

## Evaluation Summary

- Question count: {metrics["evaluation_question_count"]}
- Average overall score: {metrics["average_overall_score"]}
- Average keyword coverage: {metrics["average_keyword_coverage_score"]}
- Average groundedness: {metrics["average_groundedness_score"]}
- Average completeness: {metrics["average_answer_completeness_score"]}
- Citation valid rate: {metrics["citation_valid_rate"]}
- Insufficient-evidence handled rate: {metrics["insufficient_evidence_handled_rate"]}

## Guardrail Summary

- Query allowed: {metrics["query_allowed"]}
- Query risk level: {metrics["query_risk_level"]}
- Answer allowed: {metrics["answer_allowed"]}
- Answer risk level: {metrics["answer_risk_level"]}
- Triggered rule count: {metrics["triggered_rule_count"]}

## Missing Artifacts

{missing_text}

## Interpretation

The local pipeline is `{pipeline_health["pipeline_health_status"]}` based on artifact availability, evaluation score, and latest guardrail outcome. These metrics are intended for portfolio evidence and development-time observability, not production monitoring.

## Limitations

- Metrics are derived from local JSON and CSV artifacts
- Mock embeddings and mock generation are not production-quality AI components
- Latency and quality scores are deterministic development signals
- No CloudWatch, OpenSearch dashboards, Bedrock invocation logs, or managed observability services are connected

## Future AWS Observability Mapping

- Amazon CloudWatch can collect logs, metrics, alarms, and guardrail events
- Amazon Bedrock invocation logs can support model usage, latency, and safety analysis
- Amazon OpenSearch dashboards can visualize retrieval quality, latency, and operational trends
- Amazon S3 can store historical evaluation and monitoring artifacts
"""


def write_monitoring_report(
    output_path: Path,
    pipeline_health: dict[str, object],
    metrics: dict[str, object],
) -> None:
    """Write the monitoring Markdown report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        build_monitoring_report(pipeline_health, metrics),
        encoding="utf-8",
    )
