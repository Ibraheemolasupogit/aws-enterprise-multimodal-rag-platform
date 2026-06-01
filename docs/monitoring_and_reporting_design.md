# Monitoring and Reporting Design

Monitoring matters for enterprise RAG because teams need visibility into pipeline completeness, retrieval behavior, answer generation, evaluation quality, and guardrail outcomes before production deployment. This milestone keeps monitoring local and artifact-based.

## Local Artifacts Monitored

The monitor inspects processed documents, chunks, embeddings, retrieval context, generated answers, evaluation JSON/CSV, and guardrail results. These files represent the current local pipeline state.

## Pipeline Health Statuses

- `healthy`: required artifacts exist, evaluation score meets the configured target, and the latest guardrail result is allowed
- `degraded`: artifacts exist, but quality or guardrail signals indicate risk
- `incomplete`: one or more required artifacts are missing

## Retrieval Metrics

Retrieval metrics include result count, average similarity score, maximum similarity score, and minimum similarity score from the latest retrieval context artifact.

## Generation Metrics

Generation metrics include answer availability, generation mode, citation count, and whether citation validation passed.

## Evaluation Metrics

Evaluation metrics include question count, average overall score, keyword coverage, groundedness, answer completeness, citation validity rate, and insufficient-evidence handling rate.

## Guardrail Metrics

Guardrail metrics include query allowed status, query risk level, answer allowed status, answer risk level, and triggered rule count.

## Dashboard-Ready Outputs

The monitoring runner writes `pipeline_health.json`, `dashboard_metrics.json`, `dashboard_metrics.csv`, and an executive Markdown report. These artifacts are designed for screenshots, README evidence, and future dashboard prototypes.

## Future AWS Mapping

Amazon CloudWatch can later collect runtime metrics, logs, alarms, and guardrail events. Amazon Bedrock model invocation logs can support latency, usage, and safety analysis. Amazon OpenSearch dashboards can visualize retrieval quality and operational trends.

## Limitations

- Monitoring reads local files only
- Metrics are snapshots, not time-series data
- No CloudWatch, Bedrock logs, OpenSearch dashboards, or managed observability services are connected
- Mock retrieval and mock generation metrics are development signals, not production KPIs
