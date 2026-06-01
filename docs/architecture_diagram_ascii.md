# Architecture Diagram

## Query Flow

```text
User
  -> Amazon API Gateway
  -> AWS Lambda query guardrail
  -> Amazon OpenSearch Service retrieval
  -> Prompt assembly with citation-ready context
  -> Amazon Bedrock generation
  -> Citation validator Lambda
  -> Amazon Bedrock Guardrails + custom answer guardrails
  -> Response
```

## Ingestion Flow

```text
S3 documents
  -> Amazon Textract / AWS Lambda
  -> Text preprocessing
  -> Chunking workflow
  -> Amazon Bedrock embeddings
  -> Amazon OpenSearch Service vector index
```

## Monitoring Flow

```text
Application logs and metrics
  -> Amazon CloudWatch
  -> Alarms and dashboards
  -> S3 report artifacts
  -> QuickSight / OpenSearch dashboard sources
```
