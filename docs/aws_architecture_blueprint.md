# AWS Architecture Blueprint

This document translates the local-first enterprise multimodal RAG platform into a future AWS production architecture. It is a deployment blueprint only: no AWS resources are created, no credentials are required, and no Amazon Bedrock calls are made.

## Target Production Architecture

| Local asset or module | Production AWS mapping |
| --- | --- |
| `documents/raw/` | Amazon S3 raw document bucket |
| `documents/processed/` | Amazon S3 processed document bucket |
| `document_loader.py` | S3 object ingestion with AWS Lambda and AWS Step Functions |
| `text_preprocessor.py` | AWS Lambda, AWS Glue, or Step Functions task |
| `document_chunker.py` | AWS Lambda, Amazon SageMaker Processing, or AWS Glue |
| `embedding_model.py` | Amazon Bedrock Titan Embeddings or equivalent Bedrock embedding model |
| `chunk_embeddings.json` | Amazon OpenSearch Service vector index or Amazon Bedrock Knowledge Base |
| `vector_store.py` | Amazon OpenSearch Service vector search |
| `retrieval_orchestrator.py` | AWS Lambda, Amazon ECS, or API backend |
| `prompt_builder.py` | Bedrock prompt orchestration layer |
| `mock_generator.py` | Amazon Bedrock model invocation |
| `citation_validator.py` | Custom validation AWS Lambda |
| `query_guardrail.py`, `answer_guardrail.py` | Amazon Bedrock Guardrails plus custom policy checks |
| `evaluation_runner.py` | Scheduled evaluation workflow with AWS Step Functions |
| `monitoring_runner.py` | Amazon CloudWatch metrics, logs, dashboards, and alarms |
| `reports/sample/` | Amazon S3 reporting bucket and Amazon QuickSight dashboard source |

## Architecture Flow

1. Documents are uploaded to an Amazon S3 raw document bucket.
2. Amazon EventBridge or S3 event notifications trigger ingestion.
3. AWS Lambda or AWS Step Functions coordinates preprocessing.
4. Amazon Textract extracts text from PDFs, images, forms, and scanned documents.
5. Cleaned documents are chunked and embedded using Amazon Bedrock embeddings.
6. Vectors and chunk metadata are stored in Amazon OpenSearch Service or Bedrock Knowledge Bases.
7. Amazon API Gateway receives a user query.
8. AWS Lambda validates the query and applies query-level guardrails.
9. Retrieval searches OpenSearch for top-k citation-ready chunks.
10. A prompt is assembled with query, context, and citation metadata.
11. Amazon Bedrock generates a grounded answer.
12. A custom citation validator checks whether citations map to retrieved context.
13. Amazon Bedrock Guardrails and custom answer checks validate the final answer.
14. Logs, metrics, latency, guardrail events, and errors are sent to Amazon CloudWatch.
15. Scheduled evaluation jobs monitor quality over time.
16. Reports and metric exports feed S3-backed dashboard artifacts and future QuickSight or OpenSearch dashboards.

## Security and Governance

- IAM least privilege: each Lambda, Step Functions state machine, and service integration receives only the actions and resource ARNs it needs.
- S3 encryption: raw, processed, report, and evaluation buckets use server-side encryption with AWS KMS where appropriate.
- OpenSearch access control: vector indexes should use fine-grained access control, VPC access, encryption at rest, and encryption in transit.
- Bedrock Guardrails: managed safety policies can enforce topic restrictions, refusal behavior, and sensitive-data handling.
- Secrets Manager: API keys, connection strings, and third-party integration secrets must live in AWS Secrets Manager, never in code or config files.
- CloudWatch logging: query, retrieval, generation, evaluation, and guardrail events should be logged with sensitive-data redaction.
- Data retention: S3 lifecycle policies and CloudWatch log retention should match enterprise governance requirements.
- Auditability: retain trace IDs, query IDs, citation IDs, model IDs, evaluation run IDs, and guardrail decisions.
- PII and sensitive data: use Textract output classification, custom policy checks, and future Bedrock Guardrails sensitive-information filters.
- No hardcoded credentials: use IAM roles, environment variables for non-secret config, and Secrets Manager for secrets.
- Environment separation: maintain separate dev, test, and prod accounts or isolated stacks with separate buckets, indexes, roles, and KMS keys.

## Scalability and Reliability

- Async ingestion: Step Functions should orchestrate parsing, chunking, embeddings, indexing, retries, and dead-letter handling.
- Query serving decoupling: ingestion workflows should not block low-latency query APIs.
- Retry and failure handling: use Step Functions retry policies, Lambda destinations, and dead-letter queues where useful.
- Batch document processing: large corpora can use AWS Glue or SageMaker Processing for scalable preprocessing.
- OpenSearch scaling: size shards, replicas, and instance families for vector index volume and query latency.
- Lambda concurrency: set reserved concurrency and throttling controls for query, ingestion, and evaluation functions.
- Monitoring and alerting: CloudWatch alarms should track error rate, latency, guardrail blocks, evaluation regressions, and indexing failures.
- Cost controls: batch embeddings, cache results, tune chunk size and top-k, cap logs, and use development throttles.

## Future Multimodal Extension

- Amazon Textract can extract text and structure from scanned PDFs, forms, and images.
- Image metadata extraction can capture layout, captions, tables, and document-level visual context.
- Multimodal query handling can route text, image, or document questions to the correct extraction and retrieval path.
- Future Amazon Bedrock multimodal models can support image-aware or document-aware answer generation.
- Product-style recommendations can use metadata, usage events, and feedback signals.
- Knowledge graph extensions can connect entities, policies, systems, documents, and citations for richer enterprise reasoning.
