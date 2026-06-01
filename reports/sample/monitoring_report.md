# Monitoring Report

Generated at: 2026-06-01 12:02:42 UTC

## Project Summary

This report summarizes the local AWS Enterprise Multimodal RAG Platform pipeline artifacts. It covers ingestion, embeddings, retrieval, mock generation, deterministic evaluation, and local guardrails.

## Pipeline Health

Status: **healthy**

- Documents: 1
- Chunks: 1
- Embeddings: 1
- Evaluation questions: 6
- Guardrail allowed: True
- Guardrail risk level: low

## Key Metrics

| Metric | Value |
| --- | --- |
| `pipeline_health_status` | healthy |
| `retrieval_result_count` | 1 |
| `average_similarity_score` | 0.2225 |
| `generation_mode` | mock_local_generation |
| `citation_validation_passed` | True |
| `evaluation_question_count` | 6 |
| `average_overall_score` | 0.8729 |
| `citation_valid_rate` | 1.0 |
| `query_allowed` | True |
| `answer_allowed` | True |
| `triggered_rule_count` | 0 |

## Retrieval Summary

- Result count: 1
- Average similarity score: 0.2225
- Max similarity score: 0.2225
- Min similarity score: 0.2225

## Generation Summary

- Generated answer available: True
- Generation mode: mock_local_generation
- Used citation count: 1
- Citation validation passed: True

## Evaluation Summary

- Question count: 6
- Average overall score: 0.8729
- Average keyword coverage: 0.8333
- Average groundedness: 0.8125
- Average completeness: 0.9167
- Citation valid rate: 1.0
- Insufficient-evidence handled rate: 1.0

## Guardrail Summary

- Query allowed: True
- Query risk level: low
- Answer allowed: True
- Answer risk level: low
- Triggered rule count: 0

## Missing Artifacts

- None

## Interpretation

The local pipeline is `healthy` based on artifact availability, evaluation score, and latest guardrail outcome. These metrics are intended for portfolio evidence and development-time observability, not production monitoring.

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
