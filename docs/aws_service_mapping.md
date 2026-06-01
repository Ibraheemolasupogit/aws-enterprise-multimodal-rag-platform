# AWS Service Mapping

This table maps the current local-first RAG platform to a future AWS production architecture. It is a blueprint only. No AWS deployment is performed in this repository yet.

| Local component | Current local artifact | Target AWS service | AWS responsibility | Security consideration | Future implementation note |
| --- | --- | --- | --- | --- | --- |
| Storage | `documents/raw/`, `documents/processed/` | Amazon S3 | Store raw and processed documents | Bucket encryption, block public access, IAM least privilege | Split raw, processed, reports, and evaluation buckets |
| Ingestion | `document_loader.py` | Amazon S3, AWS Lambda, AWS Step Functions | Trigger ingestion when documents arrive | Limit Lambda role to required S3 prefixes | Use S3 events or EventBridge to start workflow |
| Preprocessing | `text_preprocessor.py` | AWS Lambda, AWS Glue, AWS Step Functions | Normalize and clean extracted text | Log redaction, encrypted intermediate outputs | Start with Lambda, move large batch jobs to Glue |
| Chunking | `document_chunker.py` | AWS Lambda, Amazon SageMaker Processing, AWS Glue | Create chunk records for indexing | Validate input size and content type | Use SageMaker Processing for heavier document batches |
| Embeddings | `embedding_model.py` | Amazon Bedrock Titan Embeddings or equivalent Bedrock embedding model | Generate semantic embeddings | IAM-scoped Bedrock model access | Replace deterministic mock embeddings with Bedrock embeddings |
| Vector retrieval | `vector_store.py`, `chunk_embeddings.json` | Amazon OpenSearch Service, Bedrock Knowledge Bases | Store and search vectors | Fine-grained access control, VPC access, encryption | Use OpenSearch for custom retrieval or Knowledge Bases for managed RAG |
| RAG generation | `prompt_builder.py`, `mock_generator.py` | Amazon Bedrock | Build prompt and invoke model | Bedrock IAM access, prompt logging controls | Replace mock generation with model invocation |
| Citations | `citation_validator.py` | AWS Lambda | Validate source labels and citation metadata | Audit invalid citation events | Keep custom validation after Bedrock response |
| Guardrails | `query_guardrail.py`, `answer_guardrail.py` | Amazon Bedrock Guardrails, AWS Lambda | Enforce safety policies and custom checks | Central policy ownership and audit logs | Combine managed guardrails with deterministic business rules |
| Evaluation | `evaluation_runner.py` | AWS Step Functions, AWS Lambda, Amazon Bedrock model evaluation | Run scheduled quality checks | Store evaluation data separately from production logs | Add offline regression tests and future Bedrock model evaluation |
| Monitoring | `monitoring_runner.py` | Amazon CloudWatch | Metrics, logs, alarms, dashboards | Log retention and sensitive-data filtering | Emit quality and guardrail metrics to CloudWatch |
| Reporting | `report_builder.py`, `reports/sample/` | Amazon S3, Amazon QuickSight | Store report artifacts and dashboard sources | Bucket policies and access logging | Use S3 reports as QuickSight or OpenSearch dashboard inputs |
| API layer | CLI runners | Amazon API Gateway, AWS Lambda, Amazon Cognito | Expose query endpoint | Authentication, authorization, throttling | Add private API or Cognito-backed public API |
| Orchestration | Local runners | AWS Step Functions, EventBridge | Coordinate ingestion, evaluation, and reporting | Workflow roles scoped by task | Separate ingestion workflows from query-serving path |
| Security | Config placeholders | AWS IAM, AWS KMS, AWS Secrets Manager | Access control, encryption, secrets | No hardcoded credentials | Create dev/test/prod roles and KMS keys |
