# AWS Cost and Monitoring Model

This document outlines likely cost drivers and monitoring signals for a future AWS deployment. It does not estimate real costs because no AWS workload is deployed yet.

## Likely Cost Drivers

- Amazon Bedrock model calls for generation
- Amazon Bedrock embedding generation
- Amazon OpenSearch Service clusters or serverless collections
- Amazon S3 storage and request volume
- AWS Lambda invocations and duration
- Amazon Textract document extraction
- Amazon CloudWatch logs, metrics, dashboards, and alarms

## Cost-Control Strategies

- Cache embeddings for unchanged chunks
- Batch embedding generation during ingestion
- Tune chunk size to reduce unnecessary token and vector volume
- Tune top-k to balance quality and retrieval/generation cost
- Set CloudWatch log retention limits
- Use development throttles and lower quotas in non-production environments
- Separate ingestion from query serving to avoid repeated processing
- Track token estimates and model invocation metadata

## Monitoring Metrics

- Retrieval latency
- Generation latency
- Evaluation score
- Citation validity rate
- Guardrail block rate
- Token and cost estimates
- Error rate
- Missing artifact count
- Ingestion failures
- OpenSearch query errors
- Bedrock invocation failures
- Lambda throttles and timeouts

## Dashboard Direction

CloudWatch dashboards can track service health, error rates, latency, and guardrail activity. OpenSearch dashboards can track retrieval quality trends, vector index behavior, and operational search metrics. S3 can store historical evaluation and monitoring reports for audit and portfolio reporting.
